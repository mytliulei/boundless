#!/usr/bin/env python

'''
'''

import pyinotify
import redis
import sys
import os,os.path
import re
import shutil
import time
import filecmp


RedisPool = None

class EventHandler(pyinotify.ProcessEvent):
    '''
    '''
    def my_init(self,watch_path=None,copy_path=None,ftpbase_path=None,codelistkey='switch:codelist:key'):
        '''
        '''
        self.watch_path = os.path.normpath(watch_path)
        self.codestream_list = ' '.join(os.listdir(self.watch_path))
        self.copy_path = os.path.normpath(copy_path)
        self.ftpbase_path = ftpbase_path
        #self.re_product = re.compile(r'(.*?)-(.*?)_')
        self.re_product = re.compile(r'(.*)-')
        self.re_product_code = re.compile(r'(.*)-(....)')
        self.productname = None
        self.code_stream = None
        self.upload_logpath = None
        self.switch_key = 'dp:dailybuild:update'
        self.redis = redis.Redis(connection_pool=RedisPool)
        self.codelistkey = codelistkey
        # self.updateCodeList()

    def process_IN_CLOSE_WRITE(self, event):
        '''
        '''
        if True:
            sys.stdout.write("[%s] Creating FILE path : %s filename %s\n" %  (time.ctime(),event.path,event.name))
            extname = os.path.splitext(event.name)[1]
            if extname == '.bin' or extname == '.BIN' :
                if not self.processBIN(event.path,event.name):
                    return
                print(self.code_stream,self.productname)
                if not self.copyBIN(event.pathname,event.name):
                    return
                if not self.broadcastRedis(event.name):
                    return
                sys.stdout.write('process file %s OK\n' % event.pathname)
                sys.stdout.flush()
            elif False and (extname == '.txt' or extname == '.TXT'):
                if not self.processTXT(event.path,event.name):
                    return
                if not self.broadcastLogpath(event.name):
                    return
                sys.stdout.write('process file %s OK\n' % event.pathname)
                sys.stdout.flush()
            else:
                pass


    def process_IN_CREATE(self, event):
        '''
        '''
        #if event.mask == pyinotify.IN_CREATE:
        if False:
            sys.stdout.write("[%s] Creating FILE path : %s filename %s\n" %  (time.ctime(),event.path,event.name))
            extname = os.path.splitext(event.name)[1]
            if extname == '.img' or extname == '.IMG' :
                if not self.processIMG(event.path,event.name):
                    return
                print(self.code_stream,self.productname)
                if not self.copyIMG(event.pathname,event.name):
                    return
                if not self.broadcastRedis(event.name):
                    return
                sys.stdout.write('process file %s OK\n' % event.pathname)
                sys.stdout.flush()
            elif extname == '.txt' or extname == '.TXT':
                if not self.processTXT(event.path,event.name):
                    return
                if not self.broadcastLogpath(event.name):
                    return
                sys.stdout.write('process file %s OK\n' % event.pathname)
                sys.stdout.flush()
            else:
                pass
        elif event.mask == (pyinotify.IN_CREATE | pyinotify.IN_ISDIR):
            sys.stdout.write('[%s] Creating Directory: path:%s directionname %s\n' % (time.ctime(),event.path,event.name))
            if self.watch_path == os.path.normpath(event.path):
                self.codestream_list = ' '.join(os.listdir(self.watch_path))
                if not self.updateCodeList():
                    return
                print('update code stream list OK: %s' % self.codestream_list)
            sys.stdout.flush()
        else:
            pass

    def process_IN_DELETE(self, event):
        '''
        '''
        if event.mask == (pyinotify.IN_DELETE | pyinotify.IN_ISDIR):
            sys.stdout.write('[%s] Deleting Directory: path:%s directionname %s\n' % (time.ctime(),event.path,event.name))
            if self.watch_path == os.path.normpath(event.path):
                self.codestream_list = ' '.join(os.listdir(self.watch_path))
                if not self.updateCodeList():
                    return
                print('update code stream list OK: %s' % self.codestream_list)
            sys.stdout.flush()

    def processBIN(self,path,name):
        '''
        '''
        sys.stdout.write('process bin file...\n')
        if not self.watch_path:
            sys.stdout.write('ftp path is None\n')
            return False
        pathtmp = os.path.join(path,name)
        self.code_stream = None
        # while self.watch_path != os.path.normpath(pathtmp):
        #     self.code_stream = os.path.split(pathtmp)[1]
        #     pathtmp = os.path.split(pathtmp)[0]
        #     if pathtmp == '/':
        #         return False
        self.productname = None
        plist = self.re_product_code.search(name)
        if plist:
            #self.productname = plist.group(2)
            self.productname = plist.group(1)
            self.code_stream = plist.group(2)
        if not self.code_stream or not self.productname:
            print('can not get code_stream or product_name in processBIN')
            return False
        return True

    def processTXT(self,path,name):
        '''
        '''
        sys.stdout.write('process txt file...\n')
        if not self.watch_path:
            sys.stdout.write('ftp path is None\n')
            return False
        pathname = os.path.join(path,name)
        basename = os.path.splitext(name)[0]
        pathtmp = pathname
        self.code_stream = None
        while self.watch_path != os.path.normpath(pathtmp):
            self.code_stream = os.path.split(pathtmp)[1]
            pathtmp = os.path.split(pathtmp)[0]
            if pathtmp == '/':
                return False
        self.productname = None
        plist = self.re_product.search(name)
        if plist:
            self.productname = plist.group(1)
        if not self.code_stream or not self.productname:
            print('can not get code_stream or product_name in processTXT')
            return False
        self.upload_logpath = None

        if os.path.isfile(pathname):
            fid = open(pathname)
            try:
                for text in fid.readlines():
                    if text.strip():
                        self.upload_logpath = text.strip()
                        break
                fid.close()
            except Exception,ex:
                print('read file %s error in processTXT,err:%s' % (pathname,ex))
                fid.close()
                return False
        else:
            print('not exists file txt')
        if not self.upload_logpath:
            print('get upload_logpath is null in TXT file')
            return False
        return True

    def copyBIN(self,pathname,name):
        '''
        '''
        if not self.copy_path:
            return False
        dstname = os.path.join(self.copy_path,name)
        try:
            shutil.copyfile(pathname,dstname)
        except Exception,ex:
            sys.stdout.write('%s' % ex)
            sys.stdout.write('\n')
            return False
        return True

    def broadcastRedis(self,name):
        '''
        '''
        try:
            self.redis = redis.Redis(connection_pool=RedisPool)
            broadcast_str = '%s||||%s||||%s' % (self.code_stream,self.productname,os.path.join(self.ftpbase_path,name))
            # cpkey = '%s %s bin' % (self.code_stream,self.productname)
            redispipe = self.redis.pipeline(transaction=False)
            # redispipe.set(cpkey,os.path.join(self.ftpbase_path,name))
            redispipe.publish(self.switch_key,broadcast_str)
            ret = redispipe.execute()
        except Exception,ex:
            sys.stdout.write('%s' % ex)
            sys.stdout.write('\n')
            return False
        return True

    def updateCodeList(self):
        '''
        '''
        try:
            self.redis = redis.Redis(connection_pool=RedisPool)
            redispipe = self.redis.pipeline(transaction=False)
            redispipe.set(self.codelistkey,self.codestream_list)
            ret = redispipe.execute()
        except Exception,ex:
            sys.stdout.write('%s' % ex)
            sys.stdout.write('\n')
            return False
        return True

    def broadcastLogpath(self,name):
        '''
        '''
        try:
            self.redis = redis.Redis(connection_pool=RedisPool)
            broadcast_str = '%s||||%s||||upload_logpath||||%s' % (self.productname,self.code_stream,self.upload_logpath)
            cpkey = '%s %s logpath' % (self.code_stream,self.productname)
            redispipe = self.redis.pipeline(transaction=False)
            redispipe.set(cpkey,self.upload_logpath)
            redispipe.publish(self.switch_key,broadcast_str)
            ret = redispipe.execute()
        except Exception,ex:
            sys.stdout.write('%s' % ex)
            sys.stdout.write('\n')
            return False
        return True
        pass


