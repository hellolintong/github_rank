#coding:utf8

import mongoengine
from ..base import BaseMongoStorage
from config import Config

mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


class UserStorage(BaseMongoStorage, mongoengine.Document):
    """ store user info
        name 用户id
        following_list 跟随的用户id列表
        follower_num 跟随者数量
        project_list 项目列表(只涉及到原创项目，fork的项目不算）
        organization_list 组织列表
        date 更新日期
        score 得分
    """
    name = mongoengine.StringField(max_length=256, unique=True, required=True)
    following_list = mongoengine.ListField(mongoengine.StringField(max_length=256))
    follower_num = mongoengine.IntField()
    project_list = mongoengine.ListField(mongoengine.StringField(max_length=256))
    organization_list = mongoengine.ListField(mongoengine.StringField(max_length=256))
    date = mongoengine.DateTimeField()
    score = mongoengine.FloatField()

    meta = {
        'ordering': ['-score']
    }
