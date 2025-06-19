import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


# Initialize SQLAlchemy
from .models import db

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '..', 'contracts.db')

    # Config
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db with app
    db.init_app(app)
    migrate.init_app(app, db) 


    # Import and register routes
    from .routes import routes_blueprint
    app.register_blueprint(routes_blueprint)

    login_manager = LoginManager()
    login_manager.login_view = 'routes.login'  # route name
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

