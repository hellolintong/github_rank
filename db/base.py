#coding:utf-8
import mongoengine


class BaseMongoStorage(object):

    def save(self):
        mongoengine.Document.save(self)

    def update(self, **kwargs):
        new_kwargs = {}
        for key in kwargs:
            new_kwargs['set__' + key] = kwargs[key]
        mongoengine.Document.update(**new_kwargs)

    def delete(self):
        mongoengine.Document.delete(self)

    @classmethod
    def get(cls, **kwargs):
        return [obj for obj in cls.objects(**kwargs)]

    @property
    def key(self):
        return str(self.pk)


    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

