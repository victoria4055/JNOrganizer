from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import db, Contract
from sqlalchemy import or_
import os
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from .forms import LoginForm, RegisterForm
from werkzeug.utils import secure_filename
from .extract import extract_metadata 
from flask_login import login_required, current_user
from pdf_search_app.models import ActivityLog
from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash, render_template, redirect, url_for
from .forms import ChangePasswordForm

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'MockContracts')


routes_blueprint = Blueprint('routes', __name__)


def generate_summary(text):
    # Placeholder until OpenAI API integration is approved
    if not text:
        return ""
    return text[:300] + "..." if len(text) > 300 else text

@routes_blueprint.route('/')
def home():
    return render_template('home.html')

@routes_blueprint.route('/dashboard')
@login_required
def dashboard():
    log = ActivityLog(user_id=current_user.id, action="Viewed Dashboard")
    db.session.add(log)
    db.session.commit()
    return render_template('dashboard.html')

@routes_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('search_query', '').strip()
        return redirect(url_for('routes.search', q=query))

    query = request.args.get('q', '').strip()
    sort_option = request.args.get('sort', 'relevance')  # default sort

    if not query:
        return render_template('search_results.html', contracts=[], query=query, count=0)

    filters = or_(
        Contract.artist_name.ilike(f'%{query}%'),
        Contract.date.ilike(f'%{query}%'),
        Contract.keywords.ilike(f'%{query}%'),
        Contract.affiliation.ilike(f'%{query}%'),
        Contract.filename.ilike(f'%{query}%') 

        
    )

    # Sorting logic
    if sort_option == 'artist_asc':
        contracts = Contract.query.filter(filters).order_by(Contract.artist_name.asc()).all()
    elif sort_option == 'artist_desc':
        contracts = Contract.query.filter(filters).order_by(Contract.artist_name.desc()).all()
    elif sort_option == 'date_asc':
        contracts = Contract.query.filter(filters).order_by(Contract.date.asc()).all()
    elif sort_option == 'date_desc':
        contracts = Contract.query.filter(filters).order_by(Contract.date.desc()).all()
    else:  # default relevance fallback
        contracts = Contract.query.filter(filters).all()

    for c in contracts:
        c.display_name = os.path.basename(c.filename)

    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, action=f"Performed search: '{query}'")
        db.session.add(log)
        db.session.commit()   

    return render_template('search_results.html', contracts=contracts, query=query, count=len(contracts))


@routes_blueprint.route("/results")
def results():
    results = Contract.query.all()
    for c in results:
        c.display_name = os.path.basename(c.filename)
    return render_template("results.html", results=results)


@routes_blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('contract_file')
        if not file:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        base, ext = os.path.splitext(filename)
        save_dir = 'pdf_search_app/static/MockContracts'
        save_path = os.path.join(save_dir, filename)

        confirm_rename = request.form.get('confirm_rename')
        renamed_filename = request.form.get('renamed_filename')

        if confirm_rename and renamed_filename:
            filename = renamed_filename
            save_path = os.path.join(save_dir, filename)
        else:
            # Check for duplicate (file or DB)
            if os.path.exists(save_path) or Contract.query.filter_by(filename=filename).first():
                counter = 1
                new_filename = f"{base}-{counter}{ext}"
                while os.path.exists(os.path.join(save_dir, new_filename)) or Contract.query.filter_by(filename=new_filename).first():
                    counter += 1
                    new_filename = f"{base}-{counter}{ext}"

                # Ask user to confirm rename
                return render_template(
                    'confirm_rename.html',
                    original=filename,
                    suggested=new_filename
                )
            

        save_path = os.path.join('pdf_search_app/static/MockContracts', filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        from .extract import extract_metadata
        metadata = extract_metadata(save_path)
        summary = generate_summary(metadata.get('content', ''))

        new_contract = Contract(
            filename=filename,
            artist_name=metadata.get('artist_name', 'Unknown'),
            date=metadata.get('date', 'Unknown'),
            keywords=metadata.get('keywords', ''),
            affiliation=metadata.get('affiliation', ''),
            status=metadata.get('status', ''),
            summary=metadata.get('summary', ''),
            category=metadata.get('category', 'Uncategorized') 

        )
        db.session.add(new_contract)
        db.session.commit()

        log = ActivityLog(user_id=current_user.id, action=f"Uploaded contract: {filename}")
        db.session.add(log)
        db.session.commit()

        return render_template('upload_success.html', contract=new_contract)

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
        contract.status = request.form.get('completion')
        contract.category = request.form.get('category') 


        db.session.commit()

        log = ActivityLog(user_id=current_user.id, action=f"Edited contract: {contract.filename}")
        db.session.add(log)
        db.session.commit()

        flash('Contract updated successfully.', 'success')
        return redirect(url_for('routes.database')) 

    return render_template('edit_contracts.html', contract=contract)


@routes_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists')
            return redirect(url_for('routes.register'))

        if not form.email.data.endswith('@jnrecords.com') and form.email.data != "victoria.v1@icloud.com":
            flash('Only JNRecords employees can register.')
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
        if user:
            # Allow if email ends in @jnrecords.com or it's your specific email
            if user.email.endswith('@jnrecords.com') or user.email == "victoria.v1@icloud.com":
                if user.check_password(form.password.data):
                    login_user(user)
                    return redirect(url_for('routes.dashboard'))
                else:
                    flash('Invalid password.')
            else:
                flash('Access denied. Only JNRecords employees may log in.')
        else:
            flash('User not found.')
    return render_template('login.html', form=form)


@routes_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))


