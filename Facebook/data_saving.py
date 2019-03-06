from pymongo import MongoClient

m = MongoClient("localhost", 27017)
db = m.meetup

urlname = ""

def save_facebook_data(id, name, time, content):
    post = dict()
    post["id"] = id
    post["name"] = name
    post["time"] = time
    post["content"] = content
    post["urlname"] = urlname
    print(post)
    db.facebook.replace_one({"id": id}, post, True)


def get_groups():
    return db.groups.find()


