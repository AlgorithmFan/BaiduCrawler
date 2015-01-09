#!usr/bin/env python
#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.proxy import *

class CWebRender(webdriver.Firefox):
    def __init__(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.http', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.http_port', 8080)
        profile.set_preference('network.proxy.ssl', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        #profile.set_preference('network.proxy.ssl_port', 8080)
        profile.update_preferences()
        webdriver.Firefox.__init__(self, profile)

    def closeUrl(self):
        self.close()
        self.quit()