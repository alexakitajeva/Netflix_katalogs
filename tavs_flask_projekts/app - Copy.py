import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///netflix.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'supersecretkey'
db = SQLAlchemy(app)

class NetflixShow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)

def generate_visualizations():
    df = pd.read_sql('SELECT * FROM netflix_show', db.engine)
    if df.empty:
        return
    
    plt.figure(figsize=(8, 6))
    ax = sns.countplot(y=df['genre'], order=df['genre'].value_counts().index, palette='coolwarm')
    plt.title("Populārākie žanri Netflix")
    plt.xlabel("Skaits")
    plt.ylabel("Žanrs")
    plt.savefig('static/genre_distribution.png')
    for container in ax.containers:
        ax.bar_label(container, fmt='%d', label_type="edge", fontsize=10, padding=3)

    plt.savefig('static/genre_distribution.png')

    plt.figure(figsize=(8, 6))
    sns.histplot(df['release_year'], bins=range(df['release_year'].min(), df['release_year'].max() + 1), kde=True, color='blue')
    plt.title("Filmu/seriālu izdošanas gadu sadalījums")
    plt.xlabel("Gads")
    plt.ylabel("Skaits")
    plt.xticks(rotation=45)
    plt.savefig('static/release_year_distribution.png')

@app.route('/')
def index():
    title = request.args.get('title', '').strip()
    genre = request.args.get('genre', '').strip()
    year = request.args.get('year', '').strip()

    query = NetflixShow.query

    if title:
        query = query.filter(NetflixShow.title.ilike(f'%{title}%'))
    if genre:
        query = query.filter(NetflixShow.genre.ilike(f'%{genre}%'))
    if year.isdigit():
        query = query.filter(NetflixShow.release_year == int(year))

    shows = query.all()
    return render_template('index.html', shows=shows)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(filepath)
            process_csv(filepath)
            return {"status": "success"}
        else:
            flash("Lūdzu, augšupielādējiet CSV failu!", "danger")
    return render_template('upload.html')

def process_csv(filepath):
    df = pd.read_csv(filepath)
    df = df[['title', 'release_year', 'listed_in', 'type']]
    df = df.rename(columns={'listed_in': 'genre'})
    df = df.dropna()
    df['release_year'] = df['release_year'].astype(int)
    db.session.query(NetflixShow).delete()
    db.session.commit()
    for _, row in df.iterrows():
        show = NetflixShow(title=row['title'], release_year=row['release_year'], genre=row['genre'], type=row['type'])
        db.session.add(show)
    db.session.commit()
    generate_visualizations()

@app.route('/get_data')
def get_data():
    shows = NetflixShow.query.all()
    genre_counts = {}
    for show in shows:
        genres = show.genre.split(", ")
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    year_counts = {}
    for show in shows:
        year_counts[show.release_year] = year_counts.get(show.release_year, 0) + 1
    data = {
        "genres": list(genre_counts.keys()),
        "genre_counts": list(genre_counts.values()),
        "years": list(year_counts.keys()),
        "year_counts": list(year_counts.values())
    }
    return jsonify(data)

@app.route('/visualizations')
def visualizations():
    return render_template('visualizations.html')

@app.route('/home')
def home():
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

