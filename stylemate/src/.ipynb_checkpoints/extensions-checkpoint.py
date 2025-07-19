from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Centralized extension instances
db = SQLAlchemy()
migrate = Migrate()