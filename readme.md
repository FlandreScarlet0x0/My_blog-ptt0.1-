Flask 博客项目完整代码文档
1. 项目简介
这是一个功能完善的个人博客系统，基于 Flask 框架构建。主要功能包括：

用户系统: 用户注册、登录、登出、个人资料编辑。
文章系统: 使用 Markdown 创建、编辑、删除文章，支持分类和标签。
富文本编辑: 集成 EasyMDE 编辑器，支持图片和视频上传。
评论系统: 支持对文章进行评论和回复。
主题系统:
浅色/深色颜色模式切换。
多种视觉主题切换（关联不同的背景图片和背景音乐）。
前端体验: AJAX 无刷新页面导航，带来单页应用（SPA）般的流畅体验。
后台管理: 为管理员提供用户管理和文章管理的基础后台。
2. 项目结构
请务必遵循以下文件和文件夹结构来组织您的项目：

D:\az\blog\
|
├── .flaskenv              # 环境变量文件 (重要!)
|
├── instance/              # Flask 自动创建，用于存放数据库等实例文件
|
├── migrations/            # Flask-Migrate 数据库迁移脚本
|
├── My_blog/               # Flask 应用核心包
|   |
|   ├── __init__.py        # 应用工厂函数 (核心)
|   ├── config.py          # 应用配置文件
|   ├── extensions.py      # Flask 扩展统一定义
|   ├── models.py          # 数据库模型
|   ├── command.py         # 自定义命令行
|   |
|   ├── routes/            # 路由蓝图
|   |   ├── main.py
|   |   ├── auth.py
|   |   └── admin.py
|   |
|   ├── static/            # 静态文件
|   |   ├── css/
|   |   │   └── style.css
|   |   ├── js/
|   |   │   ├── theme.js
|   |   │   ├── background_fade.js
|   |   │   └── navigation.js
|   |   ├── images/        # (需要手动创建，用于存放背景图等)
|   |   └── uploads/       # (程序会自动创建，用于存放用户上传的文件)
|   |
|   └── templates/         # Jinja2 模板
|       ├── base.html
|       ├── index.html
|       ├── post.html
|       ├── create_post.html
|       ├── edit_post.html
|       ├── login.html
|       ├── register.html
|       ├── profile.html
|       ├── edit_profile.html
|       |
|       └── admin/         # 后台管理模板
|           ├── index.html
|           ├── users.html
|           └── posts.html
|
└── run.py                 # 应用启动脚本
3. 安装与运行指南
准备环境: 确保已安装 Python 3，并创建和激活虚拟环境。
安装依赖: 在激活的虚拟环境中运行 pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login markdown bleach python-dotenv Flask-Whooshee。
初始化数据库: 首次运行时，在项目根目录（D:\az\blog）下依次执行以下命令：
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
创建管理员账号 (可选):
flask create-admin (按照提示输入信息)
运行应用:
flask run
在浏览器中访问 http://127.0.0.1:5000
4. 完整代码清单
4.1 根目录文件 (D:\az\blog)
.flaskenv
代码段

FLASK_APP=run.py
FLASK_DEBUG=1
run.py
Python

# D:/az/blog/run.py
import os
from My_blog import create_app

# 从 .flaskenv 文件中加载环境变量
app = create_app()

if __name__ == '__main__':
    # 使用 `flask run` 命令启动更佳
    app.run()
4.2 核心应用包 (D:\az\blog\My_blog)
__init__.py
Python

# D:/az/blog/My_blog/__init__.py
import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate, whooshee
from .models import User

def create_app(config_class=Config):
    """创建并配置 Flask 应用实例的工厂函数"""
    instance_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance')
    app = Flask(__name__, instance_path=instance_folder) 
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass 

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    from . import models
    migrate.init_app(app, db)
    whooshee.init_app(app)

    # 注册蓝图
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # 注册自定义命令
    from .command import init_app as init_command_app
    init_command_app(app)

    # Shell 上下文
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db, 
            'User': models.User, 
            'Post': models.Post,
            'Category': models.Category,
            'Tag': models.Tag,
            'Comment': models.Comment
        }

    return app
config.py
Python

# D:/az/blog/My_blog/config.py
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-!@#$%'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(project_root, 'instance', 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 5
    COMMENTS_PER_PAGE = 10
    UPLOADED_MEDIA_DEST = os.path.join(project_root, 'My_blog', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    WHOOSHEE_MIN_STRING_LEN = 1
extensions.py
Python

# D:/az/blog/My_blog/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from functools import wraps
from flask import abort
from flask_login import current_user
from flask_whooshee import Whooshee

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
whooshee = Whooshee()

login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
models.py
Python

# D:/az/blog/My_blog/models.py
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re
from .extensions import db, whooshee
import markdown
import bleach

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

@whooshee.register_model('username', 'email')
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    about_me = db.Column(db.String(140))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def __repr__(self): return f'<User {self.username}>'

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    def __repr__(self): return f'<Category {self.name}>'

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    def __repr__(self): return f'<Tag {self.name}>'

@whooshee.register_model('title', 'body')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    slug = db.Column(db.String(200), unique=True, index=True, nullable=False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self): return f'<Post {self.title}>'
    
    def generate_slug(self, title_to_slug=None):
        if not title_to_slug: title_to_slug = self.title
        s = title_to_slug.lower().strip()
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '-', s)
        s = re.sub(r'-+', '-', s).strip('-')
        if not s: s = "post"
        original_slug = s
        counter = 1
        query = Post.query.filter_by(slug=s)
        if self.id: query = query.filter(Post.id != self.id)
        while query.first():
            s = f"{original_slug}-{counter}"
            counter += 1
            query = Post.query.filter_by(slug=s)
            if self.id: query = query.filter(Post.id != self.id)
        self.slug = s

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'source', 'audio', 'br', 'hr', 'span']
        allowed_attrs = {'*': ['class', 'style'], 'a': ['href', 'title'],
                         'img': ['src', 'alt', 'title', 'width', 'height'],
                         'video': ['src', 'controls', 'width', 'height', 'poster'],
                         'source': ['src', 'type'], 'audio': ['src', 'controls']}
        html = markdown.markdown(value, extensions=['fenced_code', 'tables', 'attr_list'])
        target.body_html = bleach.linkify(bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade='all, delete-orphan')
    def __repr__(self): return f'<Comment {self.body[:20]}...>'
command.py
Python

# D:/az/blog/My_blog/command.py
import click
from flask.cli import with_appcontext
from .extensions import db
from .models import User

def init_app(app):
    app.cli.add_command(create_admin_command)

@click.command('create-admin')
@with_appcontext
def create_admin_command():
    """创建一个管理员账户。"""
    username = click.prompt('输入管理员用户名', default='admin')
    email = click.prompt('输入管理员邮箱', default=f'{username}@example.com')
    password = click.prompt('输入管理员密码', hide_input=True, confirmation_prompt=True)
    
    if User.query.filter_by(username=username).first():
        click.echo(f'错误：用户名 "{username}" 已存在！')
        return
    if User.query.filter_by(email=email).first():
        click.echo(f'错误：邮箱 "{email}" 已存在！')
        return
        
    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'管理员 "{username}" 创建成功！')
4.3 路由包 (D:\az\blog\My_blog\routes)
main.py
Python

# D:/az/blog/My_blog/routes/main.py
from flask import (render_template, Blueprint, request, redirect, url_for, 
                   flash, current_app, g, session, jsonify, abort)
from werkzeug.utils import secure_filename
from ..models import db, Post, Comment, Category, Tag, User 
from flask_login import login_required, current_user
import datetime
import os

bp = Blueprint('main', __name__)

@bp.before_app_request
def before_request():
    g.current_year = datetime.datetime.now(datetime.timezone.utc).year
    g.current_theme_for_background_fade = session.get('visual_theme', 'light')
    g.is_admin = current_user.is_authenticated and getattr(current_user, 'is_admin', False)

@bp.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')

