#coding:utf8
import datetime
import mongoengine
from config import Config
from user_storage import UserStorage
from ..organization.organization_model import get_organization
from ..project.project_model import get_project

mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


############user edit###############
def add_user(**kwargs):
    user = UserStorage()
    user.name = kwargs['name']
    user.follower_num = kwargs['follower_num']
    user.following_list = kwargs['following_list']
    user.project_list = kwargs['project_list']
    user.organization_list = kwargs['organization_list']
    user.date = datetime.datetime.now()
    calculate_score(user, **kwargs)
    try:
        user.save()
    except Exception:
        return None

    return user


def update_user(user, **kwargs):
    user.update(**kwargs)


def delete_user(user):
    user.delete()


def get_user(**kwargs):
    return UserStorage.get(**kwargs)


def calculate_score(user, **kwargs):
    organization_score = 0
    project_score = 0
    for organization_name in user.organization_list:
        organization = get_organization(name=organization_name)[0]
        organization_score += organization.score
    for project_name in user.project_list:
        project = get_project(name=project_name)[0]
        project_score += project.score
    project_score += len(kwargs['fork_project_list'])
    score = user.follower_num * 0.4 + organization_score * 0.3 + project_score * 0.3
    user.score = score































