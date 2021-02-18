from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'account.login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.account.routes import account
    from app.errors.handlers import errors
    from app.main.routes import main

    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(account)

    return app
