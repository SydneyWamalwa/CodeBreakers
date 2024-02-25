from flask import Flask, render_template, request, redirect, url_for, g, jsonify,send_from_directory,send_file
from io import BytesIO
# from PIL import Image
import sqlite3
import os
import time
import base64
import traceback
from datetime import datetime


app = Flask(__name__)
app.config['DATABASE'] = 'popkulture.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER1'] = os.path.join(os.getcwd(), 'static', 'products')
app.config['PURCHASED_FOLDER'] = os.path.join(os.getcwd(), 'static', 'purchased')  # New folder for purchased screenshots

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
                content TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchased_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userEmail TEXT NOT NULL,
                size TEXT NOT NULL,
                colorOption TEXT,
                imageUrl TEXT NOT NULL,
                screenshotUrl TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shop_purchased_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                description TEXT NOT NULL,
                image TEXT NOT NULL,
                price int NOT NULL
            )
        ''')
        db.commit()

# Call the init_db function to ensure all tables are created before running the app
init_db()

@app.route('/')
def home():
    return render_template('index.html')
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

         db = get_db()
         cursor = db.cursor()
        cursor.execute('INSERT INTO saved_canvas_content (content) VALUES (?)', (filename,))
        db.commit()

        return jsonify({'status': 'success', 'filename': filename})

@app.errorhandler(Exception)
def handle_error(e):
     return jsonify({'error': str(e)}), 500

@app.route('/display/<filename>')
def display_image(filename):
     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
#shop routes
@app.route('/shop')
def products():
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

            print(f"Received data: user_email={user_email}, size={size}, color_option={color_option}, image_url={image_url}, screenshot_url={screenshot_url}, price={price}")

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
                'INSERT INTO purchased_products (userEmail, size, colorOption, imageUrl, screenshotUrl, price) VALUES (?, ?, ?, ?, ?, ?)',
                (user_email, size, color_option, image_url, f'{screenshot_filename}', price)  # Save the filename with .png extension
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

#shop payment routes
@app.route('/shop_purchased_product', methods=['POST'])
def shop_purchased_product():
    if request.method == 'POST':
        try:
            # Retrieve product details from the request
            user_email = request.json.get('user_email')
            image_url = request.json.get('image')
            price = request.json.get('price')
            description=request.json.get('description')

            # Insert the purchased product details into the database
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO purchased_shop_products (userEmail, image, price,description) VALUES (?, ?, ?, ?)',
                (user_email, image_url, price,description)
            )
            db.commit()
            db.close()

            return jsonify({'status': 'success'})
        except Exception as e:
            print(f"Error saving purchased product details: {e}")
            return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

init_db()
if __name__ == '__main__':
    app.run(debug=True)
