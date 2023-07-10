import time
import traceback
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common import exceptions
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
import logging as log

# 获取chrome浏览器驱动路径


def get_chrome_driver(s_chrome_driver_dir=None):
    if not s_chrome_driver_dir:
        print("浏览器驱动的配置路径(%s)没有配置" % s_chrome_driver_dir)
        return None

    p_option = webdriver.ChromeOptions()
    s_option_dir = "--user-data-dir=%s" % s_chrome_driver_dir
    p_option.add_argument(s_option_dir)
    p_option.add_experimental_option('excludeSwitches', ['enable-logging'])
    try:
        p_browser_driver = webdriver.Chrome(options=p_option)
    except exceptions.InvalidArgumentException as chrome_error:
        print("(%s)检查是否已经打开过Chrome浏览器,先关闭在运行" % chrome_error)
        return None

    return p_browser_driver


# selenium公共类
class SeleniumUse(object):
    def __init__(self, s_user_data=None, s_request_url=None):
        self.s_request_url = s_request_url
        self.s_driver_exe_dir = s_user_data if s_user_data else r'D:\Projects\tool\driver_data'
        self.p_driver = None
        # 当前登录后的 X-CSRF-Token
        self.s_x_csrf_token = None
        # 当前登录后的cookie字符串
        self.s_cookies = None

    # 初始化driver 并打开
    def init_driver(self):
        if self.p_driver:
            return True
        self.p_driver = get_chrome_driver(self.s_driver_exe_dir)
        if not self.p_driver:
            return False
        self.p_driver.implicitly_wait(5)
        self.p_driver.get(self.s_request_url)
        self.p_driver.maximize_window()
        return True

    # 选择管理员 ID
    def _select_admin_id(self, s_current_admin_id):
        # 选择管理员ID
        s_admin_id_label = "div.accinfo"
        if not self._wait_element_and_click(s_admin_id_label, '选择管理ID', b_need_click=False):
            print(f'查找管理员ID控件失败.')
            return False

        l_admin_id_labels = self.p_driver.find_elements(
            By.XPATH, s_admin_id_label)
        for p_admin in l_admin_id_labels:
            log.debug(f"p_admin.text = {p_admin.text}")
            if s_current_admin_id not in p_admin.text:
                continue

            p_admin.click()
            break
        time.sleep(random.uniform(10, 15))
        return True

    # 获取指定的元素
    def get_find_element(self, s_element_xpath, p_driver=None, i_time_out=20, b_print=True):
        if not p_driver:
            p_driver = self.p_driver
        for i in range(3):
            try:
                p_element = WebDriverWait(
                    p_driver, i_time_out, 0.5).until(EC.presence_of_element_located((By.XPATH, s_element_xpath)))
                return p_element
            except Exception as p_error:
                if b_print:
                    print(f'第[{i + 1}/3]次定位到元素{s_element_xpath}失败-{p_error}')
        print(f'3次定位到元素{s_element_xpath}失败')
        return None

    # 移动页面到指定控件
    def move_to_index(self, s_element_xpath, s_name='', b_print=True):
        for i in range(3):
            try:
                p_element = self.get_find_element(s_element_xpath)
                if not p_element:
                    continue
                self.p_driver.execute_script(
                    "arguments[0].scrollIntoView();", p_element)
                log.info(f'滑动元素{s_name}({s_element_xpath})成功')
                return True
            except Exception as p_error:
                if b_print:
                    print(
                        f'第[{i + 1}/3]次滑动元素{s_name}{s_element_xpath}失败-({p_error})')
        print(f'3次滑动找元素{s_name}{s_element_xpath}失败！')
        return False

    # js类型点击按钮
    def click_js_button(self, s_element_xpath, s_name, b_print=True):
        for i in range(3):
            try:
                p_element = self.get_find_element(s_element_xpath)
                if not p_element:
                    continue
                self.p_driver.execute_script(
                    "arguments[0].click();", p_element)
                log.info(f'点击元素{s_name}-({s_element_xpath})成功')
                return True
            except Exception as p_error:
                if b_print:
                    print(
                        f'第[{i + 1}/3]次点击元素{s_name}-{s_element_xpath}失败-({p_error})')
        print(f'3次点击元素{s_name}-{s_element_xpath}失败！')
        return False

    def judge_element_exist(self, s_element_xpath, b_fast=False, i_timeout=20):
        return self._judge_element_exist(s_element_xpath, b_fast, i_timeout)

    # 判断元素是否存在
    def _judge_element_exist(self, s_element_xpath, b_fast, i_timeout=20):
        try:
            if b_fast:
                self.p_driver.find_element(By.XPATH, s_element_xpath)
                return True
            # self.p_driver.find_element_by_XPATH(s_element_xpath)
            WebDriverWait(self.p_driver, i_timeout, 0.5).until(
                EC.presence_of_element_located((By.XPATH, s_element_xpath)))
            return True
        except Exception as p_error:
            print(f'元素不存在-({s_element_xpath})-({p_error})')
            return False

    # 等待元素出现
    def wait_element(self, s_element_xpath, b_is_clickable=False, i_timeout=20, i_limit=3):
        p_web_driver_wait = WebDriverWait(self.p_driver, i_timeout, 0.5)
        s_wait_error = f"等待元素({s_element_xpath})出现失败"
        for i_times in range(i_limit):
            try:
                if b_is_clickable:
                    p_web_driver_wait.until(
                        EC.element_to_be_clickable((By.XPATH, s_element_xpath)))
                else:
                    p_web_driver_wait.until(
                        EC.presence_of_element_located((By.XPATH, s_element_xpath)))
                return True, None
            except Exception as wait_error:
                s_wait_error = f"{s_wait_error} - {wait_error}"
        return False, s_wait_error

    # 等待元素出现
    def wait_element_appear(
            self, s_element_xpath, s_element_des, i_timeout=20, b_need_click=True, b_need_refresh=False,
            p_index_type=False, b_delete=True, b_print=True):
        return self._wait_element_and_click(
            s_element_xpath, s_element_des, i_timeout, b_need_click, b_need_refresh, p_index_type, b_delete, b_print)

    # 等待元素出现并点击
    def _wait_element_and_click(
            self, s_element_xpath, s_element_des, i_timeout=20, b_need_click=True, b_need_refresh=False,
            p_index_type=False, b_delete=True, b_print=True):
        s_local_error = str()
        if not p_index_type:
            p_index_type = By.XPATH
        for i_times in range(3):
            try:
                if b_need_click:
                    WebDriverWait(self.p_driver, i_timeout, 0.5).until(
                        EC.element_to_be_clickable((p_index_type, s_element_xpath))).click()
                else:
                    if b_delete:
                        WebDriverWait(self.p_driver, i_timeout, 0.5).until(
                            EC.presence_of_element_located((p_index_type, s_element_xpath))).\
                            send_keys(Keys.CONTROL, "a")
                        WebDriverWait(self.p_driver, i_timeout, 0.5).until(
                            EC.presence_of_element_located((p_index_type, s_element_xpath))).send_keys(Keys.DELETE)
                    WebDriverWait(self.p_driver, i_timeout, 0.5).until(
                        EC.presence_of_element_located((p_index_type, s_element_xpath))).send_keys(s_element_des)

                time.sleep(random.uniform(3, 5) * i_times)
                log.info(f'点击或输入元素({s_element_des})-({s_element_xpath}))成功')
                return True

            except Exception as local_error:
                s_local_error = f"定位元素[{s_element_des}-{s_element_xpath}]失败 - {local_error}, {traceback.format_exc()}"
                s_local_warn = f"定位元素[{s_element_des}-{s_element_xpath}]失败 - {local_error}"
                if b_print:
                    print(s_local_warn)
                time.sleep(random.uniform(5, 10))
                # 刷新页面
                if b_need_refresh:
                    self.p_driver.refresh()
        print(s_local_error)
        return False

    # 等待元素消失
    def wait_element_disappear(self, s_element_xpath, i_timeout=20):
        try:
            WebDriverWait(self.p_driver, i_timeout, 0.5).until_not(
                EC.visibility_of_element_located((By.XPATH, s_element_xpath)))
            return True
        except TimeoutException:
            return False

    # 判断刷新框是否消失
    def is_hidden_refresh(self):
        s_refresh_label = "div.loading-indicator"

        # p_refresh_label = self.p_driver.find_element(By.XPATH, s_refresh_label)
        p_refresh_label = self.get_find_element(s_refresh_label)
        if not p_refresh_label:
            return True
        # 等待刷新图片的消失
        for i_times in range(15):
            # 说明当前刷新图标已经消失
            if p_refresh_label.get_attribute('hidden') == 'true':
                return True
            time.sleep(random.uniform(0, 1) * i_times)

        return False

    # # 请求网站的 X-CSRF-Token
    # def request_x_csrf_token(self, d_headers):
    #     s_request_x_csrf_token_url = "https://svc-dra.ads.huawei.com/ppsdspportal/v1/csrftoken/query"
    #     d_headers["Cookie"] = self.get_request_cookie()
    #     return requests_logic.requests_post(s_request_x_csrf_token_url, None, d_headers)

    # 获取请求的cookie
    def get_request_cookie(self):
        l_cookies = self.p_driver.get_cookies()
        s_cookies = str()
        for d_cookie in l_cookies:
            s_cookies += f"{d_cookie['name']}={d_cookie['value']};"
        self.s_cookies = s_cookies.strip(";")
        return self.s_cookies


