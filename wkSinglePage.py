#!usr/bin/env python
#coding: utf-8

import re
import urllib
from CommonModules import getUrlSource
from BeautifulSoup import BeautifulSoup
from lxml import etree
from lxml.etree import tostring
import time

class CWKCrawler():
    def __init__(self):
        ''''''

    def getContentLXML(self, url):
        ''''''
        mSourceCode = getUrlSource(url)
        if len(mSourceCode) == 0:
            return False
        page = etree.HTML(mSourceCode)
        titleModules = page.xpath("//div[@class='at_c']")
        #Read title
        if len(titleModules):
            title = titleModules[0].text
        else:
            title = ''

        #Read Content
        content = ''
        try:
            num = 1
            while True:
                mContentModules = page.xpath("//body/div[@class='ptb45 bgcolor1 xreader']")
                for cm in mContentModules:
                    temp = "".join([x for x in cm.itertext()])
                    content += temp
                num += 1
                if num>200:  break
                href = self.nextpage(url, num)
                mSourceCode = getUrlSource(href)
                if len(mSourceCode) == 0: break
                page = etree.HTML(mSourceCode)
        except:
            print 'Wrong contentAnalysis: ', url
        return {'title' : title, 'content' : content}

    def getContentBS(self, url):
        time.sleep(2)
        mSourceCode = getUrlSource(url)
        if len(mSourceCode) == 0:
            return False
        soup = BeautifulSoup(mSourceCode)
        #Read title
        title = soup.find("div",{"class":"at_c"})
        title = '' if title is None else title.text

        #Read Content
        content = ''
        try:
            num = 1
            while True:
                temp = soup.find("div",{"class":"ptb45 bgcolor1 xreader"})
                if temp is None:  break
                content = '%s%s' % (content, temp.text)
                num += 1
                if num>200:
                    break
                href = self.nextpage(url, num)
                html = getUrlSource(href)
                if len(html) == 0:
                    break
                soup = BeautifulSoup(html)
        except:
            print 'Wrong contentAnalysis: ', url
        return {'title' : title, 'content' : content}

    def nextpage(self, url, num):
        temp = url.split('ssid=')
        temp = temp[0]+('?pn=%d&ssid=' % num)
        temp = temp+'&from=&bd_page_type=1&uid=94443DC68365BC3032E299D5D78D397F&pu=rc@1,pic@on,sl@1,pw@1000,sz@224_220,pd@1,fz@2,lp@2,tpl@color,&st=1&wk=rd&maxpage=200&pos=next'
        return temp


def main():
    #url = 'http://wk.baidu.com/view/968937255901020207409c54'
    #url = 'http://wk.baidu.com/view/ba02504d4a7302768f993933.html'
    url = 'http://wk.baidu.com/view/d64fbe5b581b6bd97f19eafd'
    mCWKCrawler = CWKCrawler()
    # content = mCWKCrawler.getContentLXML(url)
    # if content:
    #     print content['title'], content['content']
    # else:
    #     print 'False'
    # print '*' * 100
    content = mCWKCrawler.getContentBS(url)
    print content['content']
    # if content:
    #     print content['title'], content['content']
    # else:
    #     print 'False'

if __name__=='__main__':
    import profile
    profile.run('main()')
    #main()

