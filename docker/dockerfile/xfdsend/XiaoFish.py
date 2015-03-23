#!/usr/bin/env python
#-*- coding: UTF-8 -*-
'''network stream genertor,for RF testing base on XMLRPC and scapy

   ps: XiaoFish is a little cat, bless her. :)
'''


import os,os.path
import sys
import StringIO
import threading
import select
import time
import traceback
import re,binascii
import socket
import struct
from cPickle import dumps

from scapy.all import *
import daemonocle
import robotremoteserver
import rpyc



__version__ = '0.1'
__author__ = 'liuleic'
__copyright__ = 'Copyright 2014, DigitalChina Network'
__license__ = 'Apache License, Version 2.0'
__mail__ = 'liuleic@digitalchina.com'


class XiaoFish(object):
    '''
    '''
    def __init__(self,iflist=None):
        ''''''
        self.ifList = iflist
        if iflist:
            #ifnumlist = [str(i) for i in range(1,len(iflist)+1)]
            self._ifDict = {str(i+1):iflist[i] for i in range(len(iflist))}
            ifilenamelist = ['xiaofish_'+name+'.pcap' for name in iflist]
            self._ifileDict = {str(i+1):ifilenamelist[i] for i in range(len(ifilenamelist))}
            self._sendThreadDict = {str(i+1):None for i in range(len(iflist))}
            self._capThreadDict = {str(i+1):None for i in range(len(iflist))}
            self._ifstatsThreadDict = {str(i+1):None for i in range(len(iflist))}
        else:
            self._ifDict = {}
            self._ifileDict = {}
            self._sendThreadDict = {}
            self._capThreadDict = {}
            self._ifstatsThreadDict = {}
        self._packetDict = {}
        self._packetLenDict = {}
        self._streamConDict = {}
        #self._sendThreadDict = {}
        #self._sendThreadStatsDict = {}
        #self._capThreadDict = {}
        #self._capThreadStatsDict = {}
        #self._ifStatsDict = {}
        self.ifilePath = '/tmp'
        #if stats thread
        #self._ifstats_thread = None
        if iflist:
            self._start_ifstats()

    def _start_ifstats(self):
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return False
        for i in range(len(self.ifList)):
            self._ifstatsThreadDict[str(i+1)] = XFIfStats(self.ifList[i])
            if not self._ifstatsThreadDict[str(i+1)].verify_if_file():
                self._ifstatsThreadDict[str(i+1)] = None
                raise AssertionError("can not find /sys/class/net path,stats thread can not start")
                return False
            #start thread
            self._ifstatsThreadDict[str(i+1)].setDaemon(True)
            self._ifstatsThreadDict[str(i+1)].start()

    def init_xfsend(self):
        ''''''
        if self.ifList:
            for i in self._ifDict.keys():
                self.stop_stream(i)
                self.stop_capture(i)
        return 0

    def _get_iface_list(self):
        ''''''
        return self.ifList

    def set_stream_from_hexstr(self,ifNum,packetStrList,streamId):
        ''''''
        if type(packetStrList) is not list:
            raise AssertionError("parameter packetStrList is not list")
            return -2
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            raise AssertionError("iface num %s not in iface List" % ifNum)
            return -1
        try:
            packetList = []
            for ipstr in packetStrList:
                if len(ipstr) % 2 == 1:
                    raise AssertionError('hexstr is not even')
                chr_ipstr_list = [
                    chr(int(ipstr[i:i+2],16)) for i in range(0,len(ipstr)-1,2)
                ]
                chr_ipstr = ''.join(chr_ipstr_list)
                packetList.append(Ether(chr_ipstr))
        except Exception,ex:
            raise AssertionError("can not convert %s to Packet on iface %s" % (ipstr,ifNum))
            return -1
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            self._packetDict[ifNum] = {}
        self._packetDict[ifNum][streamId] = packetList
        #self._packetDict[ifNum] = packetList
        self._packetLenDict[ifNum] = len(self._packetDict[ifNum])
        return 0

    def set_stream_from_scapy(self,ifNum,packetStrList,streamId):
        ''''''
        if type(packetStrList) is not list:
            raise AssertionError("parameter packetStrList is not list")
            return -2
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            raise AssertionError("iface num %s not in iface List" % ifNum)
            return -1
        try:
            packetList = []
            for ipstr in packetStrList:
                cmd = 'p=' + ipstr
                exec(cmd)
                packetList.append(p)
        except Exception,ex:
            raise AssertionError("can not convert %s to Packet on iface %s: %s" % (ipstr,ifNum,traceback.format_exc()))
            return -1
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            self._packetDict[ifNum] = {}
        self._packetDict[ifNum][streamId] = packetList
        #self._packetDict[ifNum] = packetList
        self._packetLenDict[ifNum] = len(self._packetDict[ifNum])
        return 0

    def set_stream_from_dsend(self,ifNum,packetList,streamId):
        ''''''
        if type(packetList) is not list:
            raise AssertionError("parameter packetStrList is not list")
            return -2
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            raise AssertionError("iface num %s not in iface List" % ifNum)
            return -1
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            self._packetDict[ifNum] = {}
        self._packetDict[ifNum][streamId] = packetList
        #self._packetDict[ifNum] = packetList
        self._packetLenDict[ifNum] = len(self._packetDict[ifNum])
        return 0

    @staticmethod
    def _verify_raw(rawstr):
        ''''''
        chr_ipstr_list = [
            chr(int(rawstr[i:i+2],16)) for i in range(0,len(rawstr)-1,2)
        ]
        cmd = "p=Raw(''.join(chr_ipstr_list))"
        try:
            exec(cmd)
        except Exception,ex:
            return Raw()
        else:
            return p

    def set_stream_from_pcap(self,ifNum,packetbytes,streamId):
        ''''''
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            raise AssertionError("iface num %s not in iface List" % ifNum)
            return -1
        filename = os.path.join(self.ifilePath, self._ifileDict[ifNum])
        if not self._write_pcapfile_xf(filename,packetbytes):
            raise AssertionError("wirte %s fail" % filename)
            return -1
        read_packet = self._read_pcapfile_xf(ifNum,filename)
        if not read_packet[0]:
            return -1
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            self._packetDict[ifNum] = {}
        self._packetDict[ifNum][streamId] = read_packet[1]
        #self._packetDict[ifNum] = read_packet[1]
        self._packetLenDict[ifNum] = len(self._packetDict[ifNum])
        return 0

    def _read_pcapfile_xf(self,ifNum,filename):
        if ifNum not in self._ifDict.keys():
            return False
        try:
            p = rdpcap(filename)
        except Exception,ex:
            raise AssertionError("read %s fail:%s" % (filename,ex))
            return False,None
        return True,p

    def _write_pcapfile_xf(self,filename,packetbytes):
        with open(filename,'wb') as fhandler:
            fhandler.write(packetbytes)
        return True

    def set_stream_control(self,ifNum,streamId,streamRate,streamRateMode,streamMode,numPacket,returnId):
        '''
        '''
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            raise AssertionError("iface num %s not in iface List" % ifNum)
            return -1
        streamId = str(streamId)
        if ifNum not in self._streamConDict.keys():
            self._streamConDict[ifNum] = {}
        streamInterval = 1/float(streamRate)
        streamRateMode = int(streamRateMode)
        streamMode = int(streamMode)
        numPacket = int(numPacket)
        returnId = int(returnId)
        self._streamConDict[ifNum][streamId] = [streamInterval,streamRateMode,streamMode,numPacket,returnId]
        return 0

    def get_stream_control(self,ifNum,streamId='0'):
        '''
        '''
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._streamConDict.keys():
            return -2
        streamId = str(streamId)
        conList = []
        if streamId == '0':
            for i in range(self._packetLenDict[ifNum]):
                istr += 1
                istr = str(istr)
                conList.append(self._streamConDict[ifNum][istr])
        else:
            if streamId in self._streamConDict[ifNum].keys():
                conList = self._streamConDict[ifNum][streamId]
            else:
                pass
        return conList


    def clear_stream(self,ifNum):
        '''
        '''
        if not self.ifList:
            raise AssertionError("Not attach any iface in XiaoFish RobotRemoteServer")
            return -1
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            return -2
        if ifNum not in self._packetDict.keys():
            if ifNum in self._streamConDict.keys():
                self._streamConDict[ifNum] = {}
            return -3
        else:
            self.stop_stream(ifNum)
            self._packetDict[ifNum] = {}
            self._packetLenDict[ifNum] = 0
        if ifNum in self._streamConDict.keys():
            self._streamConDict[ifNum] = {}
        return 0

    # def get_stream(self,ifNum,streamId,num=0):
    #     ''''''
    #     if type(num) is str:
    #         num = int(num)
    #     ifNum = str(ifNum)
    #     streamId = str(streamId)
    #     if ifNum not in self._packetDict.keys():
    #         raise AssertionError("ifNum %s not in _packetDict" % ifNum)
    #     if streamId not in self._packetDict[streamId].keys():
    #         raise AssertionError("streamId %s not in _packetDict[%s]" % (streamId,ifNum))
    #     packet = ''
    #     old_stdout = sys.stdout
    #     packetout = StringIO.StringIO()
    #     sys.stdout = packetout
    #     try:
    #         if num > 0:
    #             if num <= len(self._packetDict[ifNum][streamId]):
    #                 print 'packet num %i:' % num
    #                 self._packetDict[ifNum][streamId][num-1].show()
    #             else:
    #                 print('')
    #         elif num == 0:
    #             for i in range(len(self._packetDict[ifNum][streamId])):
    #                 print 'packet num %i:' % (i+1)
    #                 self._packetDict[ifNum][streamId][i].show()
    #         else:
    #             print('')
    #     except Exception,ex:
    #         packet = ''
    #         sys.stdout = old_stdout
    #         raise AssertionError("read iface %s stream %s fail: %s" % (self._ifDict[ifNum],num,ex))
    #     else:
    #         packet += packetout.getvalue()
    #         sys.stdout = old_stdout
    #     return packet

    def get_stream(self,ifNum,streamId=0,num=0):
        ''''''
        num = int(num)
        ifNum = str(ifNum)
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            raise AssertionError("ifNum %s not in _packetDict" % ifNum)
        packetList = []
        if streamId == '0':
            for i in range(self._packetLenDict[ifNum]):
                istr = str(i+1)
                if len(self._packetDict[ifNum][istr]) == 1:
                    rtstr = str(self._packetDict[ifNum][istr])
                else:
                    rtstr = [str(ipstr) for ipstr in self._packetDict[ifNum][istr]]
                packetList.append(rtstr)
            return packetList
        else:
            if streamId not in self._packetDict[streamId].keys():
                raise AssertionError("streamId %s not in _packetDict[%s]" % (streamId,ifNum))
                return packetList
            try:
                if num > 0:
                    if num <= len(self._packetDict[ifNum][streamId]):
                        packetList.append(self._packetDict[ifNum][streamId][num-1])
                    else:
                        pass
                elif num == 0:
                    packetList = self._packetDict[ifNum][streamId]
                else:
                    pass
            except Exception,ex:
                packetList = []
        return str(packetList)

    def get_stream_packet_size(self,ifNum,streamId=0,num=0):
        ''''''
        num = int(num)
        ifNum = str(ifNum)
        streamId = str(streamId)
        if ifNum not in self._packetDict.keys():
            raise AssertionError("ifNum %s not in _packetDict" % ifNum)
        packetSizeList = []
        if streamId == '0':
            for i in range(self._packetLenDict[ifNum]):
                istr += 1
                istr = str(istr)
                psize = (len(ips) for ips in self._packetDict[ifNum][istr])
                packetSizeList.append(psize)
        else:
            if streamId not in self._packetDict[streamId].keys():
                raise AssertionError("streamId %s not in _packetDict[%s]" % (streamId,ifNum))
                return str(packetSizeList)
            try:
                if num > 0:
                    if num <= len(self._packetDict[ifNum][streamId]):
                        packetSizeList.append(len(self._packetDict[ifNum][streamId][num-1]))
                    else:
                        pass
                elif num == 0:
                    psize = (len(ips) for ips in self._packetDict[ifNum][streamId])
                    packetSizeList = psize
                else:
                    pass
            except Exception,ex:
                packetSizeList = []
        return packetSizeList

    def _modify_stream(self,iface,*args):
        ''''''
        pass

    def send_stream(self,ifNum):
        '''
        '''
        #if type(interval) is str:
        #    interval = float(interval)
        #if type(count) is str:
        #    count = int(count)
        ifNum = str(ifNum)
        if ifNum not in self._ifDict.keys():
            return -2
        if ifNum not in self._packetDict.keys():
            return -3
        if not self._packetDict[ifNum]:
            raise AssertionError("iface %s stream not set" % ifNum)
            return -4
        if self._sendThreadDict and self._sendThreadDict[ifNum] and self._sendThreadDict[ifNum].isAlive():
            return self._sendThreadDict[ifNum].xfstats
        #build send packet
        sPacket = []
        sControl = []
        sLen = self._packetLenDict[ifNum]
        for i in range(sLen):
            sNum = str(i+1)
            if sNum in self._packetDict[ifNum].keys():
                sPacket.append(self._packetDict[ifNum][sNum])
            else:
                raise AssertionError("iface %s stream %s not set" % (ifNum,sNum))
                return -5
            if sNum in self._streamConDict[ifNum].keys():
                sControl.append(self._streamConDict[ifNum][sNum])
            else:
                raise AssertionError("iface %s stream %s contrl not set" % (ifNum,sNum))
                return -6
        try:
            self._sendThreadDict[ifNum] = XFSend(
                self._ifDict[ifNum],sPacket,sControl)
            self._sendThreadDict[ifNum].setDaemon(True)
            self._sendThreadDict[ifNum].start()
        except Exception,ex:
            self._sendThreadDict[ifNum] = None
            raise AssertionError("send iface %s stream fail: %s" % (self._ifDict[ifNum],ex))
            return -100
        return 0

    def stop_stream(self,ifNum):
        ''''''
        if ifNum not in self._ifDict.keys():
            return -2
        if not self._sendThreadDict or not self._sendThreadDict[ifNum]:
            return -1
        if self._sendThreadDict[ifNum].xfstats == -1:
            return 1
        elif self._sendThreadDict[ifNum].xfstats == 0:
            return 2
        elif self._sendThreadDict[ifNum].xfstats == -2:
            return -3
        #stop send
        self._sendThreadDict[ifNum].xfstats = 0
        return 0

    def get_send_stream_num(self,ifNum):
        ''''''
        if ifNum not in self._ifDict.keys():
            return 0
        if not self._sendThreadDict or not self._sendThreadDict[ifNum]:
            return 0
        return self._sendThreadDict[ifNum].xfsendnum

    def get_send_stream_status(self,ifNum):
        '''return status
           - -2 : error
           - -1 : ready to start
           -  1 : running
           -  0 : stoping
        '''
        if ifNum not in self._ifDict.keys():
            return -2
        if not self._sendThreadDict or not self._sendThreadDict[ifNum]:
            return -2
        return self._sendThreadDict[ifNum].xfstats

    def capture_packet(self,ifNum,filter=None,timeout=None,count=0):
        ''''''
        if timeout:
            timeout = float(timeout)
        if ifNum not in self._ifDict.keys():
            return -2
        if self._capThreadDict and self._capThreadDict[ifNum] and self._capThreadDict[ifNum].isAlive():
            return self._capThreadDict[ifNum].xfstats
        try:
            self._capThreadDict[ifNum] = XFCapture(
                self._ifDict[ifNum],timeout,filter,count)
            self._capThreadDict[ifNum].setDaemon(True)
            self._capThreadDict[ifNum].start()
        except Exception,ex:
            self._capThreadDict[ifNum] = None
            raise AssertionError("capture iface %s stream fail: %s" % (self._ifDict[ifNum],ex))
            return -3
        time.sleep(1)
        return 0

    def stop_capture(self,ifNum):
        ''''''
        if ifNum not in self._ifDict.keys():
            return -2
        if not self._capThreadDict or not self._capThreadDict[ifNum]:
            return -1
        if self._capThreadDict[ifNum].xfstats == -1:
            return 1
        elif self._capThreadDict[ifNum].xfstats == 0:
            return 2
        elif self._capThreadDict[ifNum].xfstats == -2:
            #return self._capThreadDict[ifNum].errmsg
            return -3
        #stop send
        self._capThreadDict[ifNum].xfstats = 0
        #self._capThreadDict[ifNum].xf_stop_capture()
        return 0

    def get_capture_packet_num(self,ifNum):
        ''''''
        if ifNum not in self._ifDict.keys():
            return -2
        if not self._capThreadDict or not self._capThreadDict[ifNum]:
            return -1
        return self._capThreadDict[ifNum].xfcapnum

    def get_capture_packet(self,ifNum,num=0):
        ''''''
        if ifNum not in self._ifDict.keys():
            return -3
        if not self._capThreadDict or not self._capThreadDict[ifNum]:
            return -1
        if self._capThreadDict[ifNum].xfstats == 1:
            return 1
        elif self._capThreadDict[ifNum].xfstats == 0:
            return 0
        elif self._capThreadDict[ifNum].xfstats == -2:
            return -2
        num = int(num)
        if num == 0:
            return str(self._capThreadDict[ifNum].xfcappacket)
        else:
            if num <= self._capThreadDict[ifNum].xfcapnum:
                return str(self._capThreadDict[ifNum].xfcappacket[num-1])
            else:
                return str(self._capThreadDict[ifNum].xfcappacket[-1])

    def get_capture_packet_hexstr(self,ifNum,num=0):
        '''
        '''
        if ifNum not in self._ifDict.keys():
            return -3
        if not self._capThreadDict or not self._capThreadDict[ifNum]:
            return -1
        if self._capThreadDict[ifNum].xfstats == 1:
            return 1
        elif self._capThreadDict[ifNum].xfstats == 0:
            return 0
        elif self._capThreadDict[ifNum].xfstats == -2:
            return -2
        num = int(num)
        if num == 0:
            cap_hexstr = []
            for icap in self._capThreadDict[ifNum].xfcappacket:
                cap_hexstr.append(hexstr(str(icap),0,1))
            return cap_hexstr
        else:
            if num <= self._capThreadDict[ifNum].xfcapnum:
                cp = self._capThreadDict[ifNum].xfcappacket[num-1]
            else:
                cp = self._capThreadDict[ifNum].xfcappacket[-1]
            return hexstr(str(cp),0,1)

    def get_capture_status(self,ifNum):
        '''return status
           - -2 : error
           - -1 : ready to start or stoped
           -  1 : running
           -  0 : in stoping
        '''
        if ifNum not in self._ifDict.keys():
            return -2
        if not self._capThreadDict or not self._capThreadDict[ifNum]:
            return -3
        return self._capThreadDict[ifNum].xfstats

    def get_statics(self,ifNum,stats=None):
        '''get if stats 

            stats args: string list
            - rxpackets
            - rxbytes
            - rxpps
            - rxBps
            - txpackets
            - txbytes
            - txpps
            - txBps

            return: stats list

            example:
            - get_statics('1',['rxpps','txpps']) 
        '''
        if ifNum not in self._ifDict.keys():
            raise AssertionError("get_statics fail: %s not in ifList" % ifNum)
            return -2
        #iface = self._ifDict[ifNum]
        strflag = False
        if stats and type(stats) is not list:
            strflag = True
            stats = [stats]
        if stats:
            stats = ['xf'+istats for istats in stats]
        get_stats = stats or ['xfrxpackets','xfrxbytes','xfrxpps','xfrxBps',
                              'xftxpackets','xftxbytes','xftxpps','xftxBps'
                             ]
        ret_stats = []
        if not self._ifstatsThreadDict or not self._ifstatsThreadDict[ifNum]:
            raise AssertionError("get_statics fail: _ifstatsThreadDict not start")
            return -2
        for istats in get_stats:
            if hasattr(self._ifstatsThreadDict[ifNum],istats):
                stats_num = getattr(self._ifstatsThreadDict[ifNum],istats)
                return stats_num
                ret_stats.append(stats_num)
        if strflag:
            return ret_stats[0]
        return ret_stats

    def clear_statics(self,ifNum):
        ''''''
        if ifNum not in self._ifDict.keys():
            raise AssertionError("clear_statics fail: %s not in ifList" % ifNum)
            return -2
        #iface = self._ifDict[ifNum]
        if not self._ifstatsThreadDict or not self._ifstatsThreadDict[ifNum]:
            raise AssertionError("clear_statics fail: _ifstatsThreadDict not start")
            return -2
        self._ifstatsThreadDict[ifNum].clear_stats()
        #time.sleep(self._ifstatsThreadDict[ifNum].xftimeout)
        return 0


