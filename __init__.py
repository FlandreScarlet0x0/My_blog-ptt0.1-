# My_blog/__init__.py
import os
from flask import Flask
from .config import Config  # <-- 导入我们刚定义的 Config
from .extensions import db, login_manager, migrate, whooshee


def create_app(config_class=Config):  # <-- 使用 Config 作为默认值
    """创建并配置 Flask 应用."""

    instance_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance')
    app = Flask(__name__, instance_path=instance_folder)

    # ************ 关键修改点: 先配置，再初始化 ************
    app.config.from_object(config_class)
    # *******************************************************

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

        # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    from . import models  # 在 db 初始化后导入模型
    migrate.init_app(app, db)
    whooshee.init_app(app)

    # 注册蓝图
    from .routes.main import bp as main_bp
    from .routes.auth import bp as auth_bp
    from .routes.admin import bp as admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # 注册命令
    from .command import init_app as init_command_app
    init_command_app(app)

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': models.User,
            'Post': models.Post,
        }

    return app