# 检测是否登陆成功
def _check_land(p_selenium_use):
    # 判断元素存在
    s_element_xpath = "//li[text()='密码登录']"
    p_selenium_use.p_driver.implicitly_wait(1)
    while True:
        if p_selenium_use.judge_element_exist(s_element_xpath, i_timeout=5):
            print('当前未登录，请扫码登录对应的账户！')
            time.sleep(5)
        else:
            break
    p_selenium_use.p_driver.implicitly_wait(5)
    log.info('检测到登陆成功！')
    time.sleep(5)


def login_info(p_selenium_use):
    print('开始执行登陆')
    s_xpath_route = '//*[@id="_7hLtYmO"]/button'
    if p_selenium_use.judge_element_exist(s_xpath_route, i_timeout=5):
        if not p_selenium_use.wait_element_appear(s_xpath_route, '点击登陆'):
            print(f'点击登陆失败！')
            return False, f'点击登陆失败！'
        # 检测登陆
        _check_land(p_selenium_use)
    print('已完成登陆')


def go_self_info(p_selenium_use):
    s_xpath_route = '//*[@id="douyin-header"]/div[1]/header/div/div/div[2]/div/div/div[7]/div/a'
    if not p_selenium_use.wait_element_appear(s_xpath_route, '点头像'):
        print(f'点击头像失败！')
        return False, f'点击头像失败！'
    s_xpath_route = "//div[text()='关注']"
    if not p_selenium_use.click_js_button(s_xpath_route, '点击关注按钮'):
        print(f'点击关注按钮失败！')
        return False, f'点击关注按钮失败！'

    s_xpath_route = '/html/body/div[3]/div/div/div[2]/div/div[4]/div[1]/div'
    l_people = p_selenium_use.p_driver.find_elements(
        By.XPATH, s_xpath_route)
    print(len(l_people))
    for i in range(len(l_people)):
        x_now = 1 + 3 * i
        s_xpath_route = f'/html/body/div[3]/div/div/div[2]/div/div[4]/div[1]/div[{x_now}]/div[2]/div[1]/div[1]/a/span/span/span/span/span/span'
        # print(s_xpath_route)
        l_admin_id_labels = p_selenium_use.p_driver.find_elements(
            By.XPATH, s_xpath_route)
        if l_admin_id_labels:
            print(f'{x_now}')
            s_now_name = l_admin_id_labels[0].text
            print(f's_now_name={s_now_name}')
            s_xpath_route = f'/html/body/div[3]/div/div/div[2]/div/div[4]/div[1]/div[{x_now}]/div[2]/div[1]/div[2]/span'
            l_admin_id_labels = p_selenium_use.p_driver.find_elements(
                By.XPATH, s_xpath_route)
            if not l_admin_id_labels:
                s_now_info = ''
            else:
                s_now_info = l_admin_id_labels[0].text
            print(f's_now_info = {s_now_info}')
            s_xpath_route = f'/html/body/div[3]/div/div/div[2]/div/div[4]/div[1]/div[{x_now}]/div[2]/div[2]/span/span/span/span/span/span'
            l_admin_id_labels = p_selenium_use.p_driver.find_elements(
                By.XPATH, s_xpath_route)
            if not l_admin_id_labels:
                s_now_title = ''
            else:
                s_now_title = l_admin_id_labels[0].text

            print(f's_now_title = {s_now_title}')

    # s_xpath_route = '/html/body/div[4]/div/div/div[2]/div/div[4]'
    # if not p_selenium_use.click_js_button(s_xpath_route, '点击窗口'):
    #     print(f'点击窗口失败！')
    #     return False, f'点击窗口失败！'
    # # 下拉到底
    # s_xpath_route = "//div[text()='暂时没有更多了']"
    # if not p_selenium_use.move_to_index(s_xpath_route, '暂时没有更多了'):
    #     return False

    time.sleep(10000)


# 流程
def main_step():
    # 打开推广界面
    s_url_tencent = f'https://www.douyin.com/'
    # 打开浏览器
    print(222)
    p_selenium_use = SeleniumUse(s_request_url=s_url_tencent)

    time.sleep(3)
    if not p_selenium_use.init_driver():
        print(f'初始化driver对象失败！')
        return
    # 登陆
    login_info(p_selenium_use)
    # 登陆动作
    # 进入个人中心
    go_self_info(p_selenium_use)
    p_selenium_use.p_driver.close()
    p_selenium_use.p_driver.quit()


if __name__ == '__main__':
    main_step()
