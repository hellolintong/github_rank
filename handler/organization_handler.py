#coding:utf-8
from flask import g, render_template, abort, url_for, request, sessions
from flask import Blueprint
from db.organization import organization_model
from db.project import project_model
from config import Config
organization = Blueprint('organization', __name__, template_folder=Config.PARENT_DIR+'/template', static_folder=Config.PARENT_DIR+'/static')


@organization.route('/organization/<organization_name>')
def fetch_organization(organization_name):
    '''
        获取组织的基本信息
    '''
    organization = organization_model.get_organization(name=organization_name)
    if not organization:
        abort()
    organization = organization[0]
    project_list = []
    for project_key in organization.project_list:
        project = project_model.get_project(name=project_key)
        if not project:
            abort()
        project = project[0]
        project_list.append(project)
    return render_template('organization_info.html', project_list=project_list, organization=organization)


@organization.route('/organization/rank')
def organization_rank():
    '''
        组织的排名
    '''
    organization_list = organization_model.get_organization()
    new_organization_list = []
    number = len(organization_list)
    for organization in organization_list:
        organization_info_url = unicode(url_for('.fetch_organization', organization_name=organization.name))
        new_organization_list.append({
            u'name': organization.name,
            u'score': unicode(organization.score),
            u'info_url': organization_info_url,
            u'update_date': unicode(organization.date.strftime("%H:%M"))
        })
    return render_template('organization_rank.html', organization_list=new_organization_list, number=number)
