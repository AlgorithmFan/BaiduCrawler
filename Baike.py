#!usr/bin/env python
#coding:utf-8

from CommonModules import getUrlSource, connectDb
from BeautifulSoup import BeautifulSoup
from multiprocessing import process, Pool
import copy_reg
import types
import time

MaxIteration = 10665788     #20000000


def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

def getSoup(url):
    num = 0
    while True:
        html = getUrlSource(url)
        if len(html) != 0:
            print 'Right:\t', url
            break
        elif num <=5:
            time.sleep(5)
            num += 1
        elif num > 5:
            print 'Wrong:\t', url
            break
    soup = BeautifulSoup(html)
    return soup


def multiHrefs(url):
    '''
    多个网址的，如http://baike.baidu.com/view/19251.htm，上海滩
    子网址有很多，如http://baike.baidu.com/subview/160234/6305613.htm?fromtitle=上海滩&fromid=374655&type=syn
    '''
    soup = getSoup(url)

class CSinglePage():
    def __init__(self):
        self.url = ''

    def getStructure(self, url):
        '''
        Get the structure of a url.
        '''
        self.url = url
        soup = getSoup(url)
        bodytSoups = soup.findAll("div", {"class":"content-bd main-body"})
        if len(bodytSoups) == 0:  return False
        title = self.getTitle(bodytSoups[0])
        modtop = self.getModTop(bodytSoups[0])
        baseInfo = self.getBaseInfo(bodytSoups[0])
        contentSoups = soup.findAll("div", {"id":"lemmaContent-0"})
        if len(contentSoups) == 0:  return False
        content = self.getContent(contentSoups[0])
        imageSoups = soup.findAll("div", {"class":"bacb-window-outer"})
        imageAddr = self.getImg(imageSoups)
        return {'title':title, 'modtop':modtop, 'baseInfo':baseInfo, 'content':content, 'imageAddr':imageAddr}


    def getTitle(self, soup):
        '''
        Get the title of url
        <h1 class="title maintitle">
        <span class="lemmaTitleH1">
        '''
        titleSoup = soup.findAll("span", {"class":"lemmaTitleH1"})
        if len(titleSoup):
            return titleSoup[0].getText()
        else:
            return ''

    def getModTop(self, soup):
        '''
        Get the mod top of url, i.e. the module followed by title.
        <div class="mod-top" id="card-container">
        '''
        modTopSoup = soup.findAll("div", {"class":"card-summary-content"})
        if len(modTopSoup):
            return modTopSoup[0].getText()
        else:
            return ''

    def getBaseInfo(self, soup):
        '''
        Get the base information of url.
        <div class="baseInfoWrap" id="baseInfoWrapDom">
        '''
        modTopSoup = soup.findAll("div", {"class":"baseInfoWrap"})
        if len(modTopSoup):
            return unicode(modTopSoup[0])
        else:
            return ''

    def getContent(self, soup):
        '''
        Get the content of url.
        <h2 class="headline-1">
        <div class="para">
        '''
        headSoups = soup.findAll("h2", {"class":"headline-1"})
        picFormat = {'class':set(["lemma-picture text-pic layout-right",
                                 "lemma-picture text-pic layout-center",
                                 "lemma-picture text-pic layout-left",
                                 "lemma-album layout-right nslog:10000206"])}
        content = {}
        for i in range(len(headSoups)-1):
            content[i] = {'head':headSoups[i].getText()}
            while headSoups[i].next_sibling != headSoups[i+1]:
                break




    def getImg(self, soup):
        '''
        Get the images of url.
        '''





def test():
    ''''''
    url = 'http://baike.baidu.com/subview/119807/13366726.htm#9'
    mCSinglePage = CSinglePage()
    mCSinglePage.getStructure(url)

def main():
    ''''''


if __name__ == '__main__':
    #main()
    test()