@bp.route('/set-visual-theme/<theme_name>')
def set_visual_theme(theme_name):
    valid_themes = ['light', 'dark', 'blue', 'green', 'yuan']
    if theme_name in valid_themes:
        session['visual_theme'] = theme_name
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 5)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    return render_template('index.html', title='首页', posts=posts, pagination=pagination)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/upload', methods=['POST'])
@login_required 
def upload_file():
    if 'file' not in request.files: return jsonify({'error': '未找到文件'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': '未选择文件'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOADED_MEDIA_DEST']
        os.makedirs(upload_folder, exist_ok=True)
        base, ext = os.path.splitext(filename)
        counter = 1
        filepath = os.path.join(upload_folder, filename)
        while os.path.exists(filepath):
            filename = f"{base}_{counter}{ext}"
            filepath = os.path.join(upload_folder, filename)
            counter += 1
        try:
            file.save(filepath)
            file_url = url_for('static', filename=f'uploads/{filename}')
            return jsonify({'url': file_url})
        except Exception as e:
            return jsonify({'error': f'无法保存文件: {str(e)}'}), 500
    return jsonify({'error': '文件类型不允许'}), 400

@bp.route('/post/<slug>')
def post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('COMMENTS_PER_PAGE', 10)
    pagination = post.comments.filter_by(parent_id=None).order_by(Comment.timestamp.asc()).paginate(page=page, per_page=per_page, error_out=False)
    comments = pagination.items
    return render_template('post.html', title=post.title, post=post, comments=comments, pagination=pagination)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        category_name = request.form.get('category', '').strip()
        tags_str = request.form.get('tags', '')

        if not title or not body:
            flash('标题和内容是必填项！', 'danger')
            return render_template('create_post.html', title_data=title, body_data=body, category_data=category_name, tags_data=tags_str)

        category = None
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
        
        new_post = Post(title=title, body=body, author=current_user, category=category)
        new_post.generate_slug()

        tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            if tag not in new_post.tags:
                new_post.tags.append(tag)
        
        db.session.add(new_post)
        try:
            db.session.commit()
            flash('文章发布成功！', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'创建文章失败: {e}')
            flash('发布文章时发生错误，请稍后重试。', 'danger')
            return render_template('create_post.html', title_data=title, body_data=body, category_data=category_name, tags_data=tags_str)

    return render_template('create_post.html', title="创建新文章")

@bp.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user and not g.is_admin:
        abort(403)
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        category_name = request.form.get('category', '').strip()
        tags_str = request.form.get('tags', '')

        category = None
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
        post.category = category
        
        post.tags.clear()
        tag_names = [name.strip() for name in tags_str.split(',') if name.strip()]
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            post.tags.append(tag)
        
        post.generate_slug(post.title)
        db.session.add(post)
        try:
            db.session.commit()
            flash('文章更新成功！', 'success')
            return redirect(url_for('main.post', slug=post.slug))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新文章失败: {e}')
            flash('更新文章时发生错误。', 'danger')

    tags_data = ', '.join(tag.name for tag in post.tags)
    return render_template('edit_post.html', title="编辑文章", post=post, tags_data=tags_data)

@bp.route('/post/<slug>/delete', methods=['POST'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user and not g.is_admin:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除。', 'success')
    return redirect(url_for('main.index'))

@bp.route('/post/<slug>/comment', methods=['POST'])
@login_required
def add_comment(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    body = request.form.get('body', '').strip()
    parent_id = request.form.get('parent_id')

    if not body:
        flash('评论内容不能为空。', 'danger')
        return redirect(url_for('main.post', slug=slug, _anchor='comment-form'))

    parent = None
    if parent_id and parent_id.isdigit():
        parent = Comment.query.get(int(parent_id))
        if not parent or parent.post_id != post.id:
            flash('无效的回复目标。', 'danger')
            return redirect(url_for('main.post', slug=slug))
    
    comment = Comment(body=body, author=current_user, post=post, parent=parent)
    db.session.add(comment)
    db.session.commit()
    flash('评论成功！', 'success')
    return redirect(url_for('main.post', slug=slug, _anchor=f'comment-{comment.id}'))
auth.py
Python

# D:/az/blog/My_blog/routes/auth.py
from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user, login_required
from ..models import db, User, Post

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('两次输入的密码不一致。', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(username=username).first():
            flash('该用户名已被使用。', 'warning')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册。', 'warning')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已成功注册！', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='注册')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember_me') is not None
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('无效的用户名或密码。', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('login.html', title='登录')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('POSTS_PER_PAGE', 5)
    pagination = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    posts = pagination.items
    return render_template('profile.html', title=f"{user.username} 的个人主页", user=user, posts=posts, pagination=pagination)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username').strip()
        about_me = request.form.get('about_me').strip()

        if new_username and new_username != current_user.username:
            if User.query.filter(User.username == new_username, User.id != current_user.id).first():
                flash('该用户名已被使用。', 'warning')
                return render_template('edit_profile.html', title='编辑资料', user=current_user)
            current_user.username = new_username
        
        current_user.about_me = about_me
        db.session.commit()
        flash('您的资料已更新。', 'success')
        return redirect(url_for('auth.profile', username=current_user.username))
    return render_template('edit_profile.html', title='编辑资料', user=current_user)
admin.py
Python

# D:/az/blog/My_blog/routes/admin.py
from flask import render_template, Blueprint, request, current_app, redirect, url_for, flash
from flask_login import login_required
from ..extensions import admin_required
from ..models import db, User, Post

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html', title="管理后台")

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    pagination = User.query.order_by(User.member_since.desc()).paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    return render_template('admin/users.html', title="用户管理", users=users, pagination=pagination)

@bp.route('/posts')
@login_required
@admin_required
def manage_posts():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    posts = pagination.items
    return render_template('admin/posts.html', title="文章管理", posts=posts, pagination=pagination)

@bp.route('/delete_post_admin/<int:post_id>', methods=['POST'])
@login_required
@admin_required
def delete_post_admin(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f'文章 "{post.title}" 已从后台删除。', 'success')
    return redirect(url_for('admin.manage_posts'))
4.4 静态文件 (D:\az\blog\My_blog\static)
css/style.css
CSS

/* static/css/style.css */

/* ================== */
/* ===  CSS 变量  === */
/* ================== */

/* --- 浅色主题 (默认) --- */
:root, [data-theme="light"], html[data-bs-theme="light"] {
    --bs-primary: #0d6efd;
    --bs-secondary: #6c757d;
    --bs-success: #198754;
    --bs-info: #0dcaf0;
    --bs-warning: #ffc107;
    --bs-danger: #dc3545;
    --bs-light: #f8f9fa;
    --bs-dark: #212529;
    --bs-body-color: #212529;
    --bs-body-bg: #ffffff;
    --bs-link-color: #0d6efd;
    --bs-link-hover-color: #0a58ca;
    --bs-border-color: #dee2e6;
    --bs-border-color-translucent: rgba(0, 0, 0, 0.175);
    --bs-tertiary-bg: #e9ecef;
    --navbar-bg: rgba(255, 255, 255, 0.9);
    --card-bg: #ffffff;
    --footer-bg: #f8f9fa;
    --footer-text-color: #6c757d;
}

/* --- 深色主题 --- */
[data-theme="dark"], html[data-bs-theme="dark"] {
    --bs-primary: #6ea8fe;
    --bs-secondary: #adb5bd;
    --bs-success: #48a77a;
    --bs-info: #6edff6;
    --bs-warning: #ffcd39;
    --bs-danger: #e66573;
    --bs-light: #343a40;
    --bs-dark: #e9ecef;
    --bs-body-color: #e9ecef;
    --bs-body-bg: #1a1a2e; /* 深蓝紫色背景 */
    --bs-link-color: #6ea8fe;
    --bs-link-hover-color: #9ec5fe;
    --bs-border-color: #495057;
    --bs-border-color-translucent: rgba(255, 255, 255, 0.15);
    --bs-tertiary-bg: #2c303a;
    --navbar-bg: rgba(26, 26, 46, 0.85); /* 深色导航栏，带透明 */
    --card-bg: #232a34; /* 深色卡片 */
    --footer-bg: #1a1a2e;
    --footer-text-color: #adb5bd;
}

/* --- 宁静蓝 (Blue) --- */
html[data-bs-theme="light"] #ajax-content-container[data-current-theme="blue"] {
    --bs-primary: #007bff;
    --bs-link-color: #0056b3;
    --bs-link-hover-color: #007bff;
}
html[data-bs-theme="dark"] #ajax-content-container[data-current-theme="blue"] {
    --bs-primary: #4dabf7;
    --bs-link-color: #4dabf7;
    --bs-link-hover-color: #74c0fc;
}

/* --- 青春绿 (Green) --- */
html[data-bs-theme="light"] #ajax-content-container[data-current-theme="green"] {
    --bs-primary: #28a745;
    --bs-link-color: #1e7e34;
    --bs-link-hover-color: #28a745;
}
html[data-bs-theme="dark"] #ajax-content-container[data-current-theme="green"] {
    --bs-primary: #4dabf7;
    --bs-link-color: #4dabf7;
    --bs-link-hover-color: #74c0fc;
}

/* --- 活力橙 (Yuan) --- */
html[data-bs-theme="light"] #ajax-content-container[data-current-theme="yuan"] {
    --bs-primary: #9c9c97;
    --bs-link-color: #4dabf7;
    --bs-link-hover-color: #74c0fc;
}
html[data-bs-theme="dark"] #ajax-content-container[data-current-theme="yuan"] {
    --bs-primary: 	#f5f5dc;
    --bs-link-color: #4dabf7;
    --bs-link-hover-color: #74c0fc;
}


