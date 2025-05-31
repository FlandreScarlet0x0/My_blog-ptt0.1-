
#### `config.py`

应用的配置类。

```python
import os

# 获取项目根目录 (D:\az\blog)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_super_secret_key_that_is_long_and_random'

    # 数据库配置，指向 instance 文件夹
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(project_root, 'instance', 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 分页配置
    POSTS_PER_PAGE = 5
    COMMENTS_PER_PAGE = 10

    # 文件上传配置
    UPLOADED_MEDIA_DEST = os.path.join(project_root, 'My_blog', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Whooshee 全文搜索
    WHOOSHEE_MIN_STRING_LEN = 1
```

#### `extensions.py`

集中管理 Flask 扩展实例。

```python
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

# 指定未登录时跳转的视图
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录以访问此页面。'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    # 需要在这里导入 User 模型以避免循环依赖
    from .models import User
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            abort(403) # Forbidden
        return f(*args, **kwargs)
    return decorated_function
```

#### `models.py`

定义数据库模型。

```python
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import re
from .extensions import db, whooshee
import markdown
import bleach

# 文章和标签的多对多关联表
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

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade='all, delete-orphan')
    def __repr__(self): return f'<Comment {self.body[:20]}...>'

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
                        'h1', 'h2', 'h3', 'p', 'img', 'video', 'source', 'audio', 'br', 'hr']
        allowed_attrs = {'*': ['class'], 'a': ['href', 'title'],
                         'img': ['src', 'alt', 'title', 'width', 'height', 'style'],
                         'video': ['src', 'controls', 'width', 'height', 'poster', 'style'],
                         'source': ['src', 'type'], 'audio': ['src', 'controls']}
        html = markdown.markdown(value, output_format='html', extensions=['fenced_code', 'tables', 'attr_list'])
        target.body_html = bleach.linkify(bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
```

#### `routes/main.py`

处理核心功能（首页、文章页、创建、编辑、上传等）的路由。

```python
from flask import (render_template, Blueprint, request, redirect, url_for,
                   flash, current_app, g, session, jsonify, send_from_directory)
from werkzeug.utils import secure_filename
from ..models import db, Post, Comment, Category, Tag
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
    try:
        return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except FileNotFoundError:
        return '', 204

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
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOADED_MEDIA_DEST']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        base, ext = os.path.splitext(filepath)
        counter = 1
        while os.path.exists(filepath):
            filepath = f"{base}_{counter}{ext}"
            filename = f"{os.path.basename(base)}_{counter}{ext}"
            counter += 1
        try:
            file.save(filepath)
            file_url = url_for('static', filename=f'uploads/{filename}', _external=False)
            return jsonify({'url': file_url})
        except Exception as e:
            current_app.logger.error(f"File save error: {e}")
            return jsonify({'error': f'Could not save file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@bp.route('/post/<slug>')
def post(slug):
    post_instance = Post.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    comments_per_page = current_app.config.get('COMMENTS_PER_PAGE', 10)
    comments_pagination = post_instance.comments.filter(Comment.parent_id == None).order_by(Comment.timestamp.asc()).paginate(page=page, per_page=comments_per_page, error_out=False)
    comments = comments_pagination.items
    return render_template('post.html', title=post_instance.title, post=post_instance, comments=comments, pagination=comments_pagination)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        category_name = request.form.get('category')
        tag_names_str = request.form.get('tags', '')
        if not title or not body:
            flash('标题和内容不能为空！', 'danger')
            return render_template('create_post.html', title='创建新文章', title_data=title, body_data=body, category_data=category_name, tags_data=tag_names_str)
        category = None
        if category_name and category_name.strip():
            category_name = category_name.strip()
            category = Category.query.filter_by(name=category_name).first()
            if not category: category = Category(name=category_name); db.session.add(category)
        new_post = Post(title=title, body=body, author=current_user, category=category); new_post.generate_slug()
        if tag_names_str:
            tag_names = [name.strip() for name in tag_names_str.split(',') if name.strip()]
            for tag_name in tag_names:
                tag = Tag.query.filter_by(name=tag_name).first()
                if not tag: tag = Tag(name=tag_name); db.session.add(tag)
                if tag not in new_post.tags: new_post.tags.append(tag)
        db.session.add(new_post)
        try:
            db.session.commit()
            flash('文章创建成功！', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建文章失败: {e}")
            flash(f'创建文章失败，请检查日志。', 'danger')
            return render_template('create_post.html', title='创建新文章', title_data=title, body_data=body, category_data=category_name, tags_data=tag_names_str)
    return render_template('create_post.html', title='创建新文章')

# ... 其他路由 (edit, delete, comment, search) ...
```
# Static Files (D:\az\blog\My_blog\static)

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
