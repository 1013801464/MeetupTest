import requests

# 头部信息
r = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'}
API_BASE_URL = 'https://api.meetup.com'
WEBSITE_BASE_URL = 'https://www.meetup.com'

# GET请求要使用的KEY
KEY = "6ca392e35c71124953276d2f1f1530"

# 新的session
def new_session():
    global r
    r = requests.Session()