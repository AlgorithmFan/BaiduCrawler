#!usr/bin/env python
#coding:utf-8

from Database import CDatabase
from CommonModules import connectDb, getUrlSource
from BeautifulSoup import BeautifulSoup
import time

def getSoup(url):
    num = 0
    while True:
        time.sleep(2)
        html = getUrlSource(url)
        if len(html) != 0 or num >20:
            print 'Wrong:\t', url
            break
    soup = BeautifulSoup(html)
    return soup

def getLessons(db, itemsNum):
    sql = 'select lesson_id, book_id, href from lessons where flag = 0 and href not like "%%/portal%%" LIMIT %d ' %  itemsNum
    lessons = db.InquiryTb(sql)
    if len(lessons) == 0:
        return False
    return lessons

def readHrefPage(url):
    soup = getSoup(url)
    docListSoup = soup.findAll("div", {"class": "doc-list"})
    if len(docListSoup) == 0:
        return False
    Hrefs = []
    hrefSoups = docListSoup[0].findAll("div", {"class": "doc-list-title"})
    for hrefSoup in hrefSoups:
        aSoups = hrefSoup.findAll("a", {"title": True, "href": True})
        if len(aSoups) == 0:    continue
        title, href = '', ''
        for aSoup in aSoups:
            for tag, value in aSoup.attrs:
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


def readHrefLesson(lesson_id, url):
    '''
    Read hrefs associated with the lesson
    '''
    values = []
    for i in range(1, 4):
        lesson_url = url + '&stype=%d&order=0' % i
        temp = readHrefPages(lesson_url)
        values.extend( [(lesson_id, title, href, i) for title, href in temp])
    return values


def main(coreNum, itemsNum):
    db = connectDb()
    while True:
        lessons = getLessons(db, itemsNum)
        if not lessons: break

        InsertSQL = 'insert into resources(lesson_id, title, href, type)  values(%s, %s, %s, %s)'
        UpdateSQL = 'update lessons set flag = %d where lesson_id=%d'
        for i in range(len(lessons)):
            sql = 'select href from books where book_id=%d' % lessons[0]['book_id']
            books = db.InquiryTb(sql)
            url = 'http://wenku.baidu.com' + books[0]['href'] + lessons[0]['href']
            values = readHrefLesson(lessons[i]['lesson_id'], url)
            db.InsertTb(InsertSQL, values)
            db.UpdateTb(UpdateSQL % (1, lessons[0]['lesson_id']))

    db.CloseDb()

if __name__ == '__main__':
    coreNum =4
    main(coreNum,1)