class XFSend(threading.Thread):
    '''send packet thread'''
    def __init__(self,iface,packet,mode,*args,**kwargs):
        '''xfstats -1: pending
                    1: running
                    0: stop
                   -2: error
        '''
        threading.Thread.__init__(self,*args,**kwargs)
        self._iface = iface
        self._sendPacket = packet
        #self._xfcount = count
        #self._xftimeout = timeout
        self._xfmode = mode
        self._xfstats = -1
        self._xfsendnum = 0
        self._args = args
        self._kwargs = kwargs
        self.errmsg = ''

    def start(self):
        ''''''
        self._xfstats = 1
        self._xfsendnum = 0
        threading.Thread.start(self)

    @property
    def xfstats(self):
        return self._xfstats

    @xfstats.setter
    def xfstats(self, value):
        self._xfstats = value

    @property
    def sendPacket(self):
        return self._sendPacket
    @sendPacket.setter
    def sendPacket(self, value):
        self._sendPacket = value

    # @property
    # def xfcount(self):
    #     return self._xfcount
    # @xfcount.setter
    # def xfcount(self, value):
    #     self._xfcount = value

    # @property
    # def xftimeout(self):
    #     return self._xftimeout
    # @xftimeout.setter
    # def xftimeout(self, value):
    #     self._xftimeout = value

    @property
    def xfsendnum(self):
        return self._xfsendnum

    def run(self):
        ''''''
        try:
            self.xfsendp(
                     self._sendPacket,iface=self._iface,
                     packet_mode=self._xfmode,*self._args,
                     **self._kwargs
                    )
            # if self._xfcount > 0:
            #     self.xfsendp(
            #         self._sendPacket,iface=self._iface,loop=0,
            #         count=self._xfcount,inter=self._xftimeout,*self._args,
            #         **self._kwargs
            #         )
            # else:
            #     self.xfsendp(
            #         self._sendPacket,iface=self._iface,loop=1,
            #         inter=self._xftimeout,*self._args,**self._kwargs
            #         )
        except Exception,ex:
            self._xfstats = -2
            self._xfsendnum = 0
            self.errmsg = str(ex)
        else:
            self._xfstats = -1

    def xfsendp(self,x, iface=None, packet_mode=None, verbose=None, realtime=None, *args, **kargs):
        '''override sendp'''
        # if iface is None and iface_hint is not None:
        #     iface = conf.route.route(iface_hint)[0]
        self.__xf__gen_send(conf.L2socket(iface=iface, *args, **kargs), x, mode=packet_mode, verbose=verbose, realtime=realtime)

    def __xf__gen_send(self,s, x, mode=None, verbose=None, realtime=None, *args, **kargs):
        '''override __gen__send'''
        if type(x) is str:
            x = Raw(load=x)
        # if not isinstance(x, Gen):
        #     x = SetGen(x)
        #if verbose is None:
            #verbose = conf.verb
        verbose = None
        #n = 0
        self._xfsendnum = 0
        pindex = 0
        #pindexStr = str(pindex)
        plen = len(x)
        pmode = mode[pindex][2]
        if  pmode == 0:
            count = None
        else:
            count = mode[pindex][3]
        inter = mode[pindex][0]
        preturnId = mode[pindex][4]
        while True:
            if count is not None:
                loop = -count
            else:
                loop=-1
            px = x[pindex]
            dt0 = None
            while loop:
                for p in px:
                    if realtime:
                        ct = time.time()
                        if dt0:
                            st = dt0+p.time-ct
                            if st > 0:
                                time.sleep(st)
                        else:
                            dt0 = ct-p.time 
                    s.send(p)
                    #n += 1
                    self._xfsendnum += 1
                    if self._xfstats == 0:
                        s.close()
                        return self._xfsendnum
                    #if verbose:
                        #sys.stdout.write(".")
                    time.sleep(inter)
                if loop < 0:
                    loop += 1
            #next stream
            if pmode == 1:
                break
            elif pmode == 2:
                pindex += 1
                #pindexStr = str(pindex)
            elif pmode == 3:
                #pindexStr = preturnId
                pindex = preturnId - 1
            else:
                pass
            if pindex >= plen:
                break
            pmode = mode[pindex][2]
            if  pmode == 0:
                count = None
            else:
                count = mode[pindex][3]
            inter = mode[pindex][0]
            preturnId = mode[pindex][4]

        s.close()
        #if verbose:
            #print "\nSent %i packets." % n
        return self._xfsendnum


