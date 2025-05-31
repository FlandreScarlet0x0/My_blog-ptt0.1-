# My_blog/config.py
import os

# 获取 My_blog 目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))
# 获取项目根目录 (My_blog 的上一级，即 D:\az\blog)
project_root = os.path.dirname(basedir)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_hard_to_guess_string_$%^&*('

    # --- 数据库配置 (使用 instance 文件夹) ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(project_root, 'instance', 'blog.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- 分页配置 ---
    POSTS_PER_PAGE = 5
    COMMENTS_PER_PAGE = 10

    # --- 文件上传配置 ---
    UPLOADED_MEDIA_DEST = os.path.join(basedir, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'ogg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    DEBUG = True  # 可以通过环境变量覆盖
    WHOOSHEE_MIN_STRING_LEN = 1