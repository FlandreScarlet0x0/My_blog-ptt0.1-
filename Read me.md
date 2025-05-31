# Flandre的It's my og!文档介绍(大概)
这是一个基于 Flask 框架构建的个人博客项目。它支持用户注册、登录、发布和编辑文章（使用 Markdown）、上传图片和视频、文章分类与标签、评论系统、以及多种视觉主题切换（包含背景音乐）。
## 项目结构

为了确保项目能正确运行，请遵循以下文件结构：

```
/D:/az/blog/
|
├── .flaskenv              # <--- 环境变量文件
|
├── instance/              # <--- Flask 自动创建，用于存放数据库等
|   └── blog.db
|
├── migrations/            # <--- Flask-Migrate 的迁移文件
|
├── My_blog/               # <--- Flask 应用核心包
|   |
|   ├── __init__.py        # <--- 应用工厂
|   ├── config.py          # <--- 配置文件
|   ├── extensions.py      # <--- Flask 扩展
|   ├── models.py          # <--- 数据库模型
|   ├── command.py         # <--- 自定义命令 (例如创建管理员,目前指创建flask db init命令)
|   |
|   ├── static/            # <--- 静态文件
|   |   ├── css/
|   |   │   └── style.css
|   |   ├── js/
|   |   │   ├── background_fade.js
|   |   │   ├── navigation.js
|   |   │   └── theme.js
|   |   ├── images/
|   |   │   └── (存放图标图片等)
|   |   └── uploads/       # <--- 用户上传的文件
|   |
|   └── templates/         # <--- Jinja2 模板
|       ├── base.html
|       ├── index.html
|       ├── post.html
|       ├── create_post.html
|       ├── edit_post.html
|       ├── login.html
|       ├── register.html
|       ├── profile.html
|       ├── edit_profile.html
|       └── search.html
|
└── run.py                 # <--- 启动脚本
```
## 安装与运行

如果您要运行该程序要做以下步骤
### 1.打开终端，进入 指定运行目录
如在终端定位
cd D:\az\blog
### 2. 删除 instance 文件夹和 migrations 文件夹。(已删除)
### 3.激活虚拟环境。
如输入（在Win CMD）
D:\az\blog\.venv\Scripts\activate.bat 
### 4.安装依赖
pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login Flask-Whooshee markdown bleach python-dotenv
### 5.初始化数据库
- flask db init（只需运行一次）
- flask db migrate
- flask db upgrade
### 附：
第一次运行需要在command.py加入db.create_all()代码
如
# My_blog/command.py
```
import click
from flask.cli import with_appcontext

@click.command('init-db')
@with_appcontext
def init_db_command():
    """初始化数据库（只运行一次）"""
    db.create_all()
    click.echo('数据库已初始化')

def init_app(app):
    app.cli.add_command(init_db_command)  # 注册命令
然后在 create_app() 中注册：
```
python
```
# My_blog/__init__.py
from .command import init_app as init_command_app

def create_app():
    # ...其他代码...
    init_command_app(app)  # 注册命令
    return app
```
### 6. 运行应用

-   使用 `flask run` 命令启动开发服务器。

    ```bash
    flask run
    ```
-   我一般在run.py脚本运行启用()
-   在浏览器中打开 `http://127.0.0.1:5000` 即可访问你的博客。

---
