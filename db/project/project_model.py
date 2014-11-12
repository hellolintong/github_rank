from project_stroage import ProjectStorage
import mongoengine
from config import Config

mongoengine.connect(Config.DB_NAME, host=Config.DB_HOST, port=Config.DB_PORT)


############project edit###############
def add_project(**kwargs):
    project = ProjectStorage()
    project.name = kwargs['name']
    project.create_user = kwargs['create_user']
    project.desc = kwargs['desc']
    project.language = kwargs['language']
    project.contributor_list = kwargs['contributor_list']
    project.score = kwargs['score']
    try:
        project.save()
    except Exception:
        return None
    return project


def update_project(project, **kwargs):
    project.update(**kwargs)


def delete_project(project):
    project.delete()


###########project check###############
def get_project(**kwargs):
    return ProjectStorage.get(**kwargs)
