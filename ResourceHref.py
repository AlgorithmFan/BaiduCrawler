#!usr/bin/env python
#coding:utf-8

from multiprocessing import process, Pool
from Database import CDatabase
from CommonModules import connectDb, getUrlSource
from BeautifulSoup import BeautifulSoup
import time
import copy_reg
import types

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

def getSoup(url):
    num = 0
    while True:
        time.sleep(1)
        html = getUrlSource(url)
        if len(html) != 0 or num >20:
            break
    soup = BeautifulSoup(html)
    return soup

def readUrl(db):
    sql = 'select lesson_id, book_id, href from lessons where flag = 0 and href not like "%/portal%" LIMIT 1 '
    lessons = db.InquiryTb(sql)
    if len(lessons) == 0:
        return False, False
    sql = 'update lessons set flag = %d where lesson_id=%d' % (1, lessons[0]['lesson_id'])
    db.UpdateTb(sql)
    sql = 'select href from books where book_id=%d' % lessons[0]['book_id']
    books = db.InquiryTb(sql)
    url = 'http://wenku.baidu.com' + books[0]['href'] + lessons[0]['href']
    return lessons[0]['lesson_id'], url

def readHrefPage(url):
    soup = getSoup(url)
    docListSoup = soup.findAll("div", {"class": "doc-list"})
    if len(docListSoup) == 0:
        return False
    Hrefs = []
    hrefSoups = docListSoup[0].findAll("a", {"title": True, "href": True})
    for hrefSoup in hrefSoups:
        title, href = '', ''
        for tag, value in hrefSoup.attrs:
            if tag == 'title':
                title = value
            elif tag == 'href':
                href = value
        if len(title) != 0 and (len(href) != 0):
            Hrefs.append((title, href))
    return Hrefs

def readHrefPages(url):
    page = 1
    Hrefs = []
    while True:
        lesson_url = url + '&page=%d' % page
        temp = readHrefPage(lesson_url)
        if not temp:
            break
        Hrefs.extend(temp)
        page += 1
    return Hrefs

def readHrefLesson(db, lesson_id, url):
    '''
    Read hrefs associated with the lesson
    '''
    sql = 'insert into resources(lesson_id, title, href, type)  values(%s, %s, %s, %s)'
    for i in range(1, 4):
        lesson_url = url + '&stype=%d&order=0' % i
        values = readHrefPages(lesson_url)
        values = [(lesson_id, title, href, i) for title, href in values]
        db.InsertTb(sql, values)
    sql = 'update lessons set flag = %d where lesson_id=%d' % (2, lesson_id)
    db.UpdateTb(sql)

class CPoolFunc():
    def __init__(self, coreNum):
        self.coreNum = coreNum

    def go(self):
        db = connectDb()
        flag = 1
        while True:
           # flag = poolFunc(db)

            pool = Pool(processes=self.coreNum)
            results = {}
            for i in xrange(10000):
                results[i] = pool.apply_async(poolFunc, args=(db,))
            pool.close()
            pool.join()

            for i in results:
                temp = results[i].get()
                if not temp:
                    flag = 0
                    break
            if flag == 0:
                break

        db.CloseDb()


def poolFunc(db):
    lesson_id, url = readUrl(db)
    if not lesson_id:
        return False
    print 'lesson id: ', lesson_id
    readHrefLesson(db, lesson_id, url)
    return True

def main(coreNum):
    # mCPoolFunc = CPoolFunc(coreNum)
    # mCPoolFunc.go()
    #
    db = connectDb()
    flag = 1
    while True:
        flag = poolFunc(db)

        pool = Pool(processes=coreNum)
        results = {}
        for i in xrange(10000):
            results[i] = pool.apply_async(poolFunc, args=(db,))
        pool.close()
        pool.join()

        for i in results:
            temp = results[i].get()
            if not temp:
                flag = 0
                break
        if flag == 0:
            break

    db.CloseDb()

if __name__ == '__main__':
    coreNum =4
    main(coreNum)

