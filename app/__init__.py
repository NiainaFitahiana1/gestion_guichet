from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_login import LoginManager
from .config import Config
from .models.user import User
from bson import ObjectId

app = Flask(__name__)
app.config.from_object(Config)

mongo = PyMongo(app)

CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_bp.login"

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User.from_mongo(user_data)
    return None

from .routes.voyage import voyage_bp
app.register_blueprint(voyage_bp)

from .routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from .routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

from .routes.voyageur import voyageur_bp
app.register_blueprint(voyageur_bp, url_prefix="/voyageurs")

from .routes.home import home_bp
app.register_blueprint(home_bp, url_prefix="/home")

from .routes.public import public_bp
app.register_blueprint(public_bp, url_prefix="/public")

from .routes.guichetier import guichet_bp
app.register_blueprint(guichet_bp, url_prefix="/guichetier")

def create_app():
    return app