@routes_blueprint.route('/database')
@login_required
def database():
    sort_option = request.args.get('sort', 'date_desc')
    category_filter = request.args.get('category', None)

    query = Contract.query

    if category_filter:
        query = query.filter(Contract.category.ilike(f'%{category_filter}%'))

    # Sorting logic
    if sort_option == 'artist_asc':
        query = query.order_by(Contract.artist_name.asc())
    elif sort_option == 'artist_desc':
        query = query.order_by(Contract.artist_name.desc())
    elif sort_option == 'date_asc':
        query = query.order_by(Contract.date.asc())
    elif sort_option == 'category_asc':
        query = query.order_by(Contract.category.asc())
    elif sort_option == 'category_desc':
        query = query.order_by(Contract.category.desc())
    else:
        query = query.order_by(Contract.date.desc())

    contracts = query.all()
    for c in contracts:
        c.display_name = os.path.basename(c.filename)

    if current_user.is_authenticated:
        log = ActivityLog(user_id=current_user.id, action="Viewed Database")
        db.session.add(log)
        db.session.commit()

    return render_template('general_db.html', contracts=contracts)

@routes_blueprint.route('/user_home')
@login_required
def user_home():
    viewed = ActivityLog.query.filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.action.like("Viewed contract:%")
    ).order_by(ActivityLog.timestamp.desc()).limit(10).all()

    uploads_edits = ActivityLog.query.filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.action.like("Uploaded contract:%") | ActivityLog.action.like("Edited contract:%")
    ).order_by(ActivityLog.timestamp.desc()).limit(10).all()

    return render_template(
        'user_home.html',
        user=current_user,
        viewed=viewed,
        uploads_edits=uploads_edits
    )


@routes_blueprint.route('/open/<filename>')
@login_required
def open_contract(filename):
    log = ActivityLog(user_id=current_user.id, action=f"Viewed contract: {filename}")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('static', filename='MockContracts/' + filename))

@routes_blueprint.route('/help')
@login_required
def help():
    return render_template('help.html')

@routes_blueprint.route('/overview/<int:contract_id>')
@login_required
def contract_overview(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    # Use existing summary, or generate a longer one from content
    from .extract import extract_metadata
    full_path = os.path.join('pdf_search_app/static/MockContracts', contract.filename)
    metadata = extract_metadata(full_path)
    full_text = metadata.get('content', '')

    # Generate long summary
    long_summary = generate_summary(full_text)  # you can create a generate_long_summary function here

    log = ActivityLog(user_id=current_user.id, action=f"Viewed overview for: {contract.filename}")
    db.session.add(log)
    db.session.commit()

    return render_template('contract_overview.html', contract=contract, long_summary=long_summary)

@routes_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.password, form.old_password.data):
            flash("Incorrect current password.", "danger")
        elif form.new_password.data != form.confirm_new_password.data:
            flash("New passwords do not match.", "danger")
        else:
            current_user.password = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password changed successfully.", "success")
            return redirect(url_for('user_home'))
    return render_template('change_password.html', form=form)
