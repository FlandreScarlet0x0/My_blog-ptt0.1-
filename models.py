# My_blog/models.py
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


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self): return f'<Comment {self.body[:20]}...>'


@whooshee.register_model('title', 'body')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    body = db.Column(db.Text, nullable=False)

    # ************ 关键修改点 ************
    body_html = db.Column(db.Text)  # 添加此字段
    # **************************************

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    slug = db.Column(db.String(200), unique=True, index=True, nullable=False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")  # 确保 backref 正确
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f'<Post {self.title}>'

    def generate_slug(self, title_to_slug=None):
        if not title_to_slug: title_to_slug = self.title
        s = title_to_slug.lower().strip()
        s = re.sub(r'[^\w\s-]', '', s)
        s = re.sub(r'[\s_-]+', '-', s)
        s = re.sub(r'-+', '-', s).strip('-')
        if not s: s = "post"
        original_slug = s;
        counter = 1
        query = Post.query.filter_by(slug=s)
        if self.id: query = query.filter(Post.id != self.id)
        while query.first():
            s = f"{original_slug}-{counter}";
            counter += 1
            query = Post.query.filter_by(slug=s)
            if self.id: query = query.filter(Post.id != self.id)
        self.slug = s

    # ************ 关键修改点 ************
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        """当 Post.body 发生变化时，自动将 Markdown 转换为安全的 HTML。"""
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
            'h1', 'h2', 'h3', 'p', 'img', 'video', 'source', 'audio', 'br', 'hr'
        ]
        allowed_attrs = {
            '*': ['class'], 'a': ['href', 'title'],
            'img': ['src', 'alt', 'title', 'width', 'height', 'style'],
            'video': ['src', 'controls', 'width', 'height', 'poster', 'style'],
            'source': ['src', 'type'], 'audio': ['src', 'controls']
        }
        html = markdown.markdown(value, output_format='html',
                                 extensions=['fenced_code', 'tables', 'attr_list'])
        target.body_html = bleach.linkify(bleach.clean(
            html, tags=allowed_tags, attributes=allowed_attrs, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)
# **************************************