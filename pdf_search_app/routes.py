from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Contract


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

@routes_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query', '').strip()
        if not query:
            return render_template('search_results.html', contracts=[], query=query, count=0)

        results = Contract.query.filter(Contract.artist_name.ilike(f'%{query}%')).all()
        return render_template('search_results.html', contracts=results, query=query, count=len(results))

    return redirect(url_for('dashboard'))

@routes_blueprint.route('/upload')
def upload():
    return render_template('upload.html')