class XFCapture(threading.Thread):
    '''capture packet thread'''

    def __init__(self,iface,timeout=0,xffilter=None,count=0,*args,**kwargs):
        '''xfstats -1: pending
                    1: running
                    0: stop
                   -2: error
        '''
        threading.Thread.__init__(self,*args,**kwargs)
        self._iface = iface
        self._xftimeout = timeout
        self._xfstats = -1
        self._xfcapnum = -1
        self._xfcount = count
        self._args = args
        self._kwargs = kwargs
        self.errmsg = ''
        self._has_epoll = True
        #self._has_epoll = hasattr(select, 'epoll')
        self._xfcappacket = None
        self._xffilter = xffilter
        self._xf_stop_pipe = None
        self._xf_l2listensocket = XFL2ListenSocket

    @property
    def xf_l2listensocket(self):
        return self._xf_l2listensocket
    @xf_l2listensocket.setter
    def xf_l2listensocket(self, value):
        self._xf_l2listensocket = value

    @property
    def xftimeout(self):
        return self._xftimeout
    @xftimeout.setter
    def xftimeout(self, value):
        self._xftimeout = value

    @property
    def xfstats(self):
        return self._xfstats
    @xfstats.setter
    def xfstats(self, value):
        self._xfstats = value
        if value == 0:
            if self._xf_stop_pipe:
                os.write(self._xf_stop_pipe[1],'s')

    @property
    def xfcount(self):
        return self._xfcount
    @xfcount.setter
    def xfcount(self, value):
        self._xfcount = value

    @property
    def xffilter(self):
        return self._xffilter
    @xffilter.setter
    def xffilter(self, value):
        self._xffilter = value

    @property
    def xfcapnum(self):
        return self._xfcapnum

    @property
    def xfcappacket(self):
        return self._xfcappacket

    def xf_stop_capture(self):
        ''''''
        self._xfstats = 0
        if self._xf_stop_pipe:
            os.write(self._xf_stop_pipe[1],'s')

    def start(self):
        ''''''
        self._xfstats = 1
        self._xfcapnum = 0
        self._xf_stop_pipe = os.pipe()
        threading.Thread.start(self)

    def run(self):
        ''''''
        try:
            if self._has_epoll:
                self._xfcappacket = self._xf_sniff_epoll(
                    count=self._xfcount,iface=self._iface,
                    timeout=self._xftimeout,filter=self._xffilter,
                    L2socket=self._xf_l2listensocket
                    )
            else:
                self._xfcappacket = self._xf_sniff_select(
                    count=self._xfcount,iface=self._iface,
                    timeout=self._xftimeout,filter=self._xffilter,
                    L2socket=self._xf_l2listensocket
                    )
        except Exception,ex:
            self._xfstats = -2
            self._xfcapnum = 0
            self._xfcappacket = None
            self.errmsg = str(sys.exc_info())
        else:
            self._xfstats = -1
            #self._xfcapnum = len(self._xfcappacket)
        if self._xf_stop_pipe:
            #os.read(self._xf_stop_pipe[0],1)
            self._xf_stop_pipe = None

    def _xf_sniff_select(self,count=0, store=1, offline=None, prn = None, lfilter=None, L2socket=None, timeout=None,opened_socket=None, stop_filter=None, *arg, **karg):
        """Sniff packets
            sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets
            count: number of packets to capture. 0 means infinity
            store: wether to store sniffed packets or discard them
            prn: function to apply to each packet. If something is returned,
            it is displayed. Ex:
            ex: prn = lambda x: x.summary()
            lfilter: python function applied to each packet to determine
            if further action may be done
            ex: lfilter = lambda x: x.haslayer(Padding)
            offline: pcap file to read packets from, instead of sniffing them
            timeout: stop sniffing after a given time (default: None)
            L2socket: use the provided L2socket
            opened_socket: provide an object ready to use .recv() on
            stop_filter: python function applied to each packet to determine
            if we have to stop the capture after this packet
            ex: stop_filter = lambda x: x.haslayer(TCP)
        """
        import select
        c = 0
        if opened_socket is not None:
            s = opened_socket
        else:
            if offline is None:
                if L2socket is None:
                    L2socket = conf.L2listen
                s = L2socket(type=ETH_P_ALL, *arg, **karg)
            else:
                s = PcapReader(offline)

        lst = []
        if timeout is not None:
            stoptime = time.time()+timeout
        remain = None
        while 1:
            try:
                if timeout is not None:
                    remain = stoptime-time.time()
                    if remain <= 0:
                        break
                sel = select.select([s,self._xf_stop_pipe[0]],[],[],remain)
                if s in sel[0] or self._xf_stop_pipe[0] in sel[0]:
                    if self._xfstats == 0:
                        break
                    p = s.recv(MTU)
                    if p is None:
                        break
                    elif p is False:
                        continue
                    if lfilter and not lfilter(p):
                        continue
                    if store:
                        lst.append(p)
                    c += 1
                    self._xfcapnum += 1
                    if prn:
                        r = prn(p)
                        if r is not None:
                            print r
                    if stop_filter and stop_filter(p):
                        break
                    if count > 0 and c >= count:
                        break
                    #if self._xfstats == 0:
                    #    break
            except KeyboardInterrupt:
                break
        if opened_socket is None:
            s.close()
        return plist.PacketList(lst,"Sniffed")

    def _xf_sniff_epoll(self,count=0, store=1, offline=None, prn = None,
        lfilter=None,L2socket=None, timeout=None,opened_socket=None, stop_filter=None, *arg, **karg):
        """ override scapy sniff
        Sniff packets
        sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets

        count: number of packets to capture. 0 means infinity
        store: wether to store sniffed packets or discard them
        prn: function to apply to each packet. If something is returned,
            it is displayed. Ex:
            ex: prn = lambda x: x.summary()
        lfilter: python function applied to each packet to determine
             if further action may be done
            ex: lfilter = lambda x: x.haslayer(Padding)
        offline: pcap file to read packets from, instead of sniffing them
        timeout: stop sniffing after a given time (default: None)
        L2socket: use the provided L2socket
        opened_socket: provide an object ready to use .recv() on
        stop_filter: python function applied to each packet to determine
             if we have to stop the capture after this packet
             ex: stop_filter = lambda x: x.haslayer(TCP)
        """
        import select,socket
        c = 0
        if opened_socket is not None:
            s = opened_socket
        else:
            if offline is None:
                if L2socket is None:
                    L2socket = conf.L2listen
                s = L2socket(type=ETH_P_ALL, *arg, **karg)
                s.ins.setblocking(0)
            else:
                s = PcapReader(offline)

        lst = []
        if timeout is not None:
            stoptime = time.time()+timeout
        remain = None
        poller = select.epoll()
        poll_in_or_priority_flags = select.EPOLLIN
        poller.register(s, poll_in_or_priority_flags | select.EPOLLET)
        poller.register(self._xf_stop_pipe[0],poll_in_or_priority_flags | select.EPOLLET)
        while 1:
            try:
                if timeout is not None:
                    remain = stoptime-time.time()
                    if remain <= 0:
                        break
                #sel = select([s],[],[],remain)
                ready = poller.poll(-1 if remain is None
                                    else remain)
                for fd, mode in ready:
                    if self._xf_stop_pipe[0] == fd:
                        if opened_socket is None:
                            s.close()
                        return plist.PacketList(lst,"Sniffed")
                    else:
                        try:
                            while True:
                                p = s.recv(MTU)
                                if p is None:
                                    break
                                elif p is False:
                                    continue
                                if lfilter and not lfilter(p):
                                    continue
                                if store:
                                    lst.append(p)
                                c += 1
                                self._xfcapnum += 1
                                if prn:
                                    r = prn(p)
                                    if r is not None:
                                        print r
                                if stop_filter and stop_filter(p):
                                    if opened_socket is None:
                                        s.close()
                                    return plist.PacketList(lst,"Sniffed")
                                if count > 0 and c >= count:
                                    if opened_socket is None:
                                        s.close()
                                    return plist.PacketList(lst,"Sniffed")
                        except socket.error:
                            pass
                if self._xfstats == 0:
                    break
            except KeyboardInterrupt:
                break
        if opened_socket is None:
            s.close()
        return plist.PacketList(lst,"Sniffed")


