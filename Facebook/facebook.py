import re
import time
from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

import data_saving


class Facebook:
    def __init__(self):
        self.browser = webdriver.Chrome()

    def login(self):
        try:
            self.browser.get('https://www.facebook.com')
            emailEle = WebDriverWait(self.browser, 2).until((lambda driver: self.browser.find_element_by_id('email')))
            passwordEle = WebDriverWait(self.browser, 2).until((lambda driver: self.browser.find_element_by_id('pass')))
            loginBtn = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_element_by_xpath(".//input[@data-testid='royal_login_button']"))
            emailEle.send_keys("1013801464@qq.com")
            passwordEle.send_keys("qq1013801464")
            loginBtn.click()
            print("开始等待2秒...", end="")
            time.sleep(2)
            print("等待结束")
        finally:
            pass
            # self.browser.close()
            # self.browser.quit()

    @staticmethod
    def __remove_facebook_redirect(url):  # 处理Facebook重定向连接和Tag
        # 处理TAG /hashtag/neuroscience?source=feed_text&epa=HASHTAG 从链接本身下手 提取neuroscience
        tags = re.findall("/hashtag/(.*?)\?source=feed_text&epa=HASHTAG", url, re.I | re.S | re.M)
        if len(tags) > 0:
            return '#' + tags[0]
        # 去掉l.facebook.com类型的重定向
        s = re.findall("https://l.facebook.com/l.php\?u=([^&]*)", url, re.I | re.S | re.M)
        if len(s) == 0: return url
        return unquote(s[0])  # URL decode

    # 把<a href='url'>link</a>替换的只剩url
    def __replace_only_url(self, m):
        # print("URL替换之前 " + m.string[m.start():m.end()])
        res_url = r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')"
        link = re.findall(res_url, m.string[m.start():m.end()], re.I | re.S | re.M)
        return self.__remove_facebook_redirect(link[0])

    def __get_post_content(self, content):
        # print("\n原始内容:" + content)
        ps = re.findall(r'<p[^>]*>(.*?)</p>', content, re.S | re.M)
        a = []
        for m in ps:
            no_a = re.sub(r'<a[^>]*>.*?</a>', self.__replace_only_url, m.replace('&amp;', '&'))
            a.append(no_a)
            a.append('\n')
            # print(no_a)
        return ''.join(a)

    ## 本模块用于定位到帖子所在元素
    def analyze_group(self, url):
        try:
            self.browser.get(url)
            from selenium.common.exceptions import TimeoutException
            try:
                # 找出feed的子元素 - 所有帖子
                posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@role='feed']/div"))
                # 遍历feed中的帖子
                for i in range(2, len(posts) + 1):
                    post = self.browser.find_elements_by_xpath(".//div[@role='feed']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]" % i)
                    if len(post) == 0: continue  # 过滤掉"近期动态" "更早"等内容
                    post_id = self.browser.find_element_by_xpath(".//div[@role='feed']/div[%s]/.//div[contains(@class,'userContentWrapper')]/../.." % i).get_attribute("id")
                    person_and_type = self.browser.find_elements_by_xpath(".//div[@role='feed']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//h5/.//a" % i)
                    who = person_and_type[0].text
                    when = self.browser.find_element_by_xpath(".//div[@role='feed']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i).get_attribute("title")
                    ### 获得帖子内容（不用点击"展开" 内容本来就有）
                    content = self.browser.find_element_by_xpath(".//div[@role='feed']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                    content = self.__get_post_content(content.get_attribute("outerHTML"))
                    data_saving.save_facebook_data(post_id, who, when, content)
                # 滚动 +等待
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                # 获得 recent_activity 的所有子元素
                posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@role='feed']/../div"))
                # 遍历 recent_activity 从第2个元素开始的所有子元素(元素1是feed)
                for i in range(2, len(posts) + 1):
                    post = self.browser.find_elements_by_xpath(".//div[@role='feed']/../div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//h5/.//a" % i)
                    if len(post) == 0: continue  # 过滤掉"近期动态" "更早"等内容
                    post_id = self.browser.find_element_by_xpath(".//div[@role='feed']/../div[%s]/.//div[contains(@class,'userContentWrapper')]/../.." % i).get_attribute("id")
                    person_and_type = self.browser.find_elements_by_xpath(".//div[@role='feed']/../div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//h5/.//a" % i)
                    who = person_and_type[0].text
                    when = self.browser.find_element_by_xpath(".//div[@role='feed']/../div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i).get_attribute("title")
                    content = self.browser.find_elements_by_xpath(".//div[@role='feed']/../div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                    content = self.__get_post_content(content[0].get_attribute("outerHTML"))
                    data_saving.save_facebook_data(post_id, who, when, content)
            except TimeoutException as e:
                print(e)
                pass
        finally:
            pass

    def analyze_event(self, url):
        self.analyze_group(url)

    def analyze_public_page(self, url, special = False):
        try:
            self.browser.get(url)
            who = self.browser.find_element_by_xpath(".//h1[@id='seo_h1_tag']/a/span").text  # 注意 我把时间+who当做ID
            # 获取_1xnd下的帖子
            posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@class='_1xnd']/div"))
            for i in range(2, len(posts)):
                if special and i == 2:
                    content = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[3]/div[2]" % i)
                else:
                    content = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                content = self.__get_post_content(content.get_attribute("outerHTML"))
                if special and i == 2:
                    when = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[3]/div[1]/.//span[@class='timestampContent']/.." % i)
                else:
                    when = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i)
                data_saving.save_facebook_data(when.get_attribute("data-utime"), who, when.get_attribute("title"), content)
            try:  # 后面的帖子可能不存在，所以进行了捕获
                # 滚动 + 等待
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                # 获取_1xnd/_1xnd下的帖子
                posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div"))
                for i in range(1, len(posts)):
                    content = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                    content = self.__get_post_content(content.get_attribute("outerHTML"))
                    when = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i)
                    data_saving.save_facebook_data(when.get_attribute("data-utime"), who, when.get_attribute("title"), content)
                # 滚动 + 等待
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                # 获取_1xnd/_1xnd/_1xnd下的帖子
                posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div"))
                for i in range(1, len(posts)):
                    content = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                    content = self.__get_post_content(content.get_attribute("outerHTML"))
                    when = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i)
                    data_saving.save_facebook_data(when.get_attribute("data-utime"), who, when.get_attribute("title"), content)                # 滚动 + 等待
                # 滚动 + 等待
                self.browser.execute_script("var q=document.documentElement.scrollTop=100000")
                time.sleep(7)
                # 获取_1xnd/_1xnd/_1xnd下的帖子
                posts = WebDriverWait(self.browser, 4).until(lambda driver: self.browser.find_elements_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div"))
                for i in range(1, len(posts)):
                    content = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[2]" % i)
                    content = self.__get_post_content(content.get_attribute("outerHTML"))
                    when = self.browser.find_element_by_xpath(".//div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[@class='_1xnd']/div[%s]/.//div[contains(@class,'userContentWrapper')]/div[1]/div[2]/div[1]/.//span[@class='timestampContent']/.." % i)
                    data_saving.save_facebook_data(when.get_attribute("data-utime"), who, when.get_attribute("title"), content)
            except Exception as e:
                print(e)
        finally:
            pass


def extract_facebook_link(message):
    pass


def process_url(url):
    '''
    将各类URL处理成统一的形式
    :param url:
    :return: (类型，处理后的URL）类型=1表示event，类型=2表示小组，类型=3表示公共主页
    '''
    print("原始URL: " + url)
    # 特殊处理的URL
    if url.find("RigaHighTech") > -1: return 3, r"https://www.facebook.com/pg/RigaHighTech/posts/?ref=page_internal"
    if url.find("bioentrepreneurs") > 0: return 0, ""
    if url.find("biohackersmeetup") > 0: return 0, ""
    if url.find("biohackerspacelille") > 0: return 0, ""
    # 检查是不是 event
    result = re.findall(r'https?://www.facebook.com/events/(.*?)/?$', url)
    if len(result) == 1:
        return 1, r"https://www.facebook.com/events/" + result[0] + r"/?active_tab=discussion"
    # 检查是不是小组
    result = re.findall(r'https?://www.facebook.com/groups/(.*?)/?$', url)
    if len(result) == 1:
        return 2, r"https://www.facebook.com/groups/" + result[0]
    # 检查公共主页
    result = re.findall(r'https?://www.facebook.com/(?:pg/)?(.*?)/?$', url)
    if len(result) == 1:
        return 3, r"https://www.facebook.com/pg/" + result[0] + "/posts/"


if __name__ == "__main__":
    fb = Facebook()
    fb.login()
    groups = data_saving.get_groups()
    flag = False    # debug
    for g in groups:
        # urls = re.findall(r"(?<=href=\").+?(?=\")",g['description'])
        # urls = re.findall(r"https?://www.facebook.com/(?!events)(?:[0-9A-Za-z/\-]|.(?=[0-9a-zA-Z]))+", g['description'])
        urls = re.findall(r"https?://www.facebook.com/(?:[0-9A-Za-z/\-]|.(?=[0-9a-zA-Z]))+", g['description'])
        if urls is None or len(urls) == 0:
            continue
        else:
            data_saving.urlname = g['urlname']
            the_type, url = process_url(urls[0])
            if urls[0].find("biohackerspacelille") > -1:
                flag = True     # debug
                continue
            if not flag: continue
            if the_type == 1:
                fb.analyze_event(url)
            elif the_type == 2:
                fb.analyze_group(url)
            elif the_type == 3:
                fb.analyze_public_page(url, url.find("RigaHighTech") > -1)
    fb.browser.quit()  # 退出驱动
