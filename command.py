# My_blog/command.py
import click
from flask.cli import with_appcontext
from .extensions import db # 使用相对导入，因为 command.py 在 My_blog 包内

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    click.echo('Initialized the database tables.')
    # 可以在这里添加创建默认用户或分类的逻辑
    from .models import User, Category
    if not User.query.filter_by(username='admin').first():
         admin_user = User(username='admin', email='admin@example.com', is_admin=True)
         admin_user.set_password('adminpassword')
         db.session.add(admin_user)
         db.session.commit()
         click.echo('Created admin user.')


def init_app(app):
    """Register database initialization command."""
    app.cli.add_command(init_db_command)