class XFIfStats(threading.Thread):
    '''interface throuput stats'''
    def __init__(self,iface,timeout=None,*args,**kwargs):
        '''xfstats -1: pending
                    1: running
                    0: stop
                   -2: error
        '''
        threading.Thread.__init__(self,*args,**kwargs)
        self._iface = iface
        self._xftimeout = timeout or 1
        self._xfstats = -1
        self._xftxbytes = 0
        self._xftxbytes = 0
        self._xftxpackets = 0
        self._xftxpackets = 0
        self._xftxpps = 0
        self._xftxpps = 0
        self._xfrxbytes = 0
        self._xfrxbytes = 0
        self._xfrxpackets = 0
        self._xfrxpps = 0
        self._xftxBps = 0
        self._xfrxBps = 0
        self._xf_bm_txbytes = 0
        self._xf_bm_rxbytes = 0
        self._xf_bm_txpackets = 0
        self._xf_bm_rxpackets = 0
        self._args = args
        self._kwargs = kwargs
        self.errmsg = ''
        self._net_dir = '/sys/class/net'
        self._xf_rxbytes_file = None
        self._xf_rxpackets_file = None
        self._xf_txbytes_file = None
        self._xf_txpackets_file = None
        self._xfclearstats = 0

    def verify_if_file(self):
        ''''''
        #for ifname in self._ifaceList:
        ifStatsPath = os.path.join(self._net_dir,self._iface,'statistics')
        if not os.path.exists(ifStatsPath):
            return False
        self._xf_rxbytes_file = os.path.join(ifStatsPath,'rx_bytes')
        self._xf_rxpackets_file = os.path.join(ifStatsPath,'rx_packets')
        self._xf_txbytes_file = os.path.join(ifStatsPath,'tx_bytes')
        self._xf_txpackets_file = os.path.join(ifStatsPath,'tx_packets')
        return True

    @property
    def xftxbytes(self):
        return self._xftxbytes

    @property
    def xftxpps(self):
        return self._xftxpps

    @property
    def xfrxbytes(self):
        return self._xfrxbytes

    @property
    def xfrxpps(self):
        return self._xfrxpps

    @property
    def xftxpackets(self):
        return self._xftxpackets

    @property
    def xfrxpackets(self):
        return self._xfrxpackets

    @property
    def xftxBps(self):
        return self._xftxBps

    @property
    def xfrxBps(self):
        return self._xfrxBps

    @property
    def xfstats(self):
        return self._xfstats
    @xfstats.setter
    def xfstats(self, value):
        self._xfstats = value

    @property
    def xftimeout(self):
        return self._xftimeout
    @xftimeout.setter
    def xftimeout(self, value):
        self._xftimeout = value

    def clear_stats(self):
        ''''''
        self._xfclearstats = 1

    def start(self):
        ''''''
        self._xfstats = 1
        #for ifname in self._ifaceList:
        self._xfclearstats = 0
        self.build_benchmark()
        threading.Thread.start(self)

    def build_benchmark(self):
        with open(self._xf_rxpackets_file) as f:
            self._xf_bm_rxpackets = long(f.read())
        with open(self._xf_txpackets_file) as f:
            self._xf_bm_txpackets = long(f.read())
        with open(self._xf_rxbytes_file) as f:
            self._xf_bm_rxbytes = long(f.read())
        with open(self._xf_txbytes_file) as f:
            self._xf_bm_txbytes = long(f.read())

    def run(self):
        ''''''
        while self._xfstats:
            #check all iface
            #for ifname in self._ifaceList:
                #check clear_stats flag
            if self._xfclearstats:
                self._xfrxpackets = 0
                self._xftxpackets = 0
                self._xftxbytes = 0
                self._xfrxbytes = 0
                self.build_benchmark()
                self._xfclearstats = 0
            #save prio stats to compute rate
            prio_rx_packets = self._xfrxpackets
            prio_tx_packets = self._xftxpackets
            prio_tx_bytes = self._xftxbytes
            prio_rx_bytes = self._xfrxbytes
            #read stats file
            with open(self._xf_rxpackets_file) as f:
                rx_packets = long(f.read()) - self._xf_bm_rxpackets
            with open(self._xf_txpackets_file) as f:
                tx_packets = long(f.read()) - self._xf_bm_txpackets
            with open(self._xf_rxbytes_file) as f:
                rx_bytes = long(f.read()) - self._xf_bm_rxbytes + 4*rx_packets
            with open(self._xf_txbytes_file) as f:
                tx_bytes = long(f.read()) - self._xf_bm_txbytes + 4*tx_packets
            #compute stats num
            self._xftxbytes = tx_bytes
            self._xftxpackets = tx_packets
            self._xfrxbytes = rx_bytes
            self._xfrxpackets = rx_packets
            #compute stats rate
            self._xftxpps = tx_packets - prio_tx_packets
            self._xfrxpps = rx_packets - prio_rx_packets
            self._xftxBps = tx_bytes - prio_tx_bytes
            self._xfrxBps = rx_bytes - prio_rx_bytes
            #sleep 1s
            time.sleep(self._xftimeout)

