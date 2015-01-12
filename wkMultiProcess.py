#!usr/bin/env python
#coding: utf-8

from wkSinglePage import CWKCrawler
from Database import CDatabase
from CommonModules import connectDb
from multiprocessing import process, Pool
import copy_reg
import types
import time

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

def readResourceHrefs(db, itemsNum):
    sql = 'select resource_id, href from resources where flag = 0 LIMIT %d ' % itemsNum
    resources = db.InquiryTb(sql)
    if len(resources) == 0:
        return False
    sql = 'update resources set flag = 1 where resource_id=%d'
    for i in range(len(resources)):
        db.UpdateTb(sql % resources[i]['resource_id'])
    return resources

def test(itemsNum):
    mCWCrawler = CWKCrawler()
    url = 'http://wk.baidu.com'
    db = connectDb()
    sql = 'update resources set content="%s",flag=2 where resource_id=%d'
    while True:
        resources = readResourceHrefs(db, itemsNum)
        if not resources:
            break
        for i in range(len(resources)):
            wkPage = mCWCrawler.getContentBS(url+resources[i]['href'], )
            db.UpdateTb(sql %(wkPage['content'], resources[i]['resource_id']))
    db.CloseDb()


def main(coreNum, itemsNum):
    mCWCrawler = CWKCrawler()
    url = 'http://wk.baidu.com'
    sql = 'update resources set content="%s",flag=2 where resource_id=%d'
    db = connectDb()
    while True:
        print 'Read resources from database.'
        resources = readResourceHrefs(db, itemsNum)
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
        pool = Pool(processes=coreNum)
        results = {}
        for i in range(len(resources)):
            results[i] = pool.apply_async(mCWCrawler.getContentBS, (url+resources[i]['href'], ))
        pool.close()
        pool.join()

        for i in results:
            print resources[i]['resource_id']
            wkPage = results[i].get()
            if not wkPage: continue
            db.UpdateTb(sql %(wkPage['content'], resources[i]['resource_id']))
    db.CloseDb()

if __name__ == '__main__':
    import cPickle
    main(4, 200)
    #test(1)