from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')
<<<<<<< HEAD
@app.route('/contacts')
def contacts():
    return render_template('contacts.html')
@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/about')
def about():
    return render_template('about.html')

=======
@app.route('/about')
def about():
    return render_template('about.html')
>>>>>>> d0fb1421fe400488e7f71199ea3c4a7e1ad7ecd8



if __name__ == '__main__':
    app.run(debug=True)