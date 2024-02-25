from flask import Flask, render_template, request, redirect, url_for, g, jsonify,send_from_directory,send_file
from io import BytesIO
# from PIL import Image
import sqlite3
import os
import time
# import base64
from datetime import datetime


app = Flask(__name__)
app.config['DATABASE'] = 'popkulture.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static', 'uploads')
app.config['UPLOAD_FOLDER1'] = os.path.join(os.getcwd(), 'static', 'products')

# generate a unique id for product table#
def generate_unique_id():
    timestamp = int(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    return str(timestamp)

@app.route('/generate-reference', methods=['POST'])
def generate_reference():
    reference = generate_unique_id()
    return jsonify({'reference': reference})

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
        db.commit()

init_db()

@app.route('/')
def home():
    return render_template('index.html')
#design routes
# @app.route('/save_canvas', methods=['POST'])
# def save_canvas_content():
#     if request.method == 'POST':
#         canvas_content = request.json.get('canvas_content')
#         img_data = base64.b64decode(canvas_content.split(',')[1])

#         os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

#         filename = f'tshirt_{int(time.time())}.png'
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#         with open(filepath, 'wb') as f:
#             f.write(img_data)

#         db = get_db()
#         cursor = db.cursor()
#         cursor.execute('INSERT INTO saved_canvas_content (content) VALUES (?)', (filename,))
#         db.commit()

#         return jsonify({'status': 'success', 'filename': filename})

# @app.errorhandler(Exception)
# def handle_error(e):
#     return jsonify({'error': str(e)}), 500

# @app.route('/display/<filename>')
# def display_image(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
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
# @app.route('/shop_display')
# def shop_display():
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute("SELECT * FROM products")
#     records = cursor.fetchall()
#     return render_template('shop.html', records=records)


@app.route('/product_image/<string:unique_id>')
def product_image(unique_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT image FROM products WHERE unique_id = ?", (unique_id,))
    image = cursor.fetchone()[0]
    return send_file(BytesIO(image), mimetype='image/jpeg')


if __name__ == '__main__':
    app.run(debug=True)