class XFL2ListenSocket(L2ListenSocket):
    '''
    override the method recv
    only recv the data of rx wire,not tx wire
    '''

    def recv(self, x=MTU):
        pkt, sa_ll = self.ins.recvfrom(x)
        if sa_ll[2] == socket.PACKET_OUTGOING:
            return False
        if sa_ll[3] in conf.l2types :
            cls = conf.l2types[sa_ll[3]]
        elif sa_ll[1] in conf.l3types:
            cls = conf.l3types[sa_ll[1]]
        else:
            cls = conf.default_l2
            warning("Unable to guess type (interface=%s protocol=%#x family=%i). Using %s" % (sa_ll[0],sa_ll[1],sa_ll[3],cls.name))

        try:
            pkt = cls(pkt)
        except KeyboardInterrupt:
            raise
        except:
            if conf.debug_dissector:
                raise
            pkt = conf.raw_layer(pkt)
        pkt.time = get_last_packet_timestamp(self.ins)
        return pkt


class XFServer(object):
    '''
    '''
    def __init__(self,port,mode,tp,hostip):
        '''
        '''
        self.bindport = port
        self.server_mode = mode
        self.tester_portList = tp.split(",")
        self.host = hostip
        self.xf = None
        self.robot_handler = None
        self.rpyc_handler = None
        os.system('iptables -F')

    def runRobotServer(self):
        '''
        '''
        self.robot_handler = robotremoteserver.RobotRemoteServer(
            self.xf,host=self.host,port=self.bindport
            )

    def runRpycServer(self):
        '''
        '''
        from rpyc.utils.server import ThreadedServer
        self.rpyc_handler = ThreadedServer(DsendService,hostname=self.host,port=self.bindport,auto_register=False)
        self.rpyc_handler.start()

    def runServer(self):
        '''
        '''
        self.xf = XiaoFish(self.tester_portList)
        if self.server_mode == '1':
            self.runRobotServer()
        elif self.server_mode == '2':
            DsendService.xf = self.xf
            DsendService.init_ctrlStreamFlag(len(self.tester_portList))
            self.runRpycServer()
        else:
            pass


