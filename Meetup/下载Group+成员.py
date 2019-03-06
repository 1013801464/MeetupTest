# 爬第1页 DIYBio概览信息和参与的Group

import json
import logging

from pymongo import MongoClient

from get_groups import download_groups
from get_members import get_all_members

############################
if __name__ == '__main__':
    groups = json.loads(download_groups().text)  # 下载目标话题的所有组织
    conn = MongoClient("localhost", 27017)  # 连接MongoDB数据库
    db = conn.meetup
    for group in groups['results']:
        urlname = group['urlname']
        try:
            group["all_members"] = db.groups.find_one({"urlname": urlname})["all_members"]
        except KeyError as e:
            logging.exception(e)
        except TypeError as e:
            logging.exception(e)
        g = db.groups.replace_one({"urlname": urlname}, group, True)    # 对Group进行的替换（或插入）
        members_count = group["members"]
        print("组织{0}有{1}个人".format(urlname, members_count))
        if group["visibility"] == "public":
            def save_member(member_ids, members):  # 函数：保存一组id和用户信息
                if "all_members" not in group:
                    group["all_members"] = []
                for member_id in member_ids:
                    group["all_members"].append(member_id)
                print("正在写入数据库...")
                db.groups.replace_one({"urlname": urlname}, group, True)
                # db.members.insert_many(members)  # 这一步无法实现增量更新
                for member in members:
                    db.members.replace_one({"id": member['id']}, member, True)
                print("写入完成.")


            get_all_members(urlname, members_count, save_member)
        else:
            pass
