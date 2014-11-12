#coding:utf-8
import mongoengine
from ..base import BaseMongoStorage
from config import Config

mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


class OrganizationStorage(BaseMongoStorage, mongoengine.Document):
    """ store organization info
        name 组织名称
        member_list 组织成员列表
        project_list 组织项目列表
        date 更新日期
        score 组织得分
    """
    name = mongoengine.StringField(max_length=256, unique=True, required=True)
    member_list = mongoengine.ListField(mongoengine.StringField(max_length=256))
    project_list = mongoengine.ListField(mongoengine.StringField(max_length=256))
    date = mongoengine.DateTimeField()
    score = mongoengine.FloatField()

    meta = {
        'ordering': ['-score']
    }