/* ================== */
/* === 基本和通用 === */
/* ================== */
html, body {
  transition: background-color 0.3s ease, color 0.3s ease;
}

body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding-top: 70px; /* 导航栏高度补偿 */
  background-color: var(--bs-body-bg);
  color: var(--bs-body-color);
}

a {
  color: var(--bs-link-color);
  text-decoration: none;
}
a:hover {
  color: var(--bs-link-hover-color);
  text-decoration: underline;
}

.card {
    background-color: var(--card-bg);
    border-color: var(--bs-border-color);
    transition: background-color 0.3s ease, border-color 0.3s ease;
    opacity:0.8;
}

.btn-primary {
    --bs-btn-bg: var(--bs-primary);
    --bs-btn-border-color: var(--bs-primary);
    --bs-btn-hover-bg: color-mix(in srgb, var(--bs-primary) 85%, black);
    --bs-btn-hover-border-color: color-mix(in srgb, var(--bs-primary) 80%, black);
}

/* ================== */
/* ===   导航栏   === */
/* ================== */
.navbar {
    background-color: var(--navbar-bg) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--bs-border-color-translucent);
    transition: background-color 0.3s ease;
}
.navbar .navbar-brand { color: var(--bs-primary); font-weight: bold; }
.navbar .nav-link { color: var(--bs-body-color); }
.navbar .nav-link:hover, .navbar .nav-link:focus { color: var(--bs-primary); }
.navbar .dropdown-menu { background-color: var(--card-bg); border-color: var(--bs-border-color-translucent); }
.navbar .dropdown-item { color: var(--bs-body-color); }
.navbar .dropdown-item:hover, .navbar .dropdown-item:focus { background-color: var(--bs-tertiary-bg); color: var(--bs-body-color); }
.theme-toggle-button { background: none; border: none; color: var(--bs-body-color); font-size: 1.1rem; padding: 0.375rem 0.75rem; }
.theme-toggle-button:hover { color: var(--bs-primary); }

/* ================== */
/* ===   内容区   === */
/* ================== */
.main-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  padding-top: 1rem;
  padding-bottom: 2rem;
}

.flash-messages-container {
    position: sticky;
    top: 70px; /* 导航栏高度 + 一点间距 */
    z-index: 1050;
    width: 100%;
    max-width: 960px;
    margin-left: auto;
    margin-right: auto;
    pointer-events: none; /* 允许点击穿透 */
}
.flash-messages-container .alert {
    pointer-events: auto; /* 让 alert 可以被点击 */
}

/* --- 背景伪元素 --- */
.main-content::before,
.main-content::after {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  background-attachment: fixed;
  transition: opacity 0.6s ease-in-out; /* 稍长过渡 */
  opacity: 0;
  z-index: -1;
}
.main-content::before { background-image: var(--before-bg-image, none); }
.main-content::after { background-image: var(--after-bg-image, none); }
.main-content.js-bg-before-active::before { opacity: 1; }
.main-content.js-bg-after-active::after { opacity: 1; }

/* --- 文章列表和详情 --- */
.post-preview { max-height: 150px; overflow: hidden; color: var(--bs-secondary); }
.post-content { line-height: 1.7; font-size: 1.1rem; }
.post-content img, .post-content video, .post-content audio { max-width: 100%; height: auto; display: block; margin: 1rem auto; border-radius: 8px; box-shadow: 0 4px 8px var(--bs-border-color-translucent); }
.post-content blockquote { border-left: 5px solid var(--bs-tertiary-bg); padding-left: 1rem; margin-left: 0; color: var(--bs-secondary); font-style: italic; }
.post-content pre { background-color: var(--bs-tertiary-bg); padding: 1rem; border-radius: 5px; overflow-x: auto; }
.post-content code { font-size: 0.9em; color: var(--bs-danger); background-color: var(--bs-tertiary-bg); padding: 0.2em 0.4em; border-radius: 3px; }
.post-content pre code { color: inherit; background-color: transparent; padding: 0; }

/* ================== */
/* ===   评论区   === */
/* ================== */
#comments .card { background-color: color-mix(in srgb, var(--card-bg) 95%, transparent); }
#comments .comment-entry { border-left: 3px solid var(--bs-border-color); }
#comments .comment-entry .card-body { padding: 1rem; }
.reply-link { font-size: 0.85em; cursor: pointer; color: var(--bs-secondary); }
.reply-link:hover { color: var(--bs-primary); }

/* ================== */
/* ===   EasyMDE  === */
/* ================== */
.EasyMDEContainer { background-color: var(--card-bg); border-color: var(--bs-border-color) !important; }
.CodeMirror { background-color: var(--card-bg); color: var(--bs-body-color); border-color: var(--bs-border-color) !important; }
.editor-toolbar { background-color: var(--bs-tertiary-bg); border-color: var(--bs-border-color) !important; }
.editor-toolbar a { color: var(--bs-body-color) !important; }
.editor-toolbar a:hover, .editor-toolbar a.active { background-color: var(--bs-border-color); border-color: var(--bs-border-color) !important; }
.editor-preview, .editor-preview-side { background-color: var(--card-bg); border-color: var(--bs-border-color) !important; }

/* ================== */
/* ===   页脚     === */
/* ================== */
.footer { background-color: var(--footer-bg); color: var(--footer-text-color); transition: background-color 0.3s ease, color 0.3s ease; border-top: 1px solid var(--bs-border-color-translucent); }

/* ================== */
/* === 音乐播放器 === */
/* ================== */
#theme-music-player {
  position: fixed;
  bottom: 15px; right: 15px;
  border: none;
  width: 298px; height: 66px;
  z-index: 1000;
  display: none;
  opacity: 0.85;
  transition: opacity 0.3s ease, transform 0.3s ease;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}
#theme-music-player:hover { opacity: 1; transform: scale(1.02); }
js/theme.js
JavaScript

// D:/az/blog/My_blog/static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('themeToggle');
    if (!themeToggleButton) return;

    const sunIcon = '<i class="fas fa-sun"></i>';
    const moonIcon = '<i class="fas fa-moon"></i>';
    
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.setAttribute('data-bs-theme', theme);
        themeToggleButton.innerHTML = theme === 'dark' ? sunIcon : moonIcon;
        try { localStorage.setItem('theme', theme); } catch (e) {}
    };

    themeToggleButton.addEventListener('click', () => {
        const newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    });

    // 初始化时设置正确的图标
    const currentTheme = document.documentElement.getAttribute('data-theme');
    themeToggleButton.innerHTML = currentTheme === 'dark' ? sunIcon : moonIcon;
});

js/background_fade.js
JavaScript
// static/js/background_fade.js
const themeImageUrls = {
    light: "",
    dark: "url('https://s21.ax1x.com/2025/05/02/pEbG0XD.jpg')",
    blue: "url('https://s21.ax1x.com/2025/05/02/pEbGG79.jpg')",
    green: "url('https://s21.ax1x.com/2025/05/02/pEb1xnH.jpg')",
    yuan: "url('https://s21.ax1x.com/2025/05/02/pEbGlXF.jpg')"
};

const themeMusicUrls = {
    light: "",
    dark: "https://music.163.com/outchain/player?type=2&id=2034454236&auto=1&height=66",
    blue: "https://music.163.com/outchain/player?type=2&id=1961353401&auto=1&height=66",
    green: "https://music.163.com/outchain/player?type=2&id=1303019326&auto=0&height=66",
    yuan: "https://music.163.com/outchain/player?type=2&id=29732992&auto=1&height=66"
};

