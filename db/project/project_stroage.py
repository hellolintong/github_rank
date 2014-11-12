#coding:utf-8
import mongoengine
from ..base import BaseMongoStorage
from config import Config

mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


class ProjectStorage(BaseMongoStorage, mongoengine.Document):
    """ store user info
        name 项目名称（id）
        create_user 项目创始者id（根据项目类型做区分）
        language 项目使用的语言
        desc 项目介绍
        score 项目得分
        type 项目类型（individual, organization)
        contributor_list 贡献者列表
    """
    name = mongoengine.StringField(max_length=256, unique=True, required=True)
    create_user = mongoengine.StringField(max_length=257, required=True)
    language = mongoengine.StringField(max_length=20)
    desc = mongoengine.StringField(max_length=2000)
    score = mongoengine.FloatField()
    type = mongoengine.StringField(max_length=20)
    contributor_list = mongoengine.ListField(mongoengine.StringField(max_length=256))

    meta = {
        'ordering': ['-score']
    }
