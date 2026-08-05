import os
from flask import Flask
from dotenv import load_dotenv
from src.infrastructure.repository import Repository
from src.web.routes import register_routes
from database import get_db

load_dotenv()
get_db()

def create_app():

    app = Flask(__name__, template_folder='templates')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
    
    repo = Repository(os.getenv('DATABASE_PATH', 'database.db'))
    
    register_routes(app, repo)
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
