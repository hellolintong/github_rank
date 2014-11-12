#coding:utf-8
from flask import g, render_template, abort, url_for, request, sessions
from flask import Blueprint
from db.user import user_model
from db.project import project_model
from config import Config
user = Blueprint('user', __name__, template_folder=Config.PARENT_DIR+'/template', static_folder=Config.PARENT_DIR+'/static')


@user.route('/user/<user_name>')
def fetch_user(user_name):
    '''
        获取用户的基本信息
    '''
    user = user_model.get_user(name=user_name)
    if not user:
        abort()
    user = user[0]
    new_project_list = []
    for project_key in user.project_list:
        project = project_model.get_project(name=project_key)
        if not project:
            abort()
        project = project[0]
        new_project_list.append(project)
    return render_template('user_info.html', project_list=new_project_list, user=user)


@user.route('/')
def index():
    '''
        用户排名
    '''
    user_list = user_model.get_user()
    new_user_list = []
    number = len(user_list)
    for user in user_list:
        user_info_url = unicode(url_for('.fetch_user', user_name=user.name))
        new_user_list.append({
            u'name': user.name,
            u'score': unicode(user.score),
            u'info_url': user_info_url,
            u'update_date': unicode(user.date.strftime("%H:%M"))
        })
    return render_template('index.html', user_list=new_user_list, number=number)


@user.route('/about')
def about():
    return render_template('about.html')
