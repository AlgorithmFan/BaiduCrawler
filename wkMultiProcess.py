#!usr/bin/env python
#coding: utf-8

from wkSinglePage import CWKCrawler
from Database import CDatabase
from CommonModules import connectDb
from multiprocessing import process, Pool
import copy_reg
import types

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
    return resources

def main(coreNum, itemsNum):
    mCWCrawler = CWKCrawler()
    url = 'http://wk.baidu.com'
    sql = 'update resources set content="%s",flag=1 where resource_id=%d'
    db = connectDb()
    while True:
        resources = readResourceHrefs(db, itemsNum)
        if not resources:
            break
        # for resource in resources:
        #     wkPage = mCWCrawler.getContentBS(url+resource['href'])
        #     db.UpdateTb(sql %(wkPage['content'], resource['resource_id']))

        pool = Pool(processes=coreNum)
        results = {}
        for i in range(len(resources)):
            results[i] = pool.apply_async(mCWCrawler.getContentBS, (url+resources[i]['href'], ))
        pool.close()
        pool.join()

        for i in results:
            print i
            wkPage = results[i].get()
            db.UpdateTb(sql %(wkPage['content'], resources[i]['resource_id']))
    db.CloseDb()

if __name__ == '__main__':
    main(4, 10000)