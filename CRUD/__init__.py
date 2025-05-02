from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from logging import basicConfig, INFO
import logging
from CRUD.config import Config
from dotenv import load_dotenv
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Configurar logging
logging.basicConfig(filename='logs.log', level=logging.INFO)

db = SQLAlchemy(app)

from CRUD import views