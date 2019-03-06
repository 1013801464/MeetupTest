import start_session as s


def download_groups(topic="diybio"):
    """
    # 根据Topic查找所有的组织
    :param topic: 待查找的话题
    :return: 组织列表
    """
    data = dict(key=s.KEY, topic=topic)
    return s.r.get('{0}/2/groups'.format(s.API_BASE_URL), headers=s.headers, params=data)