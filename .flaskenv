FLASK_APP=run.py  # My_blog指向你的包名，Flask会自动查找 __init__.py 中的 create_app
FLASK_DEBUG=1      # 启用调试模式 (在Flask 2.3+ 中)
# FLASK_ENV=development # (在旧版本 Flask 中)
# SECRET_KEY=your_actual_secret_key (如果不在 config.py 中通过 os.environ.get 读取)