from app import create_app, db
from flask_migrate import Migrate
from app.models import User, Job  # Import models
from flask_login import LoginManager

app = create_app()

# Initialize Migrate manually in run.py
migrate = Migrate(app, db)

# Create all database tables (if you don’t use migrations)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
