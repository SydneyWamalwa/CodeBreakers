from flask import Flask, render_template, request, redirect, url_for, g, jsonify,send_from_directory,send_file,session
from io import BytesIO
# from PIL import Image
import sqlite3
import os
import time
import base64
import traceback
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from flask_session import Session
# from app import app, db, Purchase



secret_key = os.urandom(24)
app = Flask(__name__)
app.secret_key = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['DATABASE'] = 'popkulture.db'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER1'] = os.path.join(os.getcwd(), 'static', 'products')
app.config['PURCHASED_FOLDER'] = os.path.join(os.getcwd(), 'static', 'purchased')  # New folder for purchased screenshots
bcrypt = Bcrypt(app)
Session(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///popkulture.db'
db = SQLAlchemy(app)


# model for purchase table
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    items_purchased = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Purchase(email='{self.email}', reference='{self.reference}', total_amount='{self.total_amount}', items_purchased='{self.items_purchased}')"

@app.route('/store-shop-purchase', methods=['POST'])
def store_shop_purchase():
    try:
        # Extract data from the request
        data = request.json
        user_email = data.get('user_email')
        description = data.get('description')
        image = data.get('image')
        price = data.get('price')

        # Store purchase data in the database
        purchase = Purchase(user_email=user_email, description=description, image=image, price=price)
        db.session.add(purchase)
        db.session.commit()

        return jsonify({'message': 'Shop purchase data stored successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# generate a unique id for product table#
def generate_unique_id():
    timestamp = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    return str(timestamp)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                unique_id TEXT PRIMARY KEY NOT NULL,
                description TEXT NOT NULL,
                price VARCHAR NOT NULL,
                color VARCHAR NOT NULL,
                image BLOB NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_canvas_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchased_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                size TEXT NOT NULL,
                colorOption TEXT,
                imageUrl TEXT NOT NULL,
                screenshotUrl TEXT NOT NULL,
                price INTEGER NOT NULL,
                userEmail TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_purchased_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_email TEXT NOT NULL,
                description TEXT NOT NULL,
                image TEXT NOT NULL,
                price int NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.commit()

# Call the init_db function to ensure all tables are created before running the app
init_db()

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/create')
def create():
    if 'user_id' not in session:
        return redirect(url_for('login', next=request.url))
    return render_template('index.html')

#Auth routes
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('popkulture.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            # If the user exists, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Redirect to the original requested page or the home page
            return redirect('/SuccessLogin')

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('Login.html', error='Invalid credentials')

    return render_template('Login.html')

@app.route('/Login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('popkulture.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            # If the user exists, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Redirect to the original requested page or the home page
            return redirect('/SuccessLogin2')

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('Login2.html', error='Invalid credentials')

    return render_template('Login2.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from the session
    session.pop('user_name', None)  # Remove user_name from the session
    return redirect(url_for('home'))



@app.route('/Signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the user into the users table
            with sqlite3.connect('popkulture.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
                connection.commit()

            # Store the user's name in the session
            session['name'] = name
            session['email'] = email

            # Redirect to the index page with the user's name as a parameter
            return redirect('/Success')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('signup.html', error='Email already exists. Please use a different email.')

    return render_template('Signup.html')

@app.route('/Success')
def success():
    # Get the user's name from the session
    user_name = session.get('name')
    return render_template('Success.html', user_name=user_name)

@app.route('/SuccessLogin')
def successlogin():
    # Get the user's name from the session
    user_name = session.get('user_name')
    return render_template('Loginsuccess.html', user_name=user_name)

@app.route('/SuccessLogin2')
def successlogin2():
    # Get the user's name from the session
    user_name = session.get('user_name')
    return render_template('Loginsuccess2.html', user_name=user_name)

@app.route('/adminsignup', methods=['GET', 'POST'])
def adminsignup():
    if request.method == 'POST':
        # Process the form data here (save to database, perform validation, etc.)
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # Hash the password before storing it in the database
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            # Insert the user into the users table
            with sqlite3.connect('popkulture.db') as connection:
                cursor = connection.cursor()
                cursor.execute("INSERT INTO admins (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
                connection.commit()

            # Store the user's name in the session
            session['name'] = name
            session['email'] = email

            # Redirect to the index page with the user's name as a parameter
            return render_template('admin.html')

        except sqlite3.IntegrityError:
            # Handle the case where the email is not unique (already exists in the database)
            return render_template('signup.html', error='Email already exists. Please use a different email.')

    return render_template('Admin_signup.html')

@app.route('/LoginAdmin', methods=['GET', 'POST'])
def loginAdmin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        with sqlite3.connect('popkulture.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM admins WHERE email=?", (email,))
            user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user[3], password):
            # If the user exists and the password is correct, store user information in the session
            session['user_id'] = user[0]
            session['user_name'] = user[1]

            # Pass the admin_name to the template
            return render_template('admin.html', admin_name=user[1])

        else:
            # If login fails, you can display an error message or redirect to the login page
            return render_template('Login.html', error='Invalid credentials')

    return render_template('AdminLogin.html')


#design routes
@app.route('/save_canvas', methods=['POST'])
def save_canvas_content():
    if request.method == 'POST':
        canvas_content = request.json.get('canvas_content')
        img_data = base64.b64decode(canvas_content.split(',')[1])

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        filename = f'tshirt_{int(time.time())}.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, 'wb') as f:
            f.write(img_data)

        user_id = session.get('user_id')

        # Establish connection to the database
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO saved_canvas_content (user_id,content) VALUES (?,?)', (user_id,filename,))
        db.commit()

        return jsonify({'status': 'success', 'filename': filename})

@app.errorhandler(Exception)
def handle_error(e):
    traceback.print_exc()  # Print the exception traceback
    return jsonify({'error': str(e)}), 500

@app.route('/display/<filename>')
def display_image(filename):
     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#shop routes
@app.route('/shop')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login2', next=request.url))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    records = cursor.fetchall()
    return render_template('shop.html',records=records)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        description = request.form['description']
        price = request.form['price']
        color = request.form['color']
        image = request.files['image'].read()

        db = get_db()
        cursor = db.cursor()
        unique_id = generate_unique_id()
        cursor.execute('INSERT INTO products (unique_id, description, price, color, image) VALUES (?, ?, ?, ?, ?)',
                       (unique_id, description, price, color, image))
        db.commit()

        os.makedirs(app.config['UPLOAD_FOLDER1'], exist_ok=True)

        filename = f'tshirt_{int(time.time())}.png'
        filepath = os.path.join(app.config['UPLOAD_FOLDER1'], filename)

        with open(filepath, 'wb') as f:
            f.write(image)

        return redirect(url_for('products'))

    return render_template('admin.html')


@app.route('/product_image/<string:unique_id>')
def product_image(unique_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT image FROM products WHERE unique_id = ?", (unique_id,))
    image = cursor.fetchone()[0]
    return send_file(BytesIO(image), mimetype='image/jpeg')

# ...

def save_image_to_file(data, filepath):
    with open(filepath, 'wb') as f:
        f.write(data)

def read_image_from_file(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# ... (Other routes and configurations)


@app.route('/save_purchased_product', methods=['POST'])
def save_purchased_product():
    if request.method == 'POST':
        try:
            user_email = request.json.get('user_email')
            size = request.json.get('size')
            color_option = request.json.get('color_option')
            image_url = request.json.get('image_url')
            screenshot_url = request.json.get('screenshot_url')
            price = request.json.get('price')

            # Retrieve user_id from the session
            user_id = session.get('user_id')

            print(f"Received data: user_email={user_email},user_id{user_id} ,size={size}, color_option={color_option}, image_url={image_url}, screenshot_url={screenshot_url}, price={price}")

            # Your SQLite database connection and cursor creation
            db = sqlite3.connect('popkulture.db')
            cursor = db.cursor()

            # Save the screenshot image to the 'purchased' directory with .png extension
            screenshot_filename = f'screenshot_{int(time.time())}.png'
            screenshot_filepath = os.path.join(app.config['PURCHASED_FOLDER'], screenshot_filename)

            # Save the base64-encoded image data to file
            save_image_to_file(base64.b64decode(screenshot_url.split(',')[1]), screenshot_filepath)

            # Read the image from the 'purchased' folder, encode in base64, and save in the database
            screenshot_db_format = read_image_from_file(screenshot_filepath)

            # Insert the purchased product details into the database
            cursor.execute(
                'INSERT INTO purchased_products (user_id,userEmail, size, colorOption, imageUrl, screenshotUrl, price) VALUES (?, ?, ?, ?, ?, ?,?)',
                (user_id,user_email, size, color_option, image_url, f'{screenshot_filename}', price)  # Save the filename with .png extension
            )

            # Retrieve the last inserted product_id
            product_id = cursor.lastrowid

            db.commit()
            db.close()

            return jsonify({'status': 'success', 'product_id': product_id})
        except Exception as e:
            # Log the exception details
            print(f"Error saving purchased product details: {e}")
            traceback.print_exc()

            # Return an error response
            return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

# ... (Other code)

@app.route('/display2/<int:product_id>')
def display2(product_id):
    try:
        # Retrieve the product details from the database using product_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM purchased_products WHERE id = ?", (product_id,))
        product = cursor.fetchone()

        if product:
            # Assuming that 'screenshot_filename' is a column in the purchased_products table
            screenshot_filename = f'screenshot_{product_id}.png'
            screenshot_path = os.path.join(app.config['PURCHASED_FOLDER'], screenshot_filename)

            # Assuming that 'other_details' are other product details you want to display
            other_details = {
                'user_email': product[1],  # Use the correct index for 'userEmail'
                'size': product[2],  # Use the correct index for 'size'
                'color_option': product[3],  # Use the correct index for 'colorOption'
                'image_url': product[4],  # Use the correct index for 'imageUrl'
                'price': product[6],  # Use the correct index for 'price'
                'screenshot': product[5]
            }

            # Render the 'display2.html' template with the product details
            return render_template('display2.html', screenshot_path=screenshot_path, product_id=product_id, **other_details)
        else:
            return "Product not found", 404
    except Exception as e:
        print(f"Error fetching product details: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

@app.route('/get_saved_details')
def get_saved_details():
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch saved details from the database
        cursor.execute('SELECT * FROM purchased_products')
        columns = [column[0] for column in cursor.description]
        saved_details = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return jsonify({'status': 'success', 'savedDetails': saved_details})
    except Exception as e:
        print(f"Error fetching saved details: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

@app.route('/display_purchased_image/<int:product_id>')
def display_purchased_image(product_id):
    try:
        # Retrieve the product details from the database using product_id
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT screenshotUrl FROM purchased_products WHERE id = ?", (product_id,))
        screenshot_filename = cursor.fetchone()[0]

        if screenshot_filename:
            screenshot_path = os.path.join(app.config['PURCHASED_FOLDER'], screenshot_filename)
            return send_from_directory(app.config['PURCHASED_FOLDER'], screenshot_filename)
        else:
            return "Image not found", 404
    except Exception as e:
        print(f"Error fetching purchased image: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

# #shop payment routes
# @app.route('/shop_purchased_product', methods=['POST'])
# def shop_purchased_product():
#     if request.method == 'POST':
#         try:
#             # Retrieve product details from the request
#             user_email = request.json.get('user_email')
#             image_url = request.json.get('image')
#             price = request.json.get('price')
#             description=request.json.get('description')

#             # Insert the purchased product details into the database
#             db = get_db()
#             cursor = db.cursor()
#             cursor.execute(
#                 'INSERT INTO purchased_shop_products (userEmail, image, price,description) VALUES (?, ?, ?, ?)',
#                 (user_email, image_url, price,description)
#             )
#             db.commit()
#             db.close()

#             return jsonify({'status': 'success'})
#         except Exception as e:
#             print(f"Error saving purchased product details: {e}")
#             return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500


# Retrieve a specific user's saved screenshots
@app.route('/get_saved_screenshots/<int:user_id>')
def get_saved_screenshots(user_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch saved screenshots for the specific user from the database
        cursor.execute('SELECT content FROM saved_canvas_content WHERE user_id = ?', (user_id,))
        saved_screenshots = cursor.fetchall()

        # Get the file paths for the saved screenshots
        image_paths = [os.path.join(app.config['UPLOAD_FOLDER'], row[0]) for row in saved_screenshots]

        # Pass the fetched data and image paths to the template for rendering
        return render_template('user_designs.html', saved_screenshots=saved_screenshots, image_paths=image_paths)
    except Exception as e:
        print(f"Error fetching saved screenshots: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

@app.route('/serve_saved_image/<path:filename>', methods=['GET'])
def serve_saved_image(filename):
    try:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.isfile(image_path):
            return send_file(image_path, mimetype='image/png')
        else:
            return "Image not found", 404
    except Exception as e:
        print(f"Error serving saved image: {e}")
        return "Internal Server Error", 500



# Retrieve a specific user's purchased items from the shop
@app.route('/get_shop_purchased_items/<int:user_id>')
def get_shop_purchased_items(user_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch purchased items from the shop for the specific user from the database
        cursor.execute('SELECT * FROM shop_purchased_products WHERE user_id = ?', (user_id,))
        columns = [column[0] for column in cursor.description]
        purchased_items = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render_template('shop_purchases.html')
    except Exception as e:
        print(f"Error fetching purchased items from the shop: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

# Retrieve a specific user's purchased products
@app.route('/get_purchased_products/<int:user_id>')
def get_purchased_products(user_id):
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch purchased products for the specific user from the database
        cursor.execute('SELECT * FROM purchased_products WHERE user_id = ?', (user_id,))
        columns = [column[0] for column in cursor.description]
        purchased_products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render_template('designpurchases.html', purchased_products=purchased_products)
    except Exception as e:
        print(f"Error fetching purchased products: {e}")
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

@app.route('/contact')
def contact():
    return render_template('contact.html')

init_db()
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
