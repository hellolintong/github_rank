#coding:utf-8
import sys
sys.path.append('/home/lintong/Flask/github/')
import time
from db.user import user_model
from db.project import project_model
from db.organization import organization_model
from spider import spider
from config import Config
from Queue import Queue

def add_organization(queue, **kwargs):
        project_name_list = []

        for member in kwargs['member_list']:
            if not user_model.get_user(name=member) and not queue.full():
                queue.put(member)

        for project in kwargs['project_list']:
            project_name_list.append(project['name'])
            if not project_model.get_project(name=project['name']):
                project_model.add_project(**project)

        #organization 只存储project的name
        kwargs['project_list'] = project_name_list
        organization_model.add_organization(**kwargs)

        for member in kwargs['fork_project_list']:
            if not user_model.get_user(name=member) and not queue.full():
                queue.put(member)

def calculate():
    queue = Queue(100000)

    user_list = user_model.get_user()
    if not user_list:
        queue.put(Config.USER_NAME)
    else:
        #爬虫只对得分最高的用户爬取(考虑到频繁爬取会被封杀ip)
        #可能出现排名第一的用户的所有跟随用户都被添加了，但是仍旧没有得分比他高的用户，所以要选择得分第二高的用户搜索
        for user in user_list:
            for key in user.following_list:
                if not user_model.get_user(name=key) and not queue.full():
                    queue.put(key)
            if not queue.empty():
                break

    while not queue.empty():
        user_name = queue.get()
        result = spider.crawler_organization(user_name)

        #说明user是组织
        if result['result']:
            result.pop('result')
            add_organization(queue, **result)
            continue

        result = spider.crawler_user(user_name)
        original_project = result['project_list'][0]
        fork_project = result['project_list'][1]

        #添加用户参与的仓库
        for project in original_project:
            if not project_model.get_project(name=project['name']):
                project_model.add_project(**project)

        #将组织也添加到搜索列表中（搜索列表不区分是组织还是用户）
        for organization in result['organization_list']:
            if not organization_model.get_organization(name=organization):
                organization = spider.crawler_organization(organization)
                add_organization(queue, **organization)

        #将该用户添加到数据库中
        project_name_list = []
        for project in original_project:
            project_name_list.append(project['name'])
        kwargs = {
            'name': user_name,
            'follower_num': result['follower_num'],
            'following_list': result['following_list'],
            'project_list': project_name_list,
            'fork_project_list': fork_project,
            'organization_list': result['organization_list'],
        }
        user_model.add_user(**kwargs)

       #将参与项目的用户添加到搜索列表中
        for user in fork_project:
            #因为不知道用户是user还是organization，所以要查两个表
            if not user_model.get_user(name=user) and not organization_model.get_organization(name=user) and not queue.full():
                queue.put(user)

        print "巴扎黑"
        time.sleep(60)


if __name__ == "__main__":
    while True:
        import pdb; pdb.set_trace()

        calculate()
        time.sleep(10 * 60)
