#!usr/bin/env python
#coding:utf-8

from WebRender import CWebRender
import re

class CSinglePage():
    def __init__(self):
        self.url = ''

    def getPage(self, url, mCWebRender):
        self.url = url
        mCWebRender.get(url)

    def getInner(self, mCWebRender):
        contentModules = mCWebRender.find_elements_by_xpath("//div[@class='bd doc-reader']")
        if len(contentModules) == 0:
            print 'False'
            return False
        for c in contentModules:
            print c
            print c.text

    def getPPTContent(self, mCWebRender):
        text = list()
        pageNum = 1
        while True:
            try:
                element = mCWebRender.find_element_by_id('pageNo-%d' % pageNum)
                text.append(element.text)
                pageNum = pageNum + 1
                element.click()
            except:
                print 'over %d' % pageNum
                return text
        return text


def main():
    url = 'http://wenku.baidu.com/view/968937255901020207409c54'
    #url = 'http://wenku.baidu.com/view/7c9d96edb8f67c1cfad6b879.html'
    mCWebRender = CWebRender()
    mCSinglePage = CSinglePage()
    mCSinglePage.getPage(url, mCWebRender)
    text = mCSinglePage.getPPTContent(mCWebRender)
    print text
    mCSinglePage.getInner(mCWebRender)
    #result = mCWebRender.find_element_by_class("inner")
    #print result.text
    mCWebRender.closeUrl()

if __name__=='__main__':
    main()