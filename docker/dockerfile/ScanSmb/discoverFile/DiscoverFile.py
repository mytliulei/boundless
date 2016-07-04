#!/usr/bin/env python
#-*- coding: UTF-8 -*-
#  Copyright 2008-2016 Hangzhou DPtech Technologies Co., Ltd.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Discover the latest version file by scanning given paths on smb server
"""

import sys
import os,os.path
import re
import shutil
import socket
from argparse import ArgumentParser
import time
import logging,logging.handlers

from nmb.NetBIOS import NetBIOS
from smb.SMBConnection import SMBConnection
import redis


class ScanSmbPath(object):
    """
    """
    def __init__(self, smbcon, paths, file_pattern, *args, **kwargs):
        """
        """
        self.smb_con = smbcon
        self.paths = paths
        self.file_re = re.compile(file_pattern)
        self.new_file = {}
        self.new_ctime = {}
        self.new_fsize = {}
        self.logger = logging.getLogger("scansmb")
        # self.write_uid = pwd.getpwnam("ftpuser").pw_uid
        # self.write_gid = pwd.getpwnam("ftpuser").pw_gid

    def walk_path(self,server_name,path,*args):
        """
        """
        rel_path = "/"+path
        dirs , files, c_times,f_sizes = [], [], [], []
        try:
            names = self.smb_con.listPath(server_name,rel_path)
        except Exception,ex:
            sys.stdout.write('[%s] listPath  error %s' % (time.ctime(),ex))
            sys.stdout.write('\n')
            self.logger.critical("listPath  error %s" % ex)
            sys.exit(1)
        for name in names:
            if name.isDirectory:
                if name.filename not in [u'.', u'..']:
                    dirs.append(name.filename)
            else:
                if self.file_re.search(name.filename):
                    files.append(name.filename)
                    c_times.append(name.create_time)
                    f_sizes.append(name.file_size)
        ret_path = os.path.join(u"/"+server_name,path)
        yield ret_path,files,c_times,f_sizes
        for name in dirs:
            new_path = os.path.join(path, name)
            for x in self.walk_path(server_name, new_path):
                yield x

    def find_file(self,file_filter=None):
        """
        """
        if file_filter:
            self.file_re = re.compile(file_filter)
        for xpath in self.paths:
            ipath = xpath.strip("/")
            ipath_list = ipath.split("/",1)
            iserver_name = ipath_list[0]
            iserver_path = ipath_list[1]
            for (w_path,w_files,w_ctimes,w_fsizes) in self.walk_path(iserver_name,iserver_path):
                self.set_new_file(xpath,w_path,w_files,w_ctimes,w_fsizes)

    def set_new_file(self,path,r_path,files,ctimes,fsizes):
        """
        """
        if path not in self.new_ctime.keys():
            base_ctime = 0
        else:
            base_ctime = self.new_ctime[path]
        base_file = None
        base_fsize = None
        for (ifile,ictime,fsize) in zip(files,ctimes,fsizes):
            if ictime > base_ctime:
                base_ctime = ictime
                base_file = ifile
                base_fsize = fsize
        if base_file:
            self.new_file[path] = os.path.join(r_path,base_file)
            self.new_ctime[path] = base_ctime
            self.new_fsize[path] = base_fsize

    def get_new_file(self,path):
        """
        """
        if path not in self.new_file.keys():
            return None
        return (self.new_file[path],self.new_fsize[path])

    def retrieve_file(self,src_path,to_path,n_fsize):
        """
        """
        if src_path in self.new_file.keys():
            new_file_path = self.new_file[src_path]
            filename = os.path.split(new_file_path)[1]
            r_to_path = os.path.realpath(to_path)
            to_file = os.path.join(r_to_path,filename)
            if os.path.exists(to_file):
                tftp_fsize = os.path.getsize(to_file)
                if n_fsize == tftp_fsize:
                    sys.stdout.write('file %s exists, not download to overwrite' % filename)
                    sys.stdout.write('\n')
                    self.logger.info("file %s exists, not download to overwrite" % filename)
                    return 0
                else:
                    pass
            ipath = new_file_path.strip("/")
            ipath_list = ipath.split("/",1)
            iserver_name = ipath_list[0]
            iserver_path = "/"+ipath_list[1]
            try:
                with open(to_file,"wb") as fobj:
                    sys.stdout.write('[%s] download file %s ...' % (time.ctime(),filename))
                    sys.stdout.write('\n')
                    self.logger.info("download file %s ..." % filename)
                    self.smb_con.retrieveFile(iserver_name,iserver_path,fobj,timeout=180)
                    # os.chown(to_file, self.write_uid, self.write_gid)
            except Exception,ex:
                if os.path.exists(to_file):
                    os.remove(to_file)
                    self.logger.error("download file error,remove it ...")
                    self.logger.error(ex)
                return 2
        else:
            return 1
        return 0


def get_sub_path(redis_con,scankey):
    """
    """
    redispipe = redis_con.pipeline()
    redispipe.smembers(scankey)
    ret = redispipe.execute()
    if not ret[0]:
        logger = logging.getLogger("scansmb")
        sys.stdout.write('key %s has no member' % scankey)
        logger.error("key %s has no member" % scankey)
        return None
    for pkey in ret[0]:
        redispipe.smembers(pkey)
    pret = redispipe.execute()
    pdict = {}
    for (k,p) in zip(ret[0],pret):
        pdict[k] = [idec.decode("utf-8") for idec in p]
        # pdict[k] = list(p)
    return pdict

def update_key(redis_con,scankey):
    """
    """
    redispipe = redis_con.pipeline()
    redispipe.smembers(scankey)
    ret = redispipe.execute()
    if not ret[0]:
        logger = logging.getLogger("scansmb")
        sys.stdout.write('key %s has no member' % scankey)
        logger.error("key %s has no member" % scankey)
        return -1
    # update smb server in scankey
    smbkey_list = list(ret[0])
    for ikey in smbkey_list:
        redispipe.exists(ikey)
    ret = redispipe.execute()
    r_smbkey_list = []
    for (ikey,val) in zip(smbkey_list,ret):
        if not val:
            redispipe.srem(scankey,ikey)
        else:
            r_smbkey_list.append(ikey)
    ret = redispipe.execute()
    # update path in smb+path key
    for pkey in r_smbkey_list:
        redispipe.smembers(pkey)
    ret = redispipe.execute()
    for (sname,key_set) in zip(r_smbkey_list,ret):
        for ikey in key_set:
            redispipe.exists(sname+ikey)
        rfret = redispipe.execute()
        for (jkey,val) in zip(key_set,rfret):
            if not val:
                redispipe.srem(sname,jkey)
        ret = redispipe.execute()
    return 0

def pulish_update_msg(redis_con,pub_key,smb_name,path,tftp_server_ip,filename):
    """
    """
    redispipe = redis_con.pipeline()
    broadcast_key = "%s_%s_%s" % (pub_key, smb_name, path)
    broadcast_str = "%s||||%s" % (filename,tftp_server_ip)
    redispipe.set(broadcast_key,filename)
    redispipe.expire(broadcast_key,60*60*24*5)
    redispipe.publish(broadcast_key,broadcast_str)
    ret = redispipe.execute()
    print('[%s] publish message on channel:' % time.ctime())
    print(broadcast_str, broadcast_key)
    logger = logging.getLogger("scansmb")
    logger.info("publish message on channel:")
    logger.info(broadcast_str)
    logger.info(broadcast_key)
    # sys.stdout.write('publish message %s on channel %s' % (broadcast_str, broadcast_key))
    # sys.stdout.write('\n')

def main():
    """
    """
    p = ArgumentParser(description='Discover file on smb server')
    p.add_argument('--scankey', "-s", default="DP_VERSIONUPDATE_SCANPAHT", help='the key of smb server paths on redis server')
    p.add_argument('--pubkey', "-k", default="DP_VERSIONUPDATE_PUB", help='the key of publish new version file on redis server')
    p.add_argument('--redisip', '-i', default="10.18.142.48", help='redis server ip address')
    p.add_argument('--filepattren', '-f', default="\\.bin$", help='file filter regexp express')
    p.add_argument('--redisport', '-p', type=int, default=6379, help='redis server port')
    p.add_argument('--tftppath', '-t', default="/home/ftpusers/tftp", help='tftp server root path')
    p.add_argument('--tftpip', '-a', default="10.18.142.48", help='tftp server ip address')
    args = p.parse_args()
    logger = logging.getLogger()
    log_Handle = logging.handlers.RotatingFileHandler("/home/ftpusers/scansmb.log",maxBytes=1024*1024,backupCount=5)
    log_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.INFO)
    log_Handle.setFormatter(log_format)
    logger.addHandler(log_Handle)
    try:
        RedisPool = redis.ConnectionPool(host=args.redisip,port=args.redisport,db=0)
        redis_con = redis.Redis(connection_pool=RedisPool)
    except Exception,ex:
        sys.stdout.write('%s' % ex)
        sys.stdout.write('\n')
        return 101
    # del expire keys from redis server
    update_code = update_key(redis_con,args.scankey)
    if update_code < 0:
        return 201
    # get scan path from redis server
    smb_path = get_sub_path(redis_con,args.scankey)
    if smb_path is None:
        return 201
    # smb_path = {"192.168.2.30@dp:dpdp":[u"/产品版本/BSW/BSWV100R003/神州二号"],}
    print("[%s] scanning smb server path %s" % (time.ctime(),smb_path))
    logger.info("scanning smb server path %s" % smb_path)
    client_name = socket.gethostname()
    for ismb in smb_path.keys():
        ismb_ip = ismb.split("@")[0]
        userpasw = ismb.split("@")[1].split(":")
        bios = NetBIOS()
        srv_name = bios.queryIPForName(ismb_ip)
        bios.close()
        smb_con = SMBConnection(userpasw[0],userpasw[1],client_name,srv_name[0])
        smb_con.connect(ismb_ip)
        scansmb = ScanSmbPath(smb_con,smb_path[ismb],args.filepattren)
        scansmb.find_file()
        for ipath in smb_path[ismb]:
            (n_file,n_fsize) = scansmb.get_new_file(ipath)
            filename = os.path.split(n_file)[1]
            ret = scansmb.retrieve_file(ipath,args.tftppath,n_fsize)
            if ret == 0:
                pulish_update_msg(redis_con,args.pubkey,ismb,ipath,args.tftpip,filename)
        smb_con.close()


if __name__ == '__main__':
    main()