def usage():
    print("usage")

if __name__ == '__main__':
    import getopt
    redis_port = 6379
    redis_ip = '192.168.50.209'
    fsdetach = False
    w_path = '/home/ftpusers/ftp/build'
    c_path='/home/ftpusers/tftp/'
    b_path=''
    client_range=''
    opts,args = getopt.getopt(sys.argv[1:],'hdp:i:w:c:b:',['help','detach','port=','ip=','wpath=','cpath=','bpath=',])
    for opt,arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit(1)
        elif opt in ("-p","--port"):
            try:
                redis_port = int(arg)
            except Exception:
                usage()
                sys.exit(1)
        elif opt in ("-i","--ip"):
            redis_ip = arg
        elif opt in ("-w","--wpath"):
            w_path = arg
        elif opt in ("-c","--cpath"):
            c_path = arg
        elif opt in ("-b","--bpath"):
            b_path = arg
        elif opt in ("-d","--detach"):
            fsdetach = True
        else:
            pass
    RedisPool = redis.ConnectionPool(host=redis_ip,port=redis_port)
    wm = pyinotify.WatchManager()  # Watch Manager
    mask = pyinotify.IN_CREATE | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_DELETE  # watched events
    handler = EventHandler(watch_path=w_path,copy_path=c_path,ftpbase_path=b_path)
    notifier = pyinotify.Notifier(wm, handler)
    wdd = wm.add_watch(w_path, mask, rec=True,auto_add=True)
    logfile = '/tmp/monitorfs%s.log' % time.strftime('%Y%m%d-%H%M%S')
    pidfile = '/tmp/monitorfs%s.pid' % time.strftime('%Y%m%d-%H%M%S')

    notifier.loop(daemonize=fsdetach,pid_file=pidfile,stdout=logfile)
    #notifier.loop()