// --- 预加载图片 ---
function preloadBackgroundImages(urls) {
    Object.values(urls).forEach(url => {
        if (url && url.startsWith('url(')) {
            const imgUrl = url.match(/url\(['"]?(.*?)['"]?\)/)[1];
            if (imgUrl !== 'none' && !imgUrl.startsWith('/static/images/none')) { // 避免加载 'none'
                const img = new Image();
                img.src = imgUrl;
            }
        }
    });
}

function applyVisualBackgroundTheme() {
    const mainContent = document.getElementById('ajax-content-container');
    if (!mainContent) return;
    mainContent.classList.add('main-content');

    const currentTheme = mainContent.dataset.currentTheme || 'light';
    const previousTheme = sessionStorage.getItem('previous_theme_for_bg');
    const beforeImage = themeImageUrls[previousTheme] || 'none';
    const afterImage = themeImageUrls[currentTheme] || 'none';

    mainContent.style.setProperty('--before-bg-image', beforeImage);
    mainContent.style.setProperty('--after-bg-image', afterImage);
    mainContent.classList.remove('js-bg-before-active', 'js-bg-after-active');

    if (previousTheme && previousTheme !== currentTheme && beforeImage !== 'none' && afterImage !== 'none') {
        mainContent.classList.add('js-bg-before-active');
        setTimeout(() => {
            mainContent.classList.add('js-bg-after-active');
            mainContent.classList.remove('js-bg-before-active');
            mainContent.style.setProperty('--before-bg-image', afterImage);
        }, 600);
    } else {
        mainContent.classList.add('js-bg-after-active');
        mainContent.style.setProperty('--before-bg-image', afterImage);
    }

    handleThemeMusic(currentTheme);
    sessionStorage.setItem('previous_theme_for_bg', currentTheme);
}

function handleThemeMusic(theme) {
    const musicPlayer = document.getElementById('theme-music-player');
    if (!musicPlayer) return;

    const musicUrl = themeMusicUrls[theme] || "";
    const currentSrc = musicPlayer.getAttribute('src');

    // ************ 关键修改点 ************
    if (musicUrl !== currentSrc) {
        console.log(`音乐状态改变: ${currentSrc || '无'} -> ${musicUrl || '无'}`);
        musicPlayer.src = musicUrl;
    }
    // 根据是否有 URL 来决定显示或隐藏
    musicPlayer.style.display = musicUrl ? 'block' : 'none';
    // **************************************
}

// --- 初始化函数 ---
function initializePageElements() {
    const mainContent = document.getElementById('ajax-content-container');
    if (mainContent) {
        mainContent.classList.add('main-content');
        applyVisualBackgroundTheme(); // 应用背景
        // 初始加载时，也让 handleThemeMusic 检查一次
        handleThemeMusic(mainContent.dataset.currentTheme || 'light');
    }
}

// --- 事件监听 ---
document.addEventListener('DOMContentLoaded', () => {
    preloadBackgroundImages(themeImageUrls);
    initializePageElements();

    window.addEventListener('beforeunload', () => {
        const mainContent = document.getElementById('ajax-content-container');
        if (mainContent) {
             sessionStorage.setItem('previous_theme_for_bg', mainContent.dataset.currentTheme || 'light');
        }
    });
});

// --- 暴露给 navigation.js ---
window.reapplyVisualBackgroundTheme = initializePageElements; // AJAX 加载后调用这个

js/navigation.js
JavaScript

// static/js/navigation.js
document.addEventListener('DOMContentLoaded', () => {
    const ajaxContainerId = 'ajax-content-container';

    function loadPage(url, pushState = true) {
        console.log(`AJAX Loading: ${url}`);
        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => {
            if (!response.ok) { window.location.href = url; return Promise.reject(new Error('Network response was not ok.')); }
            return response.text();
        })
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const newContentContainer = doc.getElementById(ajaxContainerId);
            const newContent = newContentContainer ? newContentContainer.innerHTML : null;
            const newTitle = doc.title;

            if (!newContent) { console.error("Could not find AJAX container in fetched content."); window.location.href = url; return; }

            document.getElementById(ajaxContainerId).innerHTML = newContent;
            document.title = newTitle;

            if (pushState) { history.pushState({ path: url }, '', url); }

            const mainContent = document.getElementById(ajaxContainerId);
            if (newContentContainer && mainContent) {
                mainContent.dataset.currentTheme = newContentContainer.dataset.currentTheme || 'light';
            }

            if (window.reapplyVisualBackgroundTheme) { window.reapplyVisualBackgroundTheme(); }

            // 重新绑定链接，并重新初始化可能需要的 JS (如 EasyMDE)
            attachLinkListeners();
            // 如果新页面是 create_post 或 edit_post，需要重新初始化 EasyMDE
            // 这可以通过检查新内容中是否有 #body 元素来实现
            if (document.getElementById('body')) {
                // 这里需要调用一个函数来重新初始化 EasyMDE。
                // 这可能需要将 create_post.html/edit_post.html 中的 JS 封装成一个可重用的函数。
                // 简单起见，我们暂时不在 AJAX 中处理编辑器页面。
                console.log("Editor page loaded via AJAX - Manual refresh might be needed for full JS functionality.");
            }
            window.scrollTo(0, 0);
        })
        .catch(error => { console.error('AJAX load failed:', error); window.location.href = url; });
    }

    function attachLinkListeners() {
        document.querySelectorAll('a.internal-link').forEach(link => {
            link.removeEventListener('click', handleInternalLinkClick); // 移除旧的
            link.addEventListener('click', handleInternalLinkClick); // 添加新的
        });
    }

    function handleInternalLinkClick(event) {
        const link = event.currentTarget;
        if (link.target === '_blank' || event.ctrlKey || event.metaKey ||
            link.hostname !== window.location.hostname ||
            link.href.includes('/set-visual-theme/') || // 不拦截视觉主题切换
            link.pathname.includes('/logout') || // 不拦截登出
            link.closest('form')) { // 不拦截表单提交中的链接 (虽然通常不用)
            return;
        }
        // 不拦截创建和编辑页面的链接，因为 EasyMDE 初始化复杂
        if (link.pathname.includes('/create') || link.pathname.includes('/edit/')) {
             console.log("Navigating to editor page with full reload.");
             return;
        }
        event.preventDefault();
        loadPage(link.href);
    }

    attachLinkListeners();
    window.addEventListener('popstate', event => {
        if (event.state?.path) { loadPage(event.state.path, false); }
    });
});