class DsendService(rpyc.Service):
    '''
    '''
    xf = None
    xf_ctrlStreamFlag = {}

    @classmethod
    def init_ctrlStreamFlag(cls,portnum):
        '''
        '''
        for i in range(portnum):
            pindex = str(i+1)
            cls.xf_ctrlStreamFlag[pindex] = 0


    def exposed_getRate(self,port,stat_type):
        '''
        '''
        if stat_type == 'packetSendRate':
            ret = DsendService.xf.get_statics(port,'txpps')
        elif stat_type == 'byteSendRate':
            ret = DsendService.xf.get_statics(port,'txBps')
        elif stat_type== 'packetReceiveRate':
            ret = DsendService.xf.get_statics(port,'rxpps')
        elif stat_type == 'byteReceiveRate':
            ret = DsendService.xf.get_statics(port,'rxBps')
        elif stat_type == 'packetSendNum':
            ret = DsendService.xf.get_statics(port,'txpackets')
        elif stat_type == 'byteSendNum':
            ret = DsendService.xf.get_statics(port,'txbytes')
        elif stat_type== 'packetReceiveNum':
            ret = DsendService.xf.get_statics(port,'rxpackets')
        elif stat_type == 'byteReceiveNum':
            ret = DsendService.xf.get_statics(port,'rxbytes')
        elif stat_type == 'debug':
            ret = None
        else:
            ret = None
        return ret

    def exposed_handle(self,proc,port,args):
        '''
        '''
        if proc == "startCapture":
            ret = DsendService.xf.capture_packet(port)
        elif proc == "stopCapture":
            ret = DsendService.xf.stop_capture(port)
        elif proc == "getPcapFname":
            ret = "xfserver"
        elif proc == "getPcapFile":
            ret = DsendService.xf.get_capture_packet_hexstr(port)
        elif proc == "restartServer":
            #do not restart,only return 0
            ret = 0
        elif proc == "getCaptureBuffer":
            args = str(args)
            num = DsendService.xf.get_capture_packet_num(port)
            if num == 0:
                return dumps([])
            #capture args
            if args == "all":
                hstrList = DsendService.xf.get_capture_packet_hexstr(port)
            elif args == "count":
                hstrList = str(num)
            elif args.find('detail') >= 0:
                inum=args.replace('detail','')
                hstrList = DsendService.xf.get_capture_packet_hexstr(port,inum)
            elif args.find('pak') > 0:
                requireNumber=args.replace('pak','')
                if num >= int(requireNumber):
                    num = int(requireNumber)
                bufferItem = DsendService.xf.get_capture_packet_hexstr(port)
                hstrList = bufferItem[:num]
            elif args.find('pak') == 0:
                requireNumber=args.replace('pak','')
                if num >= int(requireNumber):
                    num = int(requireNumber)
                bufferItem = DsendService.xf.get_capture_packet_hexstr(port)
                hstrList = bufferItem[-num:]
            else:
                requireNumber = int(args)
                hstrList = DsendService.xf.get_capture_packet_hexstr(port,requireNumber)
            return dumps(hstrList)
        elif proc == "getPortStatus":
            ret = "NULL"
        elif proc == "setStream":
            ret = self.set_stream(port,args)
        elif proc == "startTransmit":
            ret = DsendService.xf.send_stream(port)
        elif proc == "stopTransmit":
            ret = DsendService.xf.stop_stream(port)
        elif proc == "clearStatistic":
            ret = DsendService.xf.clear_statics(port)
        elif proc == "resetPortState":
            ret1 = DsendService.xf.stop_capture(port)
            ret2 = DsendService.xf.stop_stream(port)
            ret3 = DsendService.xf.clear_stream(port)
            ret4 = DsendService.xf.clear_statics(port)
            ret = 0
        elif proc == "getPortState":
            ret = 0
        elif proc == "getSendState":
            ret = DsendService.xf.get_send_stream_status(port)
            if ret == 1:
                pass
            else:
                ret = 0
        elif proc == "getStream":
            ret = DsendService.xf.get_stream(port)
        elif proc == "getPortDetail":
            # ret1 = self.xf.get_stream(port)
            # retx2 = self.xf.get_send_stream_status(port)
            # retx3 = self.xf.get_stream_control(port)
            # retx4 = self.xf.get_stream_packet_size(port)
            # if retx2 == 1:
            #     ret1 = 1
            # else:
            #     ret1 = 0
            # ret2 = 
            # retList = []
            ret = 0
        elif proc == "quit":
            ret = DsendService.xf.stop_stream(port)
        else:
            ret = 'Please input correct function name!'
        return dumps(str(ret))

    def set_stream(self,port,args):
        '''
        '''
        if port not in DsendService.xf_ctrlStreamFlag.keys():
            return "port %s not exists" % port
        sindex = DsendService.xf_ctrlStreamFlag[port]
        if sindex == 0:
            DsendService.xf.clear_stream(port)
        sindex += 1
        lastStreamFlag = 1             ;#是否最后一条流:Y=1,N=0
        rate = 100                     ;#报文发送速率
        streamMode = 'percent'         ;#报文速率配置模式:(pps/bps/percent)
        streamSize = 256               ;#报文长度
        ppsRate = 10                   ;#发送速率换算成pps
        mode = 0                       ;#报文发送模式: (0:PC控制速率;1:交换机控制速率)
        count = 0                      ;#发送指定数量报文后停止
        countContinue = 0              ;#发送指定数量报文后继续
        load = ''
        #deal with args:
        streamValue = None
        incrList = []
        incrMaxNum = 1                 ;#某写字段递增报文,最大递增个数
        incrCount = 0
        for name,value in args:
            if name == "stream":
                streamValueTemp=str(value)
                dot1q_re = re.compile("/Dot3Tag\\(vlan=%s,[^)]*\\)" % port)
                streamValueTemp = dot1q_re.sub("",streamValueTemp,1)
                payloadTemp = re.search("/\"payloadflag(.*)payloadflag\"",streamValueTemp)
                replaceString = ''
                if payloadTemp is not None:
                    for i in range (0,len(payloadTemp.group(1))/2):
                        replaceString += binascii.a2b_hex(payloadTemp.group(1)[i*2:i*2+2])
                streamValueTemp = re.sub("/\"payloadflag(.*)payloadflag\"","",streamValueTemp)
                #rawstream += 'stream ' + streamValueTemp + ' '
            elif str(name).find('incr') >= 0:
                exec(name+' = '+value)
                #rawstream += name + ' ' + value + ' '
                incrList.append([name,value])
                clearvalue = value.replace('\'','')
                thisnum = clearvalue.split(',')[1]
                tempMax = int(thisnum) * int(incrMaxNum)
                incrMaxNum = tempMax / calcGCD(int(thisnum),int(incrMaxNum))
            elif name == "rate":
                rate = value
            elif name == "mode":
                mode = value
            elif name == "streamMode":
                streamMode = value
            elif name == "streamSize":
                streamSize = value
            elif name == "lastStreamFlag":
                lastStreamFlag = int(value)
            elif name == "count":
                count = int(value)
            elif name == "countContinue":
                countContinue = int(value)
            else:
                pass
        #compute pps
        if (str(streamSize) == 'auto') | (str(streamSize) == 'Auto'):
            streamSize = 64
        if str(streamMode) == 'bps':
            ppsRate = int(rate)/int(streamSize)/8
        elif str(streamMode) == 'pps':
            ppsRate = int(rate)
        elif str(streamMode) == 'percent':
            return "not support line speed percent mode"
        else:
            return 'streamMode is %s,Please input correct streamMode' % streamMode
        #compute incr field
        for k in incrList:
            basicAndNum = k[1].replace('\'','')
            basicAndNum = basicAndNum.split(',')
            basic = basicAndNum[0]
            num = basicAndNum[1]
            ipv4Network = 'classD'
            ipv6Network = 128
            step = 1
            if len(basicAndNum) == 3:
                ipv4Network = ipv6Network = basicAndNum[2]
            elif len(basicAndNum) == 4:
                ipv4Network = ipv6Network = basicAndNum[2]
                step = basicAndNum[3]
            if k[0].find('Mac') >= 0:
                resList = setIncrMacList(basic,num,incrMaxNum)
            elif k[0].find('Ipv6') >= 0:
                #print basic,num,self.incrMaxNum,ipv6Network,step
                resList= setIncrIpv6List(basic,num,incrMaxNum,ipv6Network,step)
            elif k[0].find('Ip') >= 0:
                resList = setIncrIpList(basic,num,incrMaxNum,ipv4Network,step)
            elif k[0].find('Num') >= 0:
                resList = setIncrNumList(basic,num,incrMaxNum)
            else:
                pass
            exec(k[0]+'='+'resList')
        #add payload according streamsize
        streamValue = eval(streamValueTemp)
        streamLen=len(streamValue)
        load = replaceString
        for p in range(0,int(streamSize)-streamLen-len(replaceString) - 4):
            load +='\x00'
        #config stream
        stream = []
        countList = [count]
        if countContinue > 0:
            continueCountList = getCountList(incrMaxNum,countContinue)
        if (count >= 1) and (incrMaxNum>1):
            countList = getCountList(incrMaxNum,count)
        for incrCount in range(0,int(incrMaxNum)):
            streamValue = eval(streamValueTemp)
            streamValue = streamValue/load
            stream.append(streamValue)
            if count > 0:
                xf_count = countList[incrCount]
            elif countContinue > 0:
                xf_count = continueCountList[incrCount]
            else:
                xf_count = 1
        xf_rate = ppsRate
        if count == 0 and countContinue == 0:
            if lastStreamFlag == 0:
                xf_mode = 2
            else:
                xf_mode = 0
        elif count == 0 and countContinue > 0:
            if lastStreamFlag == 0:
                xf_mode = 2
            else:
                xf_mode = 3
        else:
            if lastStreamFlag == 0:
                xf_mode = 2
            else:
                xf_mode = 1
        DsendService.xf.set_stream_from_dsend(port,stream,str(sindex))
        if xf_mode == 3:
            DsendService.xf.set_stream_control(port,str(sindex),xf_rate,1,xf_mode,xf_count,1)
        else:
            DsendService.xf.set_stream_control(port,str(sindex),xf_rate,1,xf_mode,xf_count,1)
        #set ctrlStreamFlag
        if lastStreamFlag == 0:
            DsendService.xf_ctrlStreamFlag[port] = sindex
        else:
            DsendService.xf_ctrlStreamFlag[port] = 0
        return xf_mode


