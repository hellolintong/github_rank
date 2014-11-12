#coding:utf-8
from flask import g, render_template, abort, request, sessions
from flask import Blueprint
from db.project import project_model
from config import Config
project = Blueprint('project', __name__, template_folder=Config.PARENT_DIR+'/template', static_folder=Config.PARENT_DIR+'/static')


@project.route('/project/rank/<language>')
def project_rank(language):
    '''
       根据语言获取项目排名
    '''
    if language == 'all':
        language = ""
    project_list = project_model.get_project(language=language)
    number = len(project_list)
    return render_template('project_rank.html', project_list=project_list, number=number)
