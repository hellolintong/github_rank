#coding:utf-8
import sys
sys.path.append('/home/lintong/Flask/github/')

import requests
from BeautifulSoup import BeautifulSoup

'''
def login():
    global LOGIN_FLAG
    payload = {
        'login': Config.USER_NAME,
        'password': Config.PASSWORD
    }
    r = requests.get('https://github.com/login', params=payload)
    if r.status_code == 200:
        LOGIN_FLAG = True
    else:
        LOGIN_FLAG = False
'''


def get_request(url):
    ret = {
        'result': False,
        'r': None,
    }
    for i in xrange(3):
        try:
            r = requests.get(url, timeout=30)
        except requests.exceptions.ConnectionError:
            break
        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.SSLError:
            break
        ret['result'] = True
        ret['r'] = r
        break
    return ret


def get_organization_list(user_name):
    '''
        获取用户参与组织类型
    '''
    ret = []
    if isinstance(user_name, unicode):
        user_name = user_name.encode('utf-8')
    url = 'https://github.com/' + user_name
    ret_ = get_request(url)
    if not ret_['result']:
        return []
    r = ret_['r']
    soup = BeautifulSoup(r.text)
    organization_soup = soup.find('div', {'class': 'clearfix'})
    if not organization_soup:
        return []
    organization_list = organization_soup.findAll('a')
    for organization in organization_list:
        ret.append(organization['href'][1:])
    return ret


def get_following_list(user_name):
    '''
        获取用户跟随者列表
    '''
    ret = []
    if isinstance(user_name, unicode):
        user_name = user_name.encode('utf-8')
    url = 'https://github.com/' + user_name + '/following'
    init_flag = False
    while True:
        ret_ = get_request(url)
        if not ret_['result']:
            return []

        r = ret_['r']
        soup = BeautifulSoup(r.text)
        follow_list = soup.findAll('span', {'class': 'css-truncate css-truncate-target'})
        for follow in follow_list:
            if follow.findChildren('a'):
                name = follow.a['href'][1:]
                ret.append(name)

        # 获取下一页用户
        page_navigation = soup.find('div', {'class': 'pagination'})
        #没有下一页
        if not page_navigation:
            break
        page_navigation = page_navigation.findAll('a')
        #到达最后一页
        if len(page_navigation) == 1 and init_flag is True:
            break
        init_flag = True
        next_navigation = page_navigation[-1]
        url = next_navigation['href']
    return ret


def get_follower_number(user_name):
    '''
        对于跟随者，只要知道其数量就好了，因为搜索是向上搜索的，只有该用户的跟踪用户才有搜索价值，跟随者数量只是用于计算得分用
    '''
    if isinstance(user_name, unicode):
        user_name = user_name.encode('utf-8')

    url = 'https://github.com/' + user_name
    ret = get_request(url)
    if not ret['result']:
        return 0
    r = ret['r']
    soup = BeautifulSoup(r.text)
    count_soup = soup.find('strong', {'class': 'vcard-stat-count'})
    if not count_soup:
        return 0

    #处理1.1k这种情况
    if count_soup.text[-1] == u'k':
        number = float(count_soup.text[0:-1]) * 1000
    elif count_soup.text[-1] == u'w':
        number = float(count_soup.text[0:-1]) * 10000
    else:
        number = int(count_soup.text)

    number = int(number)
    return number


