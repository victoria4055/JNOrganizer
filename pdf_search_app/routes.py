from flask import Blueprint, render_template, request, redirect, url_for, flash


routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route('/')
def home():
    return render_template('home.html')

@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Dummy login logic — replace later with real validation
        username = request.form.get('username')
        password = request.form.get('password')
        print(f"Login attempt: {username} / {password}")  # for testing
        return redirect(url_for('routes.dashboard'))
    
    return render_template('login.html')

@routes_blueprint.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@routes_blueprint.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    return f"You searched for: {query}"

@routes_blueprint.route('/upload')
def upload():
    return render_template('upload.html')
