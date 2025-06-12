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

    return redirect(url_for('routes.dashboard'))

@routes_blueprint.route('/upload')
def upload():
    return render_template('upload.html')

@routes_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contract(id):
    contract = Contract.query.get_or_404(id)

    if request.method == 'POST':
        # Update only the editable fields
        contract.artist_name = request.form.get('artist_name')
        contract.date = request.form.get('date')
        contract.keywords = request.form.get('keywords')
        contract.affiliation = request.form.get('affiliation')

        db.session.commit()
        flash('Contract updated successfully.', 'success')
        return redirect(url_for('routes.search'))  # Or redirect to dashboard

    return render_template('edit_contracts.html', contract=contract)