def calcGCD(intA,intB):
    if int(intB) == 0:
        return intA
    else:
        return calcGCD(intB,intA % intB)

def setIncrMacList(value,num,maxnum):
    num=int(num)
    maxnum=int(maxnum)
    valueTemp=value
    valueList=[]
    for i in range(1,int(maxnum)+1):
        valueList.append(value)
        valueInt=int(value.replace(':',''),16)
        valueInt+=1
        value=hex(valueInt)
        value=str(value).replace('0x','')
        value=value.replace('L','')
        for k in range(0,(12-len(value))):
            value='0'+str(value)
        value=value[0:2]+':'+value[2:4]+':'+value[4:6]+':'+value[6:8]+':'+value[8:10]+':'+value[10:12]
        if i%num == 0:
            value=valueTemp
    return valueList

def setIncrIpList(value,num,maxnum,mode='classD',step=1):
    num=int(num)
    maxnum=int(maxnum)
    step=int(step)
    valueTemp=value
    valueList=[]
    if mode=='classD':
        mode=0
    elif mode=='classC':
        mode=1
    elif mode=='classB':
        mode=2
    elif mode=='classA':
        mode=3
    for i in range(1,int(maxnum)+1):
        valueList.append(value)
        valueInt=socket.ntohl(struct.unpack("I",socket.inet_aton(value))[0])
        valueInt+=(256**mode)*step
        value=socket.inet_ntoa(struct.pack('I',socket.htonl(valueInt)))
        if i%num == 0:
            value=valueTemp
    return valueList

