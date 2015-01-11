#!usr/bin/env/python
#coding: utf-8

from CommonModules import getUrlSource
from BeautifulSoup import BeautifulSoup
import re
import time

class CGetResourcesHref:
    def __init__(self):
        ''''''
        self.svgPattern = re.compile('(\d+)_s(\d+)_g(\d+)_v(\d+)')

    def getSoup(self, url):
        '''
        Get the source code.
        '''
        html = getUrlSource(url)
        if len(html) == 0:  return False
        soup = BeautifulSoup(html)
        return soup

    def getSubject(self, soup):
        '''
        Get the hrefs of subjects.
        '''
        Hrefs = set()
        return Hrefs

    def getVersion(self, soup):
        '''
        Get the hrefs of versions.
        '''
        Hrefs = set()
        return Hrefs

    def getGrade(self, soup):
        '''
        Get the hrefs of grades.
        '''
        Hrefs = set()
        return Hrefs


    def getSVG(self, soup):
        '''
        Get the hrefs of subject, version, grade.
        '''
        modules = soup.findAll("div", {"id":"select-all"})
        if len(modules) == 0:   return False
        modules = modules[0].findAll("a")
        hrefs = []
        for module in modules:
            for tag, value in module.attrs:
                href = value if tag == 'href' else ''
                svg = self.svgPattern.findall(href)
                if len(svg) == 1:
                    hrefs.append(href)
        return hrefs

    def getSelectSVG(self, soup):
        '''
        Get the hrefs of selected subject, version, grade.
        '''
        modules = soup.findAll("div", {"id":"select-all"})
        if len(modules) == 0:   return False
        modules = modules[0].findAll("li", {"class":"selected"})
        svg =[]
        for module in modules:
            for tag, value in module.find('a').attrs:
                if tag == 'href':
                    svg.append(module.text)
        if len(svg) == 3:
            return svg
        return False

    def getLessons(self, soup):
        '''
        Get the hrefs of lessons.
        '''
        modules = soup.findAll("div", {"class":"unit-area"})
        if len(modules) == 0:   return False
        modules = modules[0].findAll("a")
        hrefs = []
        for module in modules:
            for tag, value in module.attrs:
                if tag == 'href':
                    href = value
                elif tag == 'title':
                    title = value
            hrefs.append((href, title))
        return hrefs


def main():
    url = 'http://wenku.baidu.com/portal/subject/8_s0_g0_v0'

    mCGetResourcesHref = CGetResourcesHref()
    soup = mCGetResourcesHref.getSoup(url)

    Hrefs = set()   #set([href, ...])
    #Get the subject hrefs.
    subjectHrefs = mCGetResourcesHref.getSubject(soup)
    Hrefs |= subjectHrefs
    url = 'http://wenku.baidu.com'
    for s_href, svg in subjectHrefs:
        soup = mCGetResourcesHref.getSoup(url+s_href)
        versionHrefs = mCGetResourcesHref.getVersion(soup)
        Hrefs |= versionHrefs
        for v_href, svg in versionHrefs:
            soup = mCGetResourcesHref.getSoup(url+v_href)
            gradeHrefs = mCGetResourcesHref.getGrade(soup)
            Hrefs |= gradeHrefs

    svgHrefs = mCGetResourcesHref.getSVG(soup)
    lessonHrefs = mCGetResourcesHref.getLessons(soup)
    url = 'http://wenku.baidu.com'
    for svg_href  in svgHrefs:
        temp = url + svg_href
        time.sleep(3)
        mSourceCode = getUrlSource(temp)
        soup = BeautifulSoup(mSourceCode)
        svg = mCGetResourcesHref.getSelectSVG(soup)
        lessonHrefs = mCGetResourcesHref.getLessons(soup)
        for lesson_href, lesson_title in lessonHrefs:
            print temp + lesson_href, ''.join(svg), lesson_title
        # for lesson_href, lesson_title in lessonHrefs:
        #     print url + svg_href + lesson_href, svg_text, lesson_title

if __name__=='__main__':
    main()
