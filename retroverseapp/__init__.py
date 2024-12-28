
from flask import Flask
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_mail import Mail
from retroverseapp.model import db


csrf= CSRFProtect()
mail=Mail()
def create_app():
    
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_pyfile('config.py',silent=True)
    
    db.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    migrate=Migrate(app,db)
    
    return app

app=create_app()

from retroverseapp import route,model,adminroute,form