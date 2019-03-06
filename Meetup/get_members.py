# 从
# https://www.meetup.com/AppliedSingularity/members/?offset=20&sort=social&desc=1
# 获得每个成员的ID

import json
import time

from pyquery import PyQuery

import record_file
import start_session as s

# 本页代码结构
# get_all_members 首先调用get_members_id_in_a_page下载ID
# 然后调用get_members_detail获得一组详细用户的详细信息
# 下载一组用户信息的时候调用了get_detail_of_a_member


def get_all_members(urlname, total, save_member):
    """
    从网页上获得用户的ID。获得从开始页到结尾的所有ID
    此函数是本脚本的入口
    :param urlname: 组织
    :param total: 总共多少用户（不是多少页）
    :param save_member: 函数。每1页用户进行的回调。在本程序中是根据ID下载用户信息。
    """
    print("执行get member in all")
    # 读取成员记录
    r = record_file.read_member_record()
    try:
        i = r[urlname]
    except:
        r[urlname] = 0
        i = 0
    member_ids = []
    while i < (total + 19) // 20:
        part_of_ids = get_members_id_in_a_page(urlname, i)
        member_ids.extend(part_of_ids)
        print("{}第{}页的用户{}".format(urlname, i, part_of_ids[0]))
        i += 1
        get_members_detail(member_ids, urlname, save_member)
        r[urlname] = i                      # 记录里面存的是下一次要下载的页码
        record_file.save_member_record(r)   # 保存记录
        member_ids.clear()


def get_members_id_in_a_page(urlname, page):
    """
    通过爬取网页获得第Page页的所有用户的ID
    :param urlname: 组织名
    :param page: 第几页
    :return: 本页所有用户的ID（List类型）
    """
    data = dict(offset=page * 20, sort="social", desc=1)
    html = s.r.get('{0}/{1}/members/'.format(s.WEBSITE_BASE_URL, urlname), headers=s.headers, params=data)
    doc = PyQuery(html.text)  # 用PyQuery解析HTML
    member_list = doc("#memberList")
    member_ids = []
    for member_li in member_list.children():
        linkurl = doc(member_li)("a.memName").attr('href')
        member_id = linkurl.split('/')[-2]
        member_ids.append(member_id)
    return member_ids


def get_detail_of_a_member(urlname, user_id):
    """
    获取1个用户详细资料
    :param urlname: 组织名
    :param user_id: 用户ID
    :return:
    """
    data = dict(key=s.KEY)
    result = s.r.get("{0}/{1}/members/{2}".format(s.API_BASE_URL, urlname, user_id), headers=s.headers, params=data)
    return json.loads(result.text)


def get_members_detail(member_ids, urlname, save_member):
    """
    下载一批(20个)用户的详细资料
    :param save_member: 函数。保存用户信息
    :param member_ids:
    :param urlname:
    :return:
    """
    members = []
    for member_id in member_ids:
        flag = True
        while flag:
            member = get_detail_of_a_member(urlname, member_id)
            members.append(member)
            flag = False
            try:
                time.sleep(0.1)
            except KeyError:
                error = str(member)
                if "Credentials have be throttled more than" in error:
                    print("[被封禁1小时]出现KeyError 错误是 " + str(member) + " 成员是 " + member_id)
                else:
                    print("[初步警告]出现KeyError 错误是 " + str(member) + " 成员是 " + member_id)
                flag = True
                s.new_session()  # 如果出现错误就开始新会话
                time.sleep(3)
    save_member(member_ids, members)