js/theme.js
JavaScript
// static/js/theme.js
(function() {
    const htmlElement = document.documentElement;
    const themeToggleButton = document.getElementById('themeToggle');
    const sunIconClass = 'fas fa-sun';
    const moonIconClass = 'fas fa-moon';

    function applyTheme(theme) {
        document.documentElement.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        htmlElement.setAttribute('data-theme', theme);

        if (themeToggleButton) {
            if (theme === 'dark') {
                themeToggleButton.innerHTML = `<i class="${sunIconClass}"></i>`;
                themeToggleButton.setAttribute('title', '切换到浅色模式');
            } else {
                themeToggleButton.innerHTML = `<i class="${moonIconClass}"></i>`;
                themeToggleButton.setAttribute('title', '切换到深色模式');
            }
        }

        try {
            localStorage.setItem('theme', theme);
        } catch (e) {
            console.warn("LocalStorage 不可用。主题偏好将不会被保存。");
        }
    }

    // 初始主题设置
    const currentInitialTheme = htmlElement.getAttribute('data-theme') || 'light';
    if (themeToggleButton) {
        if (currentInitialTheme === 'dark') {
            themeToggleButton.innerHTML = `<i class="${sunIconClass}"></i>`;
            themeToggleButton.setAttribute('title', '切换到浅色模式');
        } else {
            themeToggleButton.innerHTML = `<i class="${moonIconClass}"></i>`;
            themeToggleButton.setAttribute('title', '切换到深色模式');
        }
    }

    // 主题切换按钮事件
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }

    // 系统主题变化监听
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        try {
            if (!localStorage.getItem('theme')) {
                applyTheme(e.matches ? 'dark' : 'light');
            }
        } catch (err) {}
    });
})();
<!doctype html>
<html lang="zh-CN"> {# JS 会在这里设置 data-theme 和 data-bs-theme #}
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title id="page-title">{{ title | default('我的博客') }} - 我的博客</title>

    <link rel="shortcut icon" href="{{ url_for('static', filename='favicon.ico') }}">
    <link rel="icon" type="image/png" sizes="32x32" href="{{ url_for('static', filename='favicon-32x32.png') }}"> {# 可选: 其他尺寸 #}
    <link rel="icon" type="image/png" sizes="16x16" href="{{ url_for('static', filename='favicon-16x16.png') }}"> {# 可选: 其他尺寸 #}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <link rel="stylesheet" href="https://unpkg.com/easymde/dist/easymde.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

    <script>
        (function() {
            const htmlElement = document.documentElement;
            let storedTheme;
            try { storedTheme = localStorage.getItem('theme'); } catch (e) {}
            const defaultTheme = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
            const currentTheme = storedTheme || defaultTheme;
            htmlElement.setAttribute('data-theme', currentTheme);
            htmlElement.setAttribute('data-bs-theme', currentTheme);
        })();
    </script>

    {% block head_extra %}{% endblock %}
</head>

<body>

    <nav class="navbar navbar-expand-lg fixed-top shadow-sm">
        <div class="container-fluid">
            <a class="navbar-brand internal-link" href="{{ url_for('main.index') }}">
                <i class="fas fa-feather-alt"></i> 我的博客
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link internal-link" href="{{ url_for('main.index') }}">首页</a>
                    </li>
                    <li class="nav-item">
                         {# 假设你有一个搜索路由 #}
                         {# <a class="nav-link internal-link" href="{{ url_for('main.search') }}">搜索</a> #}
                    </li>
                </ul>

                {# 右侧导航 #}
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0 align-items-center">
                    {% if current_user.is_authenticated %}
                        <li class="nav-item dropdown">
                            <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                <i class="fas fa-user"></i> {{ current_user.username }}
                            </a>
                            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                                <li><a class="dropdown-item internal-link" href="{{ url_for('auth.profile', username=current_user.username) }}">个人中心</a></li>
                                <li><a class="dropdown-item internal-link" href="{{ url_for('main.create_post') }}">创建文章</a></li>
                                <li><hr class="dropdown-divider"></li>
                                <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">退出登录</a></li>
                            </ul>
                        </li>
                    {% else %}
                        <li class="nav-item">
                            <a class="nav-link internal-link" href="{{ url_for('auth.login') }}">登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link internal-link" href="{{ url_for('auth.register') }}">注册</a>
                        </li>
                    {% endif %}

                    {# 视觉主题切换下拉菜单 #}
                    <li class="nav-item dropdown ms-lg-2">
                        <a class="nav-link dropdown-toggle" href="#" id="visualThemeDropdown" role="button" data-bs-toggle="dropdown" aria-expanded="false" title="切换视觉主题 (背景/音乐)">
                            <i class="fas fa-palette"></i>
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="visualThemeDropdown">
                            <li><a class="dropdown-item" href="{{ url_for('main.set_visual_theme', theme_name='light') }}">简约白 (Light)</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.set_visual_theme', theme_name='dark') }}">深邃黑 (Dark)</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.set_visual_theme', theme_name='blue') }}">宁静蓝 (Blue)</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.set_visual_theme', theme_name='green') }}">青春绿 (Green)</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.set_visual_theme', theme_name='yuan') }}">活力橙 (Yuan)</a></li>
                        </ul>
                    </li>

                    {% if g.is_admin %}
                    <li class="nav-item ms-lg-2">
                        <a class="nav-link internal-link" href="{{ url_for('admin.index') }}" title="管理后台">
                            <i class="fas fa-user-shield"></i>
                        </a>
                    </li>
                    {% endif %}

                    {# 颜色主题切换按钮 #}
                    <li class="nav-item ms-lg-2">
                        <button id="themeToggle" class="btn theme-toggle-button" title="切换颜色主题 (浅色/深色)">
                            <i class="fas fa-moon"></i>
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    {# 主内容区 #}
    <div id="ajax-content-container"
         class="main-content flex-grow-1"
         data-current-theme="{{ g.current_theme_for_background_fade | default('light') }}">

        {# Flash 消息 #}
        <div class="container flash-messages-container">
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category or 'info' }} alert-dismissible fade show mt-2" role="alert">
                            {{ message }}
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
        </div>

        {# 子模板内容 #}
        {% block content %}{% endblock %}
    </div>

    {# 页脚 #}
    <footer class="footer mt-auto py-3">
      <div class="container text-center">
        <span class="text-muted">&copy; {{ g.current_year | default('2025') }} 我的博客.</span>
      </div>
    </footer>

    {# 音乐播放器 iframe #}
    <iframe id="theme-music-player"
            frameborder="no" border="0" marginwidth="0" marginheight="0"
            width="298" height="66" src=""
            style="display:none; position: fixed; bottom: 15px; right: 15px; z-index: 1000; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);"
            allow="autoplay; encrypted-media">
    </iframe>

    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.8/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.min.js"></script>
    <script src="https://unpkg.com/easymde/dist/easymde.min.js"></script>
    <script src="{{ url_for('static', filename='js/theme.js') }}"></script>
    <script src="{{ url_for('static', filename='js/background_fade.js') }}"></script>
    <script src="{{ url_for('static', filename='js/navigation.js') }}"></script>

    {% block scripts %}{% endblock %}
</body>
</html>

[Uploading create_post.html…](){# D:\az\blog\My_blog\templates\create_post.html #}
{% extends "base.html" %}

{% block title %}创建新文章 - 我的博客{% endblock %}

{% block head_extra %}
<style>
    .EasyMDEContainer { border-color: var(--bs-border-color); }
    .CodeMirror { background-color: var(--bs-body-bg); color: var(--bs-body-color); border-color: var(--bs-border-color); }
    .editor-toolbar { background-color: var(--bs-tertiary-bg); border-color: var(--bs-border-color); }
    .editor-toolbar a { color: var(--bs-body-color) !important; }
    .editor-preview, .editor-preview-side { background-color: var(--bs-body-bg); }
</style>
{% endblock %}

{% block content %}
<div id="main-content-wrapper" class="container mt-4 mb-5">
    <div class="card shadow-sm">
        <div class="card-body">
            <h2 class="card-title">创建新文章</h2>
            <hr>
            {# 显示 Flash 消息 #}
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                {% for category, message in messages %}
                  <div class="alert alert-{{ category or 'info' }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                  </div>
                {% endfor %}
              {% endif %}
            {% endwith %}

            <form method="POST" action="{{ url_for('main.create_post') }}" id="post-form">
                <div class="mb-3">
                    <label for="title" class="form-label">标题</label>
                    <input type="text" class="form-control" id="title" name="title" value="{{ title_data or '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">分类 (可选)</label>
                    <input type="text" class="form-control" id="category" name="category" value="{{ category_data or '' }}" placeholder="例如: 技术, 生活">
                </div>
                <div class="mb-3">
                    <label for="tags" class="form-label">标签 (用逗号分隔, 可选)</label>
                    <input type="text" class="form-control" id="tags" name="tags" value="{{ tags_data or '' }}" placeholder="例如: Flask, Python">
                </div>
                <div class="mb-3">
                    <label for="body" class="form-label">内容 (支持 Markdown)</label>
                    {# 使用上次提供的值填充，防止因 Flash 刷新丢失内容 #}
                    <textarea class="form-control" id="body" name="body" rows="15" >{{ body_data or '' }}</textarea>
                </div>
                <button type="submit" class="btn btn-primary"><i class="fas fa-paper-plane"></i> 发布文章</button>
                <a href="{{ url_for('main.index') }}" class="btn btn-secondary ms-2 internal-link"><i class="fas fa-times"></i> 取消</a>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof EasyMDE !== 'undefined') {
        var easyMDE = new EasyMDE({
            element: document.getElementById("body"),
            spellChecker: false,
            autosave: { enabled: true, uniqueId: "create_post_{{ current_user.id if current_user.is_authenticated else 'anon' }}", delay: 2000 },
            toolbar: [ "bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link",
                { name: "image", action: function(editor) { selectAndUploadFile(editor, 'image'); }, className: "fa fa-image", title: "上传图片" },
                { name: "video", action: function(editor) { selectAndUploadFile(editor, 'video'); }, className: "fa fa-video", title: "上传视频" },
                "|", "preview", "side-by-side", "fullscreen", "|", "guide" ],
        });

        function selectAndUploadFile(editor, type) {
            var input = document.createElement('input');
            input.type = 'file';
            input.accept = type === 'image' ? 'image/png, image/jpeg, image/gif' : 'video/mp4, video/webm, video/ogg';
            input.onchange = e => {
                var file = e.target.files[0];
                if (file) { uploadFile(file, editor, type); }
            }
            input.click();
        }

        function uploadFile(file, editor, type) {
            var formData = new FormData();
            formData.append('file', file);
            var cm = editor.codemirror;
            var doc = cm.getDoc();
            var cursor = doc.getCursor();
            var placeholderText = `\n[上传中: ${file.name}...]\n`;
            doc.replaceRange(placeholderText, cursor);

            fetch("{{ url_for('main.upload_file') }}", { method: 'POST', body: formData })
            .then(response => {
                if (!response.ok) { return response.json().then(err => { throw new Error(err.error || `HTTP ${response.status}`); }); }
                return response.json();
            })
            .then(data => {
                let output = '';
                if (data.url) {
                    output = type === 'image' ? `![${file.name}](${data.url})\n` : `\n<video width="100%" controls>\n  <source src="${data.url}" type="${file.type}">\n  您的浏览器不支持视频标签。\n</video>\n`;
                } else {
                    alert('上传失败: ' + (data.error || '未知错误'));
                }
                var currentContent = doc.getValue();
                var placeholderIndex = currentContent.indexOf(placeholderText);
                if (placeholderIndex > -1) {
                    doc.replaceRange(output, doc.posFromIndex(placeholderIndex), doc.posFromIndex(placeholderIndex + placeholderText.length));
                } else {
                    doc.replaceRange(output, cursor);
                }
            })
            .catch(error => {
                alert('上传发生错误: ' + error.message);
                var currentContent = doc.getValue();
                var placeholderIndex = currentContent.indexOf(placeholderText);
                if (placeholderIndex > -1) {
                    doc.replaceRange('', doc.posFromIndex(placeholderIndex), doc.posFromIndex(placeholderIndex + placeholderText.length));
                }
                console.error('上传错误:', error);
            });
        }
    } else { console.error("EasyMDE 未加载!"); }
});
</script>
{% endblock %}

[Uploading edit_post.html…](){% extends "base.html" %}

{% block title %}编辑文章 - {{ post.title }} - 我的博客{% endblock %}

{% block head_extra %}
<style>
    /* 与 create_post.html 相同的 EasyMDE 样式 */
    .EasyMDEContainer {
        border-color: var(--bs-border-color);
    }
    .CodeMirror {
        background-color: var(--bs-body-bg);
        color: var(--bs-body-color);
        border-color: var(--bs-border-color);
    }
    .editor-toolbar {
        background-color: var(--bs-tertiary-bg);
        border-color: var(--bs-border-color);
    }
     .editor-toolbar a {
        color: var(--bs-body-color) !important;
    }
    .editor-preview, .editor-preview-side {
        background-color: var(--bs-body-bg);
    }
</style>
{% endblock %}


{% block content %}
<div id="main-content-wrapper" class="container mt-4 mb-5">
    <div class="card shadow-sm">
        <div class="card-body">
            <h2 class="card-title">编辑文章</h2>
            <hr>
            {# ... (Flash 消息) ... #}
            <form method="POST" action="{{ url_for('main.edit_post', slug=post.slug) }}" id="post-form">
                {# ... (表单字段保持不变) ... #}
                <div class="mb-3">
                    <label for="title" class="form-label">标题</label>
                    <input type="text" class="form-control" id="title" name="title"
                           value="{{ post.title }}" required>
                </div>
                <div class="mb-3">
                    <label for="category" class="form-label">分类 (可选)</label>
                    <input type="text" class="form-control" id="category" name="category"
                           value="{{ post.category.name if post.category else '' }}">
                </div>
                <div class="mb-3">
                    <label for="tags" class="form-label">标签 (用逗号分隔, 可选)</label>
                    <input type="text" class="form-control" id="tags" name="tags"
                           value="{{ existing_tags }}">
                </div>
                <div class="mb-3">
                    <label for="body" class="form-label">内容 (支持 Markdown)</label>
                    <textarea class="form-control" id="body" name="body" rows="15" >{{ post.body }}</textarea>
                </div>

                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-save"></i> 保存更改
                </button>
                <a href="{{ url_for('main.post', slug=post.slug) }}" class="btn btn-secondary ms-2 internal-link">
                     <i class="fas fa-times"></i> 取消
                </a>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
{{ super() }}
<script>
document.addEventListener('DOMContentLoaded', function() {
    if (typeof EasyMDE !== 'undefined') {
        var easyMDE = new EasyMDE({
            element: document.getElementById("body"),
            spellChecker: false,
            autosave: { enabled: true, uniqueId: "edit_post_{{ post.id }}", delay: 2000, },
            placeholder: "在这里继续写作...",
            status: ["autosave", "lines", "words", "cursor"],
            toolbar:  [ "bold", "italic", "heading", "|", "quote", "unordered-list", "ordered-list", "|", "link",
                { name: "image", action: function(editor) { selectAndUploadFile(editor, 'image'); }, className: "fa fa-image", title: "上传图片" },
                { name: "video", action: function(editor) { selectAndUploadFile(editor, 'video'); }, className: "fa fa-video", title: "上传视频" },
                "|", "preview", "side-by-side", "fullscreen", "|", "guide" ],
        });

        function selectAndUploadFile(editor, type) { var input = document.createElement('input');
            input.type = 'file';
            input.accept = type === 'image' ? 'image/png, image/jpeg, image/gif' : 'video/mp4, video/webm, video/ogg';
            input.onchange = e => {
                var file = e.target.files[0];
                if (file) { uploadFile(file, editor, type); }
            }
            input.click(); }

        // ************ 关键修改点: 使用新的 uploadFile ************
        function uploadFile(file, editor, type) {
            var formData = new FormData();
            formData.append('file', file);
            var cm = editor.codemirror;
            var doc = cm.getDoc();
            var cursor = doc.getCursor();
            var placeholderText = `\n[上传中: ${file.name}...]\n`;
            doc.replaceRange(placeholderText, cursor);

            fetch("{{ url_for('main.upload_file') }}", { method: 'POST', body: formData, })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || `HTTP ${response.status}`); });
                }
                return response.json();
            })
            .then(data => {
                let output = '';
                if (data.url) {
                    if (type === 'image') {
                        output = `![${file.name}](${data.url})\n`;
                    } else {
                        output = `\n<video width="100%" controls>\n  <source src="${data.url}" type="${file.type}">\n  您的浏览器不支持视频标签。\n</video>\n`;
                    }
                } else {
                    alert('上传失败: ' + (data.error || '未知错误'));
                    output = '';
                }
                var currentContent = doc.getValue();
                var placeholderIndex = currentContent.indexOf(placeholderText);
                if (placeholderIndex > -1) {
                    var startPos = doc.posFromIndex(placeholderIndex);
                    var endPos = doc.posFromIndex(placeholderIndex + placeholderText.length);
                    doc.replaceRange(output, startPos, endPos);
                } else {
                    console.warn("未找到占位符，将在原始光标处插入。");
                    doc.replaceRange(output, cursor);
                }
            })
            .catch(error => {
                alert('上传发生错误: ' + error.message);
                var currentContent = doc.getValue();
                var placeholderIndex = currentContent.indexOf(placeholderText);
                if (placeholderIndex > -1) {
                    var startPos = doc.posFromIndex(placeholderIndex);
                    var endPos = doc.posFromIndex(placeholderIndex + placeholderText.length);
                    doc.replaceRange('', startPos, endPos);
                }
                console.error('上传错误:', error);
            });
        }
        // *******************************************************
    } else {
        console.error("EasyMDE 未能加载!");
    }
});
</script>
{% endblock %}

[Uploading edit_profile.html…](){% extends "base.html" %}

{% block title %}编辑资料 - 我的博客{% endblock %}

{% block content %}
<div class="container mt-4">
    <h2>编辑资料</h2>
    <hr>
    <form method="POST" action="{{ url_for('auth.edit_profile') }}">
        <div class="mb-3">
            <label for="username" class="form-label">用户名</label>
            <input type="text" class="form-control" id="username" name="username" 
                   value="{{ user.username }}" required>
        </div>
        <div class="mb-3">
            <label for="about_me" class="form-label">个人简介</label>
            <textarea class="form-control" id="about_me" name="about_me" 
                      rows="3">{{ user.about_me or '' }}</textarea>
        </div>
        <button type="submit" class="btn btn-primary">保存更改</button>
        <a href="{{ url_for('auth.profile', username=user.username) }}" class="btn btn-secondary ms-2">取消</a>
    </form>
</div>
{% endblock %}

[Uploading index.html…](){% extends "base.html" %}

{% block title %}首页 - 我的博客{% endblock %}

{% block content %}
<div id="main-content-wrapper" class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h1>博客文章</h1>
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('main.create_post') }}" class="btn btn-primary internal-link">
                <i class="fas fa-plus"></i> 创建新文章
            </a>
        {% endif %}
    </div>
    <hr>
    {% for post_item in posts %}
        <article class="mb-4 card shadow-sm">
            <div class="card-body">
                <h2 class="card-title"><a href="{{ url_for('main.post', slug=post_item.slug) }}" class="internal-link">{{ post_item.title }}</a></h2>
                <p class="card-subtitle mb-2 text-muted small">
                    作者：<a href="{{ url_for('auth.profile', username=post_item.author.username) }}" class="internal-link">{{ post_item.author.username }}</a> 发表于 {{ post_item.timestamp.strftime('%Y-%m-%d %H:%M') }}
                </p>
                <div class="card-text post-preview">
                    {# 使用 body_html 的摘要会更好，但需要后端处理，暂时用 body #}
                    {{ post_item.body[:200] | striptags }}{% if post_item.body|length > 200 %}...{% endif %}
                </div>
                <a href="{{ url_for('main.post', slug=post_item.slug) }}" class="btn btn-outline-primary btn-sm mt-2 internal-link">阅读更多 &rarr;</a>
                {% if current_user.is_authenticated and (post_item.author == current_user or g.is_admin) %}
                <a href="{{ url_for('main.edit_post', slug=post_item.slug) }}" class="btn btn-outline-secondary btn-sm mt-2 ms-1 internal-link">编辑</a>
                <form action="{{ url_for('main.delete_post', slug=post_item.slug) }}" method="POST" style="display:inline;" class="ms-1">
                    <input type="submit" value="删除" class="btn btn-outline-danger btn-sm mt-2" onclick="return confirm('您确定要删除这篇文章吗？');">
                </form>
                {% endif %}
            </div>
        </article>
    {% else %}
        <p>暂无文章。{% if current_user.is_authenticated %}<a href="{{url_for('main.create_post')}}" class="internal-link">成为第一个创建文章的人！</a>{% endif %}</p>
    {% endfor %}

    {# 分页 (使用 pagination 对象) #}
    {% if pagination and (pagination.has_prev or pagination.has_next) %}
    <nav aria-label="Page navigation">
        <ul class="pagination justify-content-center">
            <li class="page-item {{ 'disabled' if not pagination.has_prev }}">
                <a class="page-link internal-link" href="{{ url_for('main.index', page=pagination.prev_num) if pagination.has_prev else '#' }}">上一页</a>
            </li>
            {% for page_num in pagination.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                {% if page_num %}
                    <li class="page-item {{ 'active' if pagination.page == page_num }}"><a class="page-link internal-link" href="{{ url_for('main.index', page=page_num) }}">{{ page_num }}</a></li>
                {% else %}
                    <li class="page-item disabled"><span class="page-link">...</span></li>
                {% endif %}
            {% endfor %}
            <li class="page-item {{ 'disabled' if not pagination.has_next }}">
                <a class="page-link internal-link" href="{{ url_for('main.index', page=pagination.next_num) if pagination.has_next else '#' }}">下一页</a>
            </li>
        </ul>
    </nav>
    {% endif %}

</div>
{% endblock %}

[Uploading login.html…](){% extends "base.html" %}

{% block title %}登录 - 我的博客{% endblock %}

{% block content %}
<div class="login-wrapper">
    <div class="login-card">
        <h2 class="text-center mb-4">登录</h2>
        <form method="POST" action="{{ url_for('auth.login') }}">
            <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <div class="mb-3 form-check">
                <input type="checkbox" class="form-check-input" id="remember_me" name="remember_me">
                <label class="form-check-label" for="remember_me">记住我</label>
            </div>
            <button type="submit" class="btn btn-primary w-100">登录</button>
        </form>
        <hr>
        <p class="text-center">还没有账号？<a href="{{ url_for('auth.register') }}" class="internal-link">立即注册</a></p>
    </div>
</div>
{% endblock %}

[Uploading post.html…](){% extends "base.html" %}

{% block title %}{{ post.title }} - 我的博客{% endblock %}

{% block content %}
<div id="main-content-wrapper" class="container mt-4"> {# 这个 div 是可选的，但可以帮助组织内容 #}
    <div class="card shadow-sm mb-4">
        <div class="card-body">
            <article class="post-detail">
                <h1 class="card-title">{{ post.title }}</h1>
                <p class="card-subtitle text-muted small mb-2">
                    作者: <a href="{{ url_for('auth.profile', username=post.author.username) }}" class="internal-link">{{ post.author.username }}</a> |
                    发布于: {{ post.timestamp.strftime('%Y-%m-%d %H:%M') }}
                    {% if post.category %}
                    | 分类: <a href="#" class="text-decoration-none internal-link">{{ post.category.name }}</a>
                    {% endif %}
                </p>

                {% if post.tags %}
                <div class="mb-3">
                    {% for tag in post.tags %}
                    <span class="badge rounded-pill bg-secondary me-1">{{ tag.name }}</span>
                    {% endfor %}
                </div>
                {% endif %}

                <hr>

                {# ************ 关键修改点 ************ #}
                <div class="post-content">
                    {{ post.body_html | safe }}
                </div>
                {# ************************************** #}

                {# 编辑/删除按钮 #}
                {% if current_user.is_authenticated and (post.author == current_user or g.is_admin) %}
                <div class="mt-4 border-top pt-3">
                    <a href="{{ url_for('main.edit_post', slug=post.slug) }}" class="btn btn-outline-secondary btn-sm internal-link">
                        <i class="fas fa-edit"></i> 编辑
                    </a>
                    <form action="{{ url_for('main.delete_post', slug=post.slug) }}" method="POST" class="d-inline ms-1">
                        <button type="submit" class="btn btn-outline-danger btn-sm" onclick="return confirm('确定要删除这篇文章吗？')">
                            <i class="fas fa-trash"></i> 删除
                        </button>
                    </form>
                </div>
                {% endif %}
            </article>
        </div>
    </div>

    {# 评论区 #}
    <section id="comments" class="card shadow-sm mb-4">
        <div class="card-body">
            <h3 class="card-title">评论 ({{ post.comments.count() }})</h3>
            <hr>
            {% if current_user.is_authenticated %}
            <form method="POST" action="{{ url_for('main.add_comment', slug=post.slug) }}" class="mb-4" id="comment-form">
                <div class="mb-3">
                    <label for="comment-body" class="form-label">发表评论</label>
                    <textarea class="form-control" id="comment-body" name="body" rows="3" placeholder="写下你的评论..." required></textarea>
                </div>
                <input type="hidden" name="parent_id" id="comment-parent-id" value="">
                <button type="submit" class="btn btn-primary">提交评论</button>
                <button type="button" class="btn btn-secondary btn-sm ms-2" id="cancel-reply-btn" style="display:none;">取消回复</button>
            </form>
            {% else %}
            <p><a href="{{ url_for('auth.login', next=request.url) }}" class="internal-link">登录</a>后发表评论</p>
            {% endif %}

            {# 评论列表 #}
            {% for comment in comments %}
                {% if not comment.parent %} {# 只显示顶级评论，回复在 JS 中处理或递归渲染 #}
                <div class="card mb-3 comment-entry" id="comment-{{ comment.id }}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                             <div class="d-flex">
                                 {# <img src="{{ comment.author.avatar_url or url_for('static', filename='images/default-avatar.png') }}" alt="{{ comment.author.username }}" class="rounded-circle me-2" width="32" height="32"> #}
                                 <div>
                                    <h6 class="card-subtitle mb-1 text-muted">
                                        <a href="{{ url_for('auth.profile', username=comment.author.username) }}" class="internal-link fw-bold">{{ comment.author.username }}</a>
                                    </h6>
                                    <p class="card-text mb-1">{{ comment.body }}</p>
                                    <small class="text-muted d-block">
                                        {{ comment.timestamp.strftime('%Y-%m-%d %H:%M') }}
                                        {% if current_user.is_authenticated %}
                                            <a href="#comment-form" class="reply-link ms-2" data-comment-id="{{ comment.id }}" data-comment-author="{{ comment.author.username }}">回复</a>
                                        {% endif %}
                                    </small>
                                </div>
                            </div>
                        </div>

                        {# 渲染回复 #}
                        {% for reply in comment.replies %}
                        <div class="card mt-3 ms-4 comment-entry" id="comment-{{ reply.id }}">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start">
                                     <div class="d-flex">
                                         {# <img src="{{ reply.author.avatar_url or url_for('static', filename='images/default-avatar.png') }}" alt="{{ reply.author.username }}" class="rounded-circle me-2" width="32" height="32"> #}
                                         <div>
                                            <h6 class="card-subtitle mb-1 text-muted">
                                                <a href="{{ url_for('auth.profile', username=reply.author.username) }}" class="internal-link fw-bold">{{ reply.author.username }}</a>
                                                <span class="fw-normal"> 回复 </span>
                                                <a href="#comment-{{ reply.parent_id }}" class="internal-link fw-bold">{{ reply.parent.author.username }}</a>
                                            </h6>
                                            <p class="card-text mb-1">{{ reply.body }}</p>
                                            <small class="text-muted d-block">
                                                {{ reply.timestamp.strftime('%Y-%m-%d %H:%M') }}
                                                {% if current_user.is_authenticated %}
                                                    <a href="#comment-form" class="reply-link ms-2" data-comment-id="{{ reply.id }}" data-comment-author="{{ reply.author.username }}">回复</a>
                                                {% endif %}
                                            </small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endif %}
            {% else %}
            <p>还没有评论，快来抢沙发吧！</p>
            {% endfor %}

            {# 评论分页 #}
            {% if pagination and (pagination.has_prev or pagination.has_next) %}
            <nav aria-label="Comment navigation" class="mt-4">
                <ul class="pagination justify-content-center">
                    <li class="page-item {{ 'disabled' if not pagination.has_prev }}">
                        <a class="page-link internal-link" href="{{ url_for('main.post', slug=post.slug, page=pagination.prev_num) if pagination.has_prev else '#' }}">上一页</a>
                    </li>
                    {% for page_num in pagination.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                        {% if page_num %}
                            <li class="page-item {{ 'active' if pagination.page == page_num }}"><a class="page-link internal-link" href="{{ url_for('main.post', slug=post.slug, page=page_num) }}">{{ page_num }}</a></li>
                        {% else %}
                            <li class="page-item disabled"><span class="page-link">...</span></li>
                        {% endif %}
                    {% endfor %}
                    <li class="page-item {{ 'disabled' if not pagination.has_next }}">
                        <a class="page-link internal-link" href="{{ url_for('main.post', slug=post.slug, page=pagination.next_num) if pagination.has_next else '#' }}">下一页</a>
                    </li>
                </ul>
            </nav>
            {% endif %}
        </div>
    </section>
</div>
{% endblock %}

{% block scripts %}
{{ super() }} {# 调用父模板的 scripts 块 #}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');
    if (commentForm) {
        const parentIdInput = document.getElementById('comment-parent-id');
        const commentTextarea = commentForm.querySelector('textarea[name="body"]');
        const cancelReplyBtn = document.getElementById('cancel-reply-btn');
        const commentBodyLabel = commentForm.querySelector('label[for="comment-body"]');

        document.querySelectorAll('.reply-link').forEach(link => {
            link.addEventListener('click', function(event) {
                event.preventDefault(); // 阻止默认跳转行为
                const commentId = this.dataset.commentId;
                const commentAuthor = this.dataset.commentAuthor;

                parentIdInput.value = commentId; // 设置要回复的评论ID
                commentBodyLabel.textContent = '回复 ' + commentAuthor + ':'; // 更新标签
                commentTextarea.focus(); // 聚焦文本框
                cancelReplyBtn.style.display = 'inline-block'; // 显示取消按钮

                // 平滑滚动到评论框
                commentForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        });

        if (cancelReplyBtn) {
            cancelReplyBtn.addEventListener('click', function() {
                parentIdInput.value = ''; // 清空回复ID
                commentBodyLabel.textContent = '发表评论'; // 恢复标签
                commentTextarea.placeholder = '写下你的评论...'; // 恢复占位符
                this.style.display = 'none'; // 隐藏取消按钮
            });
        }
    }
});
</script>
{% endblock %}

[Uploading profile.html…](){% extends "base.html" %}
{% block title %}{{ user.username }}的资料{% endblock %}

{% block content %}
<div id="main-content-wrapper" class="main-content container mt-4" data-current-theme="{{ g.current_theme_for_background_fade | default('light') }}">
    <div class="profile-container">
        <div class="row">
            <div class="col-md-3">
                <div class="card shadow-sm mb-3">
                    <div class="card-body text-center">
                        <img src="{{ url_for('static', filename='images/default-avatar.png') }}"
                             alt="{{ user.username }}的头像" class="rounded-circle mb-3" width="150" height="150"
                             style="border: 3px solid var(--bs-primary-border-subtle);">
                        <h3>{{ user.username }}</h3>
                        <p class="text-muted small">注册于: {{ user.member_since.strftime('%Y年%m月%d日') }}</p>
                        {% if user.about_me %}
                            <p class="text-muted small"><em>"{{ user.about_me }}"</em></p>
                        {% endif %}
                        {% if current_user == user %}
                        <a href="{{ url_for('auth.edit_profile') }}" class="btn btn-outline-primary btn-sm internal-link">编辑资料</a>
                        {% endif %}
                    </div>
                </div>
            </div>
            <div class="col-md-9">
                <h4>{{ user.username }} 的文章 ({{ pagination.total or posts|length }})</h4>
                <hr>
                {% if posts %}
                    {% for post_item in posts %}
                        <article class="mb-4 card shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title"><a href="{{ url_for('main.post', slug=post_item.slug) }}" class="internal-link">{{ post_item.title }}</a></h5>
                                <p class="card-subtitle mb-2 text-muted small">
                                    发表于 {{ post_item.timestamp.strftime('%Y-%m-%d %H:%M') }}
                                    {% if post_item.category %}
                                    | 分类: <a href="#" class="text-decoration-none">{{ post_item.category.name }}</a> {# TODO: Add category link #}
                                    {% endif %}
                                </p>
                                <div class="card-text post-preview mb-2">
                                    {{ post_item.body[:150] | striptags }}{% if post_item.body|length > 150 %}...{% endif %}
                                </div>
                                <a href="{{ url_for('main.post', slug=post_item.slug) }}" class="btn btn-sm btn-outline-secondary internal-link">阅读更多 &rarr;</a>
                            </div>
                        </article>
                    {% endfor %}
                {% else %}
                    <p>该用户还没有发表任何文章。</p>
                {% endif %}

                {# 用户文章的分页 #}
                {% if pagination and (pagination.has_prev or pagination.has_next) %}
                <nav aria-label="User posts navigation">
                    <ul class="pagination justify-content-center mt-4">
                        {% if pagination.has_prev %}
                            <li class="page-item"><a class="page-link internal-link" href="{{ url_for('auth.profile', username=user.username, page=pagination.prev_num) }}">上一页</a></li>
                        {% else %}
                            <li class="page-item disabled"><span class="page-link">上一页</span></li>
                        {% endif %}
                        {% for page_num in pagination.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
                            {% if page_num %}
                                {% if pagination.page == page_num %}
                                <li class="page-item active" aria-current="page"><span class="page-link">{{ page_num }}</span></li>
                                {% else %}
                                <li class="page-item"><a class="page-link internal-link" href="{{ url_for('auth.profile', username=user.username, page=page_num) }}">{{ page_num }}</a></li>
                                {% endif %}
                            {% else %}
                                <li class="page-item disabled"><span class="page-link">...</span></li>
                            {% endif %}
                        {% endfor %}
                        {% if pagination.has_next %}
                            <li class="page-item"><a class="page-link internal-link" href="{{ url_for('auth.profile', username=user.username, page=pagination.next_num) }}">下一页</a></li>
                        {% else %}
                            <li class="page-item disabled"><span class="page-link">下一页</span></li>
                        {% endif %}
                    </ul>
                </nav>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}

[Uploading register.html…](){% extends "base.html" %}

{% block title %}注册 - 我的博客{% endblock %}
{% block content %}
<div class="login-wrapper">
    <div class="login-card">
        <h2 class="text-center mb-4">注册</h2>
        <form method="POST" action="{{ url_for('auth.register') }}">
            <div class="mb-3">
                <label for="username" class="form-label">用户名</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">邮箱</label>
                <input type="email" class="form-control" id="email" name="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">密码</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <div class="mb-3">
                <label for="password2" class="form-label">确认密码</label>
                <input type="password" class="form-control" id="password2" name="password2" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">注册</button>
        </form>
        <hr>
        <p class="text-center">已有账号？<a href="{{ url_for('auth.login') }}" class="internal-link">立即登录</a></p>
    </div>
</div>
{% endblock %}
