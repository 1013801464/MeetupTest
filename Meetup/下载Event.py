# 爬第3页 获得所有Event
import json
import time

from pymongo import MongoClient

import record_file as record_file
import start_session as s
from get_groups import download_groups

PAGE_SIZE = 200

# 本程序的入口在 main 处。
# 本程序首先通过 download_all_events 下载某个组织的所有事件，
# 然后通过download_event_members下载事件的所有成员。
#

########## 函数区域 #########
def download_all_events(urlname):
    """
    下载某个组织的所有事件。
    :param urlname: 组织的URL
    :return: 由event组成的list。这是list是从API解析出来的。
    """
    print("正在下载第1组事件...", end="")
    events = download_events(urlname)
    print("len = " + str(len(events)))
    flag = len(events) == PAGE_SIZE  # 第一组事件是否满1页
    while flag:
        print("下载第n组事件...", end="")
        new_events = download_events(urlname, events[-1]["local_date"] + "T" + events[-1]["local_time"] + ":00.000")
        print("len = " + str(len(new_events)))
        # 下面的一段代码用于去重
        if len(new_events) <= 1:
            return events
        else:
            start = 0
            for e in new_events:
                if events[-1]["time"] == e["time"]:
                    start += 1
                    if events[-1]["id"] == e["id"]:
                        break
                else:
                    break
        events.extend(new_events[start:len(new_events)])
        time.sleep(0.12)
        flag = len(new_events) == PAGE_SIZE
    return events


def download_events(urlname, no_earlier_than=""):
    """
    使用API下载一组事件（最多200个）
    :param urlname: 组织
    :param no_earlier_than: 不早于
    :return: 将API返回的结果直接用JSON解析并返回
    """
    if len(no_earlier_than) == 0:
        data = dict(key=s.KEY, status="past", page=str(PAGE_SIZE), fields="attendance_count")
    else:
        data = dict(key=s.KEY, status="past", page=str(PAGE_SIZE), fields="attendance_count",
                    no_earlier_than=no_earlier_than)
    return json.loads(s.r.get('{0}/{1}/events'.format(s.API_BASE_URL, urlname), headers=s.headers, params=data).text)


def download_event_members(urlname, event_id):
    """
    获取参加某活动的所有成员
    :param urlname: 组织的名字
    :param event_id: 事件ID
    :return: API限制，最多返回200个。但是好像所有event的参加人数都不超过200
    """
    data = dict(key=s.KEY)
    data["photo-host"] = "public"
    return json.loads(
        s.r.get("{0}/{1}/events/{2}/attendance".format(s.API_BASE_URL, urlname, event_id), headers=s.headers,
                params=data).text)


def read_a_record(record, urlname):
    """
    读取某个组织的是否已经下载过了。本函数只是对dict的读取进行了简单封装。
    :param record: JSON格式的信息
    :param urlname: 组织名
    """
    try:
        return record[urlname]
    except:
        record[urlname] = 0
        return 0


##################################

if __name__ == '__main__':
    conn = MongoClient("localhost", 27017)    # 连接MongoDB数据库
    db = conn.meetup
    record = record_file.read_event_record()  # 读取当前下载进度
    groups = json.loads(download_groups().text)['results']  # 查找所有Group
    for group in groups:
        urlname = group["urlname"]
        if read_a_record(record, urlname) != 0: continue    # 如果已经爬过了就跳过
        print("正在下载%s的事件" % urlname)
        events = download_all_events(urlname)               # 下载到所有事件
        group = db.groups.find_one({"urlname": urlname})
        group["events"] = []                                # 活动ID=空
        for i in range(len(events)):
            event = events[i]
            # if i % 5 == 0:
            #    print("[%s/%s/%.2f%%]下载活动%s的成员" % (i, len(events), i / len(events) * 100, event["id"]))
            group["events"].append(event["id"])                         # 追加活动ID到组织中
            e_members = download_event_members(urlname, event["id"])    # 下载所有成员
            event["attendance"] = e_members                             # 添加成员到事件中
            time.sleep(0.12)
        time.sleep(1)
        if len(events) == 0: continue
        print("正在保存事件...", end="")
        for event in events:                                        # 添加事件
            db.events.replace_one({'id': event["id"]}, event, True)
        print(db.groups.replace_one({"urlname": urlname}, group))   # 更新组织信息
        record[urlname] = 1                                         # 标记为下载已完成
        record_file.save_event_record(record)                       # 保存刚才的标记
        print("保存成功")