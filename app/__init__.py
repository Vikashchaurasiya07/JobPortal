from flask import Flask
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager

# Load environment variables from .env
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    # Create Flask app instance
    app = Flask(__name__)

    # App configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///job_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize db and bcrypt with app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # Import and register the routes blueprint
    from .routes import main
    app.register_blueprint(main)

    return app
