#!/usr/bin/env python
# del old files every week
# author: liuleic
# liencese: Apache License 2.0
import os,os.path
import time
import re
import shutil

Del_Path = ['/home/ftpusers/tftp/',]
#Del_Path = ['/home/ubuntu/test/aaa']

Old_Time = 60 * 60 * 24 * 30
#Old_Time = 60 * 60 * 24

File_Type = []
#File_Type = [r'.*\.img']

def RmFile(fpath):
    '''
    '''
    if not File_Type:
        os.remove(fpath)
    else:
        pass

def RmDirs(fpath):
    '''
    '''
    if not File_Type:
        shutil.rmtree(fpath)
    else:
        pass

def DeleteFiles(arg,dir_name,filelist):
    '''
    '''
    #print dir_name,filelist
    for f in filelist:
        fpath = os.path.join(dir_name,f)
        if os.path.exists(fpath):
            if os.path.isfile(fpath):
                s = os.stat(fpath)
                #print f,s.st_mtime
                diff_time = time.time() - s.st_mtime
                if diff_time > Old_Time:
                    #print diff_time
                    RmFile(fpath)
            elif os.path.isdir(fpath):
                s = os.stat(fpath)
                diff_time = time.time() - s.st_mtime
                if diff_time > Old_Time:
                    RmDirs(fpath)
            else:
                pass
        else:
            pass

def main():
    '''
    '''
    for p in Del_Path:
        if os.path.exists(p) and os.path.isdir(p) and os.listdir(p):
            os.path.walk(p,DeleteFiles,'del files')
        else:
            pass


if __name__ == '__main__':
    main()
