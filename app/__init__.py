from flask import Flask
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_login import LoginManager
import os, qrcode

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

limiter = Limiter(get_remote_address)

load_dotenv()

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY']= os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['CACHE_TYPE'] = 'SimpleCache'  
app.config['CACHE_DEFAULT_TIMEOUT'] = 300 
#postgres://scissors_qcf6_user:kt2hJbuwLioiJlEpAUsUFG7HSfNvvEXy@dpg-cif3o2l9aq09mhgc42k0-a.oregon-postgres.render.com/scissors_qcf6

cache = Cache(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from . import routes
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

with app.app_context():
    db.create_all()