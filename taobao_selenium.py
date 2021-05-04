#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Version   : 1.0  2021.3.3    初步实现自动提交订单功能
@Version   : 1.1  2021.3.4    1、实现过滑；2、增加自动付款功能
@Version   : 1.2  2021.3.5    1、优化“订单提交”按钮查找方式，并尝试连续点击2次；2、到点打开页面修改为页面刷新，更稳定；
"""

import time
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException


class TaobaoSelenium:
    def __init__(self):
        # 初始化所需对象
        self.id = ''
        self.pwd = ''
        self.pay_pwd = ''
        self.order_link = 'https://h5.m.taobao.com/cart/order.html?buyParam='
        self.item_num = 0
        self.buy_time = ''
        self.if_auto_pay = False
        self.seconds_pre = 0.05
        # 初始化浏览器参数
        chrome_options = webdriver.ChromeOptions()
        # 取消自动化控制提示
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 禁用默认浏览器检测
        chrome_options.add_argument('no-default-browser-check')
        # 窗口最大化
        chrome_options.add_argument('start-maximized')
        # 禁用密码保存提示
        prefs = {'credentials_enable_service': False, 'profile.password_manager_enabled': False}
        chrome_options.add_experimental_option("prefs", prefs)
        # 页面模拟为iPhoneX
        # '''
        mobile_emulation = {'deviceName': 'iPhone X'}
        chrome_options.add_experimental_option('mobileEmulation', mobile_emulation)
        user_agent_iphone_x = 'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) ' \
                              'AppleWebKit/605.1.15(KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"'
        chrome_options.add_argument(user_agent_iphone_x)
        '''
        # 页面模拟为chrome
        user_agent_chrome = 'user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like ' \
                            'Gecko) Chrome/88.0.4324.190 Safari/537.36"'
        chrome_options.add_argument(user_agent_chrome)
        '''
        # 启动浏览器
        self.browser = webdriver.Chrome(options=chrome_options)
        # selenium隐藏自动控制命令，跳过滑块验证
        self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})

    # 获取登陆模式
    def get_user_input(self):
        choose_login = input('请选择登录方式：1、扫码登录；2、账号密码登录\n')
        if_auto_pay = input('请选择是否自动付款：1、是；2、否\n')
        if if_auto_pay == '1':
            self.if_auto_pay = True
            self.get_pay_pwd()
        if choose_login == '1':
            self.login_by_scan()
        elif choose_login == '2':
            self.get_id_pwd()
        else:
            print('登录方式选择有误！')
            self.get_user_input()

    # 获取是否自动支付
    def get_pay_pwd(self):
        pay_pwd = input('请输入支付密码：')
        try:
            int(pay_pwd)
            if len(pay_pwd) == 6:
                self.pay_pwd = pay_pwd
            else:
                print('输入有误，请重试')
                self.get_pay_pwd()
        except ValueError:
            print('输入有误，请重试')
            self.get_pay_pwd()

    # 获取用户输入账号/密码
    def get_id_pwd(self):
        self.id = input('请输入账号：')
        self.pwd = input('请输入密码：')
        self.login_by_pwd()

    # 扫码登录
    def login_by_scan(self):
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        self.browser.get('https://login.taobao.com/member/login.jhtml')
        print('请在30秒内完成扫码登录')
        time.sleep(30)
        if self.browser.title == '我的淘宝':
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + '：登陆成功!')
            self.get_item_num()
        else:
            print('未检测到登录，请重试')
            self.login_by_scan()

    # 配置用户名密码自动登录
    def login_by_pwd(self):
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        self.browser.get('https://login.taobao.com/member/login.jhtml')
        try:
            self.browser.find_element_by_id('fm-login-id').clear()
            time.sleep(1)
            self.browser.find_element_by_id('fm-login-id').send_keys(self.id)
            time.sleep(0.5)
            self.browser.find_element_by_id('fm-login-password').clear()
            time.sleep(1)
            self.browser.find_element_by_id('fm-login-password').send_keys(self.pwd)
            time.sleep(2)
            self.browser.find_element_by_xpath('//*[text()="登录"]').click()
            # 使用页面title验证是否登录成功
            # 也可使用url验证(网页模式'i.taobao.com'/手机模式'h5.m.taobao.com' in self.browser.current_url)
            for i in range(5):
                time.sleep(1)
                if '我的淘宝' == self.browser.title:
                    print('登录成功!' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                    break
            self.get_item_num()
        except NoSuchElementException:
            print('未找到输入框，3秒后自动刷新重试')
            time.sleep(3)

    # 获取购买商品种数
    def get_item_num(self):
        item_num = input('请输入欲抢购商品种数：')
        try:
            self.item_num = int(item_num)
            self.get_buy_items()
        except ValueError:
            print('非正确数字，请重新输入')
            self.get_item_num()

    # 获取商品id，skuId
    def get_buy_items(self):
        for num in range(self.item_num):
            if num > 0:
                self.order_link = self.order_link + ','
            buy_item_link = input(f'请输入第{num + 1}件欲购商品链接：')
            params = buy_item_link.split('?')[1]
            buy_item = {'id': '', 'skuId': '0'}
            for param in params.split('&'):
                if param.split('=')[0] in buy_item:
                    buy_item[param.split('=')[0]] = param.split('=')[1]
            self.order_link = self.order_link + buy_item['id'] + '_1_' + buy_item['skuId']
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + '：抢购链接为：' + self.order_link)
        self.get_buy_time()

    # 获取抢购时间
    def get_buy_time(self):
        buy_time = input('请输入抢购时间，以“10:00”的格式：') + ':00.0'
        try:
            if buy_time != '00:00':
                buy_time = datetime.datetime.strptime(buy_time, '%H:%M:%S.%f') - datetime.timedelta(
                    seconds=self.seconds_pre)
            else:
                buy_time = datetime.datetime.strptime(buy_time, '%H:%M:%S.%f') + datetime.timedelta(
                    days=1, seconds=-self.seconds_pre)
            self.buy_time = datetime.datetime.now().strftime('%Y-%m-%d') + ' ' + buy_time.strftime('%H:%M:%S.%f')
            print('预计抢购开始时间为：' + self.buy_time)
            self.time_count_down()
        except ValueError:
            print('时间输入错误，请重新输入！')
            self.get_buy_time()

    # 开始倒计时
    def time_count_down(self):
        self.buy_time = datetime.datetime.strptime(self.buy_time, '%Y-%m-%d %H:%M:%S.%f')
        now = datetime.datetime.now()
        # 判断离开始是否还有20分钟，若是，每15分钟刷新一次保持登录状态
        while (self.buy_time - now).seconds > 1200:
            time.sleep(900)
            now = datetime.datetime.now()
            self.browser.refresh()
        # 判断是否距离5分钟
        while (self.buy_time - now).seconds > 300:
            time.sleep(300)
            now = datetime.datetime.now()
        # 判断是否开始前40秒，每15秒判断一次
        while (self.buy_time - now).seconds > 40:
            time.sleep(15)
            now = datetime.datetime.now()
        # 离开始不到30秒，预加载购买页面，提高访问速度
        self.browser.get(self.order_link)
        print('预加载页面，提高访问速度：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        # 离开时不到2秒，每秒判断一次
        while (self.buy_time - now).seconds > 2:
            time.sleep(1)
            now = datetime.datetime.now()
        # 准备开始抢购
        while self.buy_time > now:
            now = datetime.datetime.now()
        self.auto_buy()

    # 开始抢购
    def auto_buy(self):
        print('开始抢购：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        self.browser.refresh()
        while True:
            try:
                # 间隔50ms尝试一次点击，共尝试5次
                for try_count in range(5):
                    if 'buyParam' in self.browser.current_url:
                        print('尝试提交订单：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                        self.browser.find_element_by_xpath('//*[text()="提交订单"]').click()
                        time.sleep(0.05)
                    else:
                        break
                break
                # self.browser.quit()
            except NoSuchElementException:
                print('未找到下单按钮')
            except ElementNotInteractableException:
                print('按钮不可点击')
        self.auto_pay()

    def auto_pay(self):
        while True:
            try:
                self.browser.find_element_by_xpath('//*[contains(text(),"确认付款")]').click()
                print('成功提交订单：' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                break
            except NoSuchElementException:
                print('未成功自动付款')
                time.sleep(0.02)
            except ElementNotInteractableException:
                print('按钮不可点击')
                time.sleep(0.02)
        if self.pay_pwd != '':
            while True:
                try:
                    self.browser.find_element_by_xpath("//*[@id='pwd_unencrypt']").send_keys(self.pay_pwd)
                    break
                except NoSuchElementException:
                    print('未找到密码输入框')


if __name__ == '__main__':
    print('Taobao')

