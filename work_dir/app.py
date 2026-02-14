from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    projects = [
        {'title': 'Proyek 1', 'description': 'Deskripsi proyek 1'},
        {'title': 'Proyek 2', 'description': 'Deskripsi proyek 2'}
    ]
    return render_template('projects.html', projects=projects)

@app.route('/about')
def about():
    return render_template('about.html')
