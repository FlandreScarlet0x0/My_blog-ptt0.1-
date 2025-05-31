# My_blog/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from functools import wraps
from flask import abort
from flask_login import current_user
from flask_whooshee import Whooshee

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # <-- 重要: 登录视图
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'
migrate = Migrate()
whooshee = Whooshee()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function