def setIncrIpv6List(ipv6addr,num,maxnum,network=128,step=1):
    sep=":"
    maxnum=int(maxnum)
    step=int(step)
    network=int(network)
    num=int(num)-1
    a=ipv6addr.split(sep)
    num1=len(a)
    num2=a.count("")
    num3=8 - num1 + num2
    if num2==1:
        index=a.index("")
        i=1
        while i < num3 + 1:
            a.insert(index+i,"0")
            i += 1
        del a[index]
    ipv6list=[sep.join(a)]
    temp1=sep.join(a)
    duan=network/16 - 1
    tmp=temp2=int(a[duan],16)
    j=1
    while j < maxnum:
        tmp += step
        a[duan]="%X" % tmp
        ipv6list.append(sep.join(a))
        if (j%num == 0) & (maxnum-j>1):
            tmp=temp2
            ipv6list.append(temp1)
            maxnum=maxnum-1
        j+=1
    return ipv6list

def setIncrNumList(value,num,maxnum):
    value=int(value)
    num=int(num)
    maxnum=int(maxnum)
    valueTemp=value
    valueList=[]
    for i in range(1,int(maxnum)+1):
        valueList.append(value)
        value+=1
        if i%num == 0:
            value=valueTemp
    return valueList

def getCountList(num,count):
    countList=[]
    for i in range(0,num):
        countList.append(count/num)
    for k in range(0,count%num):
        countList[k] += 1
    return countList

def usage():
    print("usage")


if __name__ == '__main__':
    if os.geteuid() != 0:
        print('should be run as root,please check')
        sys.exit(2)
    #get argv
    import getopt
    bindport = 11918
    server_mode = "1"
    test_port = None
    action = "start"
    host = '0.0.0.0'
    xfdetach = False
    opts,args = getopt.getopt(sys.argv[1:],'hdp:m:i:t:o:',['help','detach','port=','iface=','mode=','action=','host='])
    for opt,arg in opts:
        if opt in ("-h","--help"):
            usage()
            sys.exit(1)
        elif opt in ("-p","--port"):
            try:
                bindport = int(arg)
            except Exception:
                usage()
                sys.exit(1)
        elif opt in ("-m","--mode"):
            server_mode = arg
        elif opt in ("-i","--iface"):
            test_port = arg
        elif opt in ("-t","--action"):
            action = arg
        elif opt in ("-o","--host"):
            host = arg
        elif opt in ("-d","--detach"):
            xfdetach = True
        else:
            pass
    #xf server instance
    if not test_port:
        usage()
        sys.exit(3)
    s = XFServer(bindport,server_mode,test_port,host)
    #detach the xiaofish
    daemon = daemonocle.Daemon(
        worker=s.runServer,detach=xfdetach,pidfile='/tmp/daemonocle_xiaofish.pid',
        )
    daemon.do_action(action)