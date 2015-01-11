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

    def getPage(self, url, mCWebRender):
        self.url = url
        mCWebRender.get(url)

    def nextPage(self, mCWebRender):
        '''
        Get the next page comment.
        '''
        pagerModules = mCWebRender.find_elements_by_xpath("//div[@class='pager-inner']")
        if len(pagerModules) == 0: return False
        nextpage = pagerModules[0].find_elements_by_xpath("//h4[@class='next pn-item']")
        if len(nextpage) == 0:
            return False
        nextpage[0].click()
        time.sleep(3)
        return True

    def getCommentUsers(self, commentModule):
        '''
        Get the commenter for this article.
        '''
        commentUsers = commentModule.find_elements_by_xpath("li[@class='ct-item']")
        users = []
        for userModule in commentUsers:
            # print person.text
            #time.sleep(1)
            user_id = int(userModule.get_attribute("data-reply-id"))
            dayModule = userModule.find_element_by_xpath("div[@class='ct-extra-into']")
            day = dayModule.find_element_by_xpath("p").text
            scoreModule = userModule.find_elements_by_xpath("b[@class='ic-star-score star-score-on']")
            score = len(scoreModule)
            users.append((user_id, day, score))
        return users

    def getAllComment(self, mCWebRender):
        '''
        Get all the pages comments.
        '''
        commentModule = mCWebRender.find_elementss_by_id("doc-comment")
        if len(commentModule) == 0: return False
        users = self.getCommentUsers(commentModule)
        while True:
            if not self.nextPage(mCWebRender):
                break
            users.extend(self.getCommentUsers(commentModule))
        return users

def getResources(db, itemsNum):
    '''
    3: represent being crawling the comments.
    4: represent be crawled the comments.
    '''
    sql = 'select resource_id, href from resources where flag != 4 and flag !=3 LIMIT %d ' %  itemsNum
    resources = db.InquiryTb(sql)
    if len(resources) == 0:
        return False
    sql = 'update resources set flag = 3 where resource_id=%d'
    for i in range(itemsNum):
        db.UpdateTb(sql % resources[i]['resource_id'])
    return resources

def main(itemsNum):
    db = connectDb()
    mCWebRender = CWebRender()
    mCWenkuPage = CWenkuPage()
    url = 'http://wenku.baidu.com'
    insertSQL = 'insert into comment(user_id, resource_id, score, time) values(%s, %s, %s, %s)'
    while True:
        resources = getResources(db, itemsNum)
        if not resources: break
        for resource in resources:
            print resource['resource_id']
            num = 0
            while True:
                mCWenkuPage.getPage(url+resource['href'], mCWebRender)
                users = mCWenkuPage.getAllComment(mCWebRender)
                num += 1
                if users is False:
                    time.sleep(30)
                if len(users) == 0 or num > 20:
                    break
            updateSQL = 'update resources set flag=4 where resource_id=%d' % resource['resource_id']
            db.UpdateTb(updateSQL)
            values = [(user[0], resource['resource_id'], user[1], user[2]) for user in users]
            db.InsertTb(insertSQL, values)
    mCWebRender.closeUrl()
    db.CloseDb()

if __name__ == '__main__':
    main(100)

