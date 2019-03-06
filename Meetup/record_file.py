# 保存每个group保存到哪一页了
import json

record_file = 'member_record.txt'
event_record_file = "event_record.txt"


def read_member_record():
    try:
        f = open(record_file)
        records = json.load(f)
        f.close()
        return records
    except:
        records = dict()
        #for name0 in urlnames:
        #    records[name0] = 0
        return records


def save_member_record(record):
    f = open(record_file, "w")
    try:
        f.write(json.dumps(record))
    finally:
        f.close()


def save_event_record(record):
    f = open(event_record_file, "w")
    try:
        f.write(json.dumps(record))
    finally:
        f.close()


# 读取事件下载记录(只管group是否已经下载完成, 不存具体下载到哪一个了)
def read_event_record():
    try:
        f = open(event_record_file)
    except FileNotFoundError:
        return dict()
    try:
        events = json.load(f)
        return events
    except Exception as e:
        return dict()


# 测试代码
if __name__ == '__main__':
    s = dict(abc=12, dedf=7)
    save_member_record(s)
    e = read_member_record()
    print(e)