def get_project(user_name):
    '''
        根据用户名获取项目信息
        用户的项目有两种类型:一种是原创项目，一种是参与项目
        对于参与项目，要获取原作者用户名
        对于原创项目，获取项目的信息包括：
        项目名
        项目的语言
        项目得分（根据star和fork数量获取）
        项目描述
        贡献者列表
    '''
    def get_project_by_url(url):
        '''
            根据url爬取项目，一个用户可能会有很多页的项目，所以会采用递归搜索
        '''
        original_project = []
        fork_project = []
        ret = get_request(url)
        if not ret['result']:
            return [], []
        r = ret['r']

        soup = BeautifulSoup(r.text)
        project_soup = soup.find('ul', {'class': 'repo-list js-repo-list'})
        if not project_soup:
            return [], []
        project_list = project_soup.findAll('li')
        for project in project_list:
            project_kind_soup = project.find('p', {'class': 'repo-list-info'})
            # 如果project_kind_soup存在，说明是参与项目，获取原作者用户名
            if project_kind_soup:
                fork_url = project_kind_soup.a['href']
                user = fork_url.split('/')[-2]
                fork_project.append(user)
                continue
            name = project.h3.a['href'][1:]

            stat = project.find('div', {'class': 'repo-list-stats'})
            start_num = project.find('a', {'class': 'repo-list-stat-item tooltipped tooltipped-s', 'aria-label': 'Stargazers'}).text
            start_str = start_num
            # 处理1,234这种情况
            start_num = ''.join(start_num.split(','))
            if not start_num:
                start_num = 0

            fork_num = project.find('a', {'class': 'repo-list-stat-item tooltipped tooltipped-s', 'aria-label': 'Forks'}).text
            fork_str = fork_num
            fork_num = ''.join(fork_num.split(','))
            if not fork_num:
                fork_num = 0

            #因为stat.text包含了language，start_num，fork_num三类string，而且language长度是未知的
            #所以先把start_num, fork_num求出来，然后再减去他们就知道language
            language = stat.text[0:len(stat.text) - len(fork_str + start_str)]

            desc = project.find('p', {'class': 'repo-list-description'})
            if desc:
                desc = desc.text
                #因为数据库规定了项目描述的最大长度，所以要截断
                if len(desc) > 1800:
                    desc = desc[0:1800]
            else:
                desc = ""
            '''
            #获取项目贡献者列表
            contributor_member_list = []
            contributor_url = 'https://www.github.com/' + name + '/graphs/contributors'
            ret = get_request(contributor_url)
            if not ret['result']:
                continue
            r = ret['r']
            soup = BeautifulSoup(r.text)
            contributor_list = soup.findAll('a', {'class': 'aname'})
            for contributor in contributor_list:
                contributor_member_list.append(contributor['href'][1:])
            '''
            contributor_member_list = []
            score = int(start_num) + int(fork_num) + len(contributor_member_list) + 1
            original_project.append({'name': name, 'create_user': user_name, 'language': language, 'score': score, 'desc': desc, 'contributor_list': contributor_member_list})

        #获取下一页仓库数据
        next_page_soup = soup.find('div', {'class': 'pagination'})
        #没有下一页
        if not next_page_soup:
            return original_project, fork_project
        #到达最后一页
        next_page_soup = next_page_soup.find('a', {'rel': 'next'})
        if not next_page_soup:
            return original_project, fork_project
        #运行到这里说明有下一页，所以要递归搜索
        next_url = next_page_soup['href']
        next_url = 'https://github.com' + next_url.encode('utf-8')
        next_ret = get_project_by_url(next_url)
        original_project.extend(next_ret[0])
        fork_project.extend(next_ret[1])
        return original_project, fork_project

    if isinstance(user_name, unicode):
        user_name = user_name.encode('utf-8')
    url = 'https://github.com/' + user_name + '/repositories'
    return get_project_by_url(url)


def crawler_organization(organization_name):
    '''
    此函数为试探搜索，因为从get_project中返回的fork project我们也不知道是不是属于organization的，所以要试探搜索
    '''
    ret = {
        'result': False,
        'name': organization_name,
        'member_list': [],
        'project_list': [],
        'fork_project_list': [],
    }
    if isinstance(organization_name, unicode):
        organization_name = organization_name.encode('utf-8')

    url = 'https://github.com/orgs/' + organization_name + '/people'
    ret_ = get_request(url)
    if not ret_['result']:
        return ret
    r = ret_['r']
    soup = BeautifulSoup(r.text)
    member_soup = soup.find('div', {'id': 'org-members'})
    if not member_soup:
        return ret

    index = 1
    while True:
        member_list = member_soup.findAll('strong', {'class': 'member-username'})
        if not member_list:
            break
        for member in member_list:
            ret['member_list'].append(member.text)
        index += 1
        next_url = 'https://www.github.com/orgs/' + organization_name + '/people?page=' + str(index)
        ret_ = get_request(next_url)
        if not ret_['result']:
            break
        r = ret_['r']
        member_soup = BeautifulSoup(r.text)

    project = get_project(organization_name)
    ret['project_list'] = project[0]
    ret['fork_project_list'] = project[1]
    ret['result'] = True
    return ret


def crawler_user(user_name):
    following_list = get_following_list(user_name)
    follower_number = get_follower_number(user_name)
    project_list = get_project(user_name)
    organization_list = get_organization_list(user_name)

    return {
        'following_list': following_list,
        'follower_num': follower_number,
        'project_list': project_list,
        'organization_list': organization_list,
    }


if __name__ == "__main__":
    import pdb; pdb.set_trace()
    crawler_user('Lao-liu')
