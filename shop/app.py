from flask import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_login import LoginManager
from flask_login import UserMixin
from flask_bcrypt import bcrypt
from flask_migrate import Migrate
from flask_mail import *
# import logging

# from flask_uploads import IMAGES,configure_uploads,patch_request_class,UploadSet
import os

from werkzeug.utils import secure_filename

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

web = Flask(__name__)
# basedir=os.path.abspath(os.path.dirname(__file__))
# Database Configuration
db_url = "mysql://root:@localhost/mens_db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
# ceryoehnctfxzdkp      ->>app password_.gmail account managerrana47@gmail.com



web.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/mens_db'
web.secret_key = 'dh47v_secretkey'
db = SQLAlchemy(web)
migrate=Migrate(web,db)

# config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')

# web.config['UPLOADED_PHOTOS_DEST']=os.path.join(basedir,'static/assets/images')
# with open(config_path,"r") as f:
#     params=json.load(f)['params']
web.config['MAIL_SERVER']='smtp.gmail.com'
web.config['MAIL_PORT']=587
web.config['MAIL_USERNAME']='managerrana47@gmail.com'
web.config['MAIL_PASSWORD']='ceryoehnctfxzdkp'
web.config['MAIL_USE_TLS']=True
web.config['MAIL_USE_SSL']=False

mail_sr=Mail(web)


UPLOAD_FOLDER='shop/static/assets/images/'
web.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
# os.makedirs(web.config['UPLOAD_FOLDER'], exist_ok=True)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    
    def __init__(self,id,email,password,name):
        self.id=id
        self.name=name 
        self.email=email
        self.password= bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')

    def chpsw(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))
    
    def hash_password(self, password):
        # Hash the password using bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def __repr__(self):
        return '<User %r>' %self.name
#database end--<<<
from shop.customer import models
     
with web.app_context():
    db.create_all()


login_manager = LoginManager(web)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after defining the user loader function


from shop.customer import routes
from shop.admin import routes

 



