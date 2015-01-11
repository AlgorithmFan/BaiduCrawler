#!usr/bin/env/python
#coding: utf-8

from CommonModules import getUrlSource, connectDb
from BeautifulSoup import BeautifulSoup
import re
import time
from Database import CDatabase

bookPattern = re.compile('(\d+)_s(\d+)_g(\d+)_v(\d+)')

def getSoup(url):
    num = 0
    while True:
        time.sleep(1)
        html = getUrlSource(url)
        if len(html) != 0 or num >20:
            break
        num += 1
    soup = BeautifulSoup(html)
    return soup

def getBookSoups(soup):
    selectSoup = soup.find("div", {"id": "select-all"})
    bookSoups = selectSoup.findAll("div", {"class":"sel-list"})
    if len(bookSoups) != 3:   return False
    return bookSoups

def getAttrsHref(hrefSoups):
    Hrefs = set()
    for hrefSoup in hrefSoups:
        for tag, value in hrefSoup.attrs:
            if tag == 'href':
                Hrefs.add(value)
    return Hrefs

def getSoupHrefs(soup):
    hrefSoups = soup.findAll('a')
    Hrefs = getAttrsHref(hrefSoups)
    return Hrefs

def getSelectBook(soup):
    selectSoup = soup.find("div", {"id": "select-all"})
    selectBookSoup = selectSoup.findAll("li", {"class":"selected"})
    book = []
    for select in selectBookSoup:
        temp = select.find('a')
        if temp is None:    continue
        for tag, value in temp.attrs:
            if tag == 'href':
                book.append(select.text)
    if len(book) == 3:
        return book
    return False

def getLessons(soup):
    lessonSoups = soup.findAll("div", {"class":"unit-area"})
    if len(lessonSoups) == 0:   return False
    hrefSoups = lessonSoups[0].findAll("a")
    Hrefs = []
    for hrefsoup in hrefSoups:
        lesson, href = '', ''
        for tag, value in hrefsoup.attrs:
            if tag == 'href':
                href = value
            elif tag == 'title':
                lesson = value
        if (len(lesson)>0) and (len(href)>0):
            Hrefs.append((lesson, href))
    return Hrefs

def main():
    #url = 'http://wenku.baidu.com/portal/subject/8_s0_g0_v0'   #小学
    #url = 'http://wenku.baidu.com/portal/subject/9_s0_g0_v0'    #初中
    url = 'http://wenku.baidu.com/portal/subject/31_s0_g0_v0'   #高中
    soup = getSoup(url)
    bookSoups = getBookSoups(soup)
    if not bookSoups:
        return False
    subjectSoup = bookSoups[0]
    subjectHrefs = getSoupHrefs(subjectSoup)
    db = connectDb()
    bookSQL = 'insert into books(subject, version, grade, href) values(%s, %s, %s, %s)'
    lessonSQL = 'insert into lessons(book_id, title, href, flag) values(%s, %s, %s, %s)'
    url = 'http://wenku.baidu.com'
    for subject_href in subjectHrefs:
        soup = getSoup(url + subject_href)
        bookSoups = getBookSoups(soup)
        if not bookSoups: continue
        versionHrefs = getSoupHrefs(bookSoups[1])
        for version_href in versionHrefs:
            soup = getSoup(url + version_href)
            bookSoups = getBookSoups(soup)
            if not bookSoups: continue
            gradeHrefs = getSoupHrefs(bookSoups[2])
            for grade_href in gradeHrefs:
                book_href = url + grade_href
                soup = getSoup(book_href)
                book_name = getSelectBook(soup)
                lessons = getLessons(soup)
                print '#' * 100
                if not book_name: continue
                book_id = db.InsertTb(bookSQL, [(book_name[0], book_name[1], book_name[2], grade_href)])
                print book_href, '_'.join(book_name), len(lessons)
                values = []
                for title, href in lessons:
                    print '  '*3, title, book_href+href
                    values.append((book_id, title, href, 0))
                db.InsertTb(lessonSQL, values)
    db.CloseDb()
    print 'Over!'

if __name__ == '__main__':
    main()