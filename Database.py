#!usr/bin/python
#coding:utf8
#author: Zhang Haidong
#date: 2013/8/19

import MySQLdb
class CDatabase():
    def __init__(self, ip, username, password, database):
        self.ip = ip
        self.username = username
        self.password = password
        self.database = database
        self.connection = None
        
    def OpenDb(self):
        '''
        ip:the address of the server
        username: the name of user
        password: the password of the user
        database: the database needed
        '''
        try:
            self.connection = MySQLdb.connect(user=self.username, passwd=self.password, host=self.ip, db=self.database, charset='utf8')
            #self.connection.ping(True)
            print 'Succeed to connect to the database --%s' % self.database
        except:
            print 'Cannot connect to the database --%s' % self.database
            exit(0)
        
    def InquiryTb(self, sql, flag=0):
        '''
        flag==0: select all the items from the table
        flag==1: select only one item from the table
        flag==n: select n items from the table
        '''
        try:
            cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(sql)
            result = []
            if flag==0:
                result = cursor.fetchall()
            elif flag==1:
                result.append(cursor.fetchone())
            else:
                result = cursor.fetchmany(flag)
            cursor.close()
            return result
        except MySQLdb.Error as e:
            print "InquiryTable Error %d: %s" % (e.args[0], e.args[1])
            

    def InsertTb(self, sql, value):
        '''
        the type of value must be []
        '''
        try:
            cursor = self.connection.cursor()
            if len(value)==1:
                cursor.execute(sql, value[0])
                return cursor.lastrowid
            else:
                cursor.executemany(sql, value)
            self.connection.commit()
            cursor.close()
        except MySQLdb.Error as e:
            try:
                print 'MySQL need to be connected again.'
                self.openDatabase()
                cursor = self.connection.cursor()
                if len(value)==1:
                    cursor.execute(sql, value[0])
                    return cursor.lastrowid
                else:
                    cursor.executemany(sql, value)
                self.connection.commit()
                cursor.close()
            except:
                self.connection.rollback()
                print "InsertTable Error %d: %s" % (e.args[0], e.args[1])
       
    def DeleteTb(self, sql):
        '''
        delete the items by sql
        '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            cursor.close()
        except MySQLdb.Error as e:
            self.connection.rollback()
            print "DeleteTable Error %d: %s" % (e.args[0], e.args[1])

    def TruncateTb(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            cursor.close()
        except MySQLdb.Error as e:
            self.connection.rollback()
            print "Truncate Error %d: %s" % (e.args[0], e.args[1])

         
    def UpdateTb(self, sql):
        ''''''
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
            self.connection.commit()
            cursor.close()
        except MySQLdb.Error as e:
            self.connection.rollback()
            print "UupdateTable Error %d: %s" % (e.args[0], e.args[1])
            
    def CloseDb(self):
        try:
            self.connection.close()
        except MySQLdb.Error as e:
            print "Close Erros %d: %s" % (e.args[0], e.args[1])
                  

