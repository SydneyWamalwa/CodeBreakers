from flask import Flask,render_template

# Simulated database of shirts
shirts_data = [
    {"id": 1, "name": "T-shirt 1", "price": 19.99, "image_url": "/static/images/sample shirt.jpeg"},
    {"id": 2, "name": "T-shirt 2", "price": 24.99, "image_url": "/static/images/sample shirt.jpeg"},
    
]


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/shop')
def shop():
    return render_template('Display_Products.html', shirts=shirts_data)



if __name__ == '__main__':
    app.run(debug=True)