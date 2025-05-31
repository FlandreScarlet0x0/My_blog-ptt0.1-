## run.py
import os
from My_blog import create_app

# 从 .flaskenv 或环境变量加载
# FLASK_APP=run.py 和 FLASK_DEBUG=1
app = create_app()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 静态文件立即过期
app.config['TEMPLATES_AUTO_RELOAD'] = True   # 模板自动重载
if __name__ == '__main__':
    app.run()