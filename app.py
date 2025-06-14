from flask import Flask, render_template, url_for, jsonify,redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
app = Flask(__name__)
import feedparser

load_dotenv()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DB_URI")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(db.Model, UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    f_name = db.Column(db.String(50), nullable = False)
    password = db.Column(db.String(200), nullable = False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
@app.route('/')
def home():
    return render_template('home.html')
@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials, please try again.", "danger")

    return render_template("login.html")
@app.route('/register', methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        fname = request.form["fname"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, f_name=fname, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account Created! You can login.", "success")
        return redirect(url_for("login"))
    return render_template('register.html')
@app.route('/contacts')
def contacts():
    return render_template('contacts.html')
@app.route('/services')
def services():
    return render_template('services.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('studentdash.html')
@app.route('/timetable')
@login_required
def timetable():
    user_id = current_user.id
    if not user_id:
        flash("You need to login first!", "danger")
        return redirect(url_for('login'))

    # Embed Google Sheets iframe code
    google_sheets_embed_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRYdN6R4Dj9V2xNN-Y4LfN7eW9Tm9b7mZaVQYvRIZ5OUnFnYIcJoY4EVo171cjCDGWpST5LEd3VvYWG/pubhtml"
    
    # Render the timetable on the page with the iframe URL
    return render_template('timetable.html', google_sheets_embed_url=google_sheets_embed_url)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

RSS_FEEDS = {
    "technology": "https://feeds.feedburner.com/TheHackersNews",
    "science": "https://www.sciencedaily.com/rss/top/science.xml",
    "education": "https://www.eschoolnews.com/teaching-and-learning/feed/",
    "health": "https://www.modernhealthcare.com/section/rss/news?days=7&topics=81631",
    "architecture" : "https://architectureau.com/editorspick/rss.xml",
    "music" : "https://pitchfork.com/feed/feed-news/rss"
}

@app.route('/blogs', methods=['GET'])
@login_required
def blogs():
    # Get the selected topic from the query parameter, default to 'technology'
    topic = request.args.get('topic', 'technology').lower()  # Use .lower() to make it case-insensitive
    
    # Check if the selected topic is valid
    if topic not in RSS_FEEDS:
        return "Topic not found", 404
    
    # Fetch and parse the RSS feed for the selected topic
    feed = feedparser.parse(RSS_FEEDS[topic])
    posts = []

    for entry in feed.entries[:10]:  # Limit to 10 posts
        image_url = None
        if 'enclosures' in entry and entry.enclosures:
            image_url = entry.enclosures[0]['url']

        posts.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
            "published": entry.published,
            "image_url": image_url
        })
    
    # Debugging: Print out the topic for verification
    print(f"Requested topic: {topic}")

    return render_template('myblog.html', topic=topic.capitalize(), posts=posts, topics=RSS_FEEDS)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)