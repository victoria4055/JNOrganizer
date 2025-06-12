from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Contract
from sqlalchemy import or_
import os
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from .forms import LoginForm, RegisterForm



routes_blueprint = Blueprint('routes', __name__)

@routes_blueprint.route('/')
def home():
    return render_template('home.html')

@routes_blueprint.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@routes_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query', '').strip()
        if not query:
            return render_template('search_results.html', contracts=[], query=query, count=0)

        results = Contract.query.filter(
            or_(
                Contract.artist_name.ilike(f'%{query}%'),
                Contract.date.ilike(f'%{query}%'),
                Contract.keywords.ilike(f'%{query}%'),
                Contract.affiliation.ilike(f'%{query}%')
            )
        ).all()

        for c in results:
            c.display_name = os.path.basename(c.filename)

        return render_template('search_results.html', contracts=results, query=query, count=len(results))

    return redirect(url_for('routes.dashboard'))

@routes_blueprint.route("/results")
def results():
    results = Contract.query.all()
    for c in results:
        c.display_name = os.path.basename(c.filename)
    return render_template("results.html", results=results)


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


@routes_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
            return redirect(url_for('routes.register'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)

@routes_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('routes.dashboard'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@routes_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

