#!usr/bin/env python
#coding:utf-8

import re
import time
from WebRender import CWebRender
from Database import CDatabase
from CommonModules import connectDb

class CWenkuPage():
    def __init__(self):
        ''''''
        self.url = ''

    def getPage(self, url, mCWebRender):
        self.url = url
        try:
            num = 1
            while True:
                mCWebRender.get(url)
                comments = mCWebRender.find_elements_by_xpath("//div[@id='doc-comment']")
                if len(comments) != 0:
                    break
                elif num > 5:
                    break
                else:
                    num += 1
                    time.sleep(20)
            return True
        except:
            return False


    def nextPage(self, mCWebRender):
        '''
        Get the next page comment.
        '''
        pagerModules = mCWebRender.find_elements_by_xpath("//div[@class='pager-inner']")
        if len(pagerModules) == 0: return False
        nextpage = pagerModules[0].find_elements_by_xpath("a[@class='next pn-item']")
        if len(nextpage) == 0:
            return False
        nextpage[0].click()
        time.sleep(3)
        return True

    def getCommentUsers(self, mCWebRender):
        '''
        Get the commenter for this article.
        '''
        users = []
        commentUsers = mCWebRender.find_elements_by_xpath("//ul[@id='comment-list']")
        if len(commentUsers) == 0: return users
        userModules = commentUsers[0].find_elements_by_xpath("li[@class='ct-item']")
        for userModule in userModules:
            # print person.text
            #time.sleep(1)
            user_id = userModule.get_attribute("data-reply-id")
            if len(user_id) > 0:
                user_id = int(user_id)
            else:
                continue
            dayModule = userModule.find_elements_by_xpath("div/div/div[@class='ct-extra-into']")
            if len(dayModule):
                day = dayModule[0].find_element_by_xpath("p").text
            else:
                day = ''
            scoreModule = userModule.find_elements_by_xpath("div/div/div/div/p/span/b[@class='ic-star-score star-score-on']")
            score = len(scoreModule)
            users.append((user_id, day, score))
        return users

    def getAllComment(self, mCWebRender):
        '''
        Get all the pages comments.
        '''
        users = self.getCommentUsers(mCWebRender)
        while True:
            try:
                if not self.nextPage(mCWebRender):
                    break
                users.extend(self.getCommentUsers(mCWebRender))
            except:
                self.getPage(self.url, mCWebRender)
        return users

def getResources(db, itemsNum):
    '''
    3: represent being crawling the comments.
    4: represent be crawled the comments.
    '''
    sql = 'select resource_id, href from resources where flag = 2 LIMIT %d ' %  itemsNum
    resources = db.InquiryTb(sql)
    if len(resources) == 0:
        return False
    sql = 'update resources set flag = 3 where resource_id=%d'
    for i in range(len(resources)):
        db.UpdateTb(sql % resources[i]['resource_id'])
    return resources

def test():
    mCWebRender = CWebRender()
    mCWenkuPage = CWenkuPage()
    #url = 'http://wenku.baidu.com/view/54be8d6b0912a21615792935.html?fr=gaokao'
    url = 'http://wenku.baidu.com/view/fa4ef92d915f804d2b16c197.html?re=view'
    #insertSQL = 'insert into comment(user_id, resource_id, score, time) values(%s, %s, %s, %s)'
    mCWenkuPage.getPage(url, mCWebRender)
    users = mCWenkuPage.getAllComment(mCWebRender)
    mCWebRender.closeUrl()


def main(itemsNum):
    db = connectDb()
    mCWebRender = CWebRender()
    mCWenkuPage = CWenkuPage()
    url = 'http://wenku.baidu.com'
    insertSQL = 'insert into comment(user_id, resource_id, score, time) values(%s, %s, %s, %s)'
    while True:
        resources = getResources(db, itemsNum)
        if not resources:
            fp = open('flag.txt', 'r')
            flag = cPickle.load(fp)
            fp.close()

            if flag == 0:
                break
            else:
                print 'Sleep: ', time.localtime()
                db.CloseDb()
                time.sleep(600)
                print 'Wake up:', time.localtime()
                db = connectDb()
                continue
        for resource in resources:
            print resource['resource_id']
            flag = mCWenkuPage.getPage(url+resource['href'], mCWebRender)
            if not flag:
                continue
            users = mCWenkuPage.getAllComment(mCWebRender)

            updateSQL = 'update resources set flag=4 where resource_id=%d' % resource['resource_id']
            db.UpdateTb(updateSQL)
            values = [(user[0], resource['resource_id'], user[1], user[2]) for user in users]
            db.InsertTb(insertSQL, values)
    mCWebRender.closeUrl()
    db.CloseDb()

if __name__ == '__main__':
    import cPickle
    main(100)
    #test()

