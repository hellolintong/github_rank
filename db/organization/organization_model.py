#coding:utf8
import datetime
import mongoengine
from config import Config
from organization_storage import OrganizationStorage
mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


############organization edit###############
def add_organization(**kwargs):
    organization = OrganizationStorage()
    organization.name = kwargs['name']
    organization.member_list = kwargs['member_list']
    organization.project_list = kwargs['project_list']
    organization.date = datetime.datetime.now()
    #如果组织的得分也按照项目得分算的话，用户的得分会被重复计算，所以组织得分直接按照项目数量和成员数量算
    organization.score = len(kwargs['project_list']) * 0.7 + len(kwargs['member_list']) * 0.3
    try:
        organization.save()
    except Exception:
        return None
    return organization


def update_organization(organization, **kwargs):
    organization.update(**kwargs)


def delete_organization(organization):
    organization.delete()


def get_organization(**kwargs):
    return OrganizationStorage.get(**kwargs)