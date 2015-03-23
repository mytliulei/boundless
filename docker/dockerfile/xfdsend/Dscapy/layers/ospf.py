
## This file is part of Scapy
## See http://www.secdev.org/projects/scapy for more informations
## Copyright (C) Philippe Biondi <phil@secdev.org>
## This program is published under a GPLv2 license

from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import IP
#from scapy.utils6 import *
#from scapy.layers.inet6 import *

class OSPF(Packet):
    name = "OSPF Header"
    fields_desc = [
        ByteField("version",2),
        ByteEnumField("type",1,{1:"Hello",2:"DD",3:"Link State Request",4:"Link State Update",5:"Link State ACK"}),
        ShortField("len",None),
        IPField("routerid","121.0.0.2"),
        IPField("areaid","0.0.0.0"),
        ShortField("chksum", None),
        ShortField("authtype",0),
        LongField("value",0),
        ]
    def post_build(self, p, pay):
        p += pay
        if self.len is None:
            l = len(p)
            p = p[:2]+struct.pack("!H", l)+p[4:]
        if self.chksum is None:
            ck = checksum(p)
            p = p[:12]+chr(ck>>8)+chr(ck&0xff)+p[14:]
        return p

class OSPFHello(Packet):
    name = "OSPFHello"
    fields_desc = [
        IPField("mask","255.255.255.0"),
        ShortField("interval",10),
        ByteField("cap",2),
        ByteField("pri",0),
        ShortField("deadinterhigh",0),
        ShortField("deadinterlow",40),
        IPField("dr","121.0.0.2"),
        IPField("br","121.0.0.1"),
        IPField("neighbor","11.11.11.11"),
        ]

class OSPFDD(Packet):
    name = "OSPF Databace Description"
    fields_desc = [
        ShortField("mtu",1500),
        ByteField("cap",2),
        ByteField("flags",7),
        XShortField("seqnumhigh",0xffff),
        XShortField("seqnumlow",0xffff),
        ]

class OSPFLSA(Packet):
    name = "OSPF Link State Advertisement"
    fields_desc = [
        ShortField("age",1),
        ByteField("cap",0),
        ByteField("type",1),
        IPField("id","0.0.0.0"),
        IPField("adverrouter","0.0.0.0"),
        XShortField("seqnumhigh",0xffff),
        XShortField("seqnumlow",0xffff),
        ShortField("chksum",None),
        ShortField("len",None),
        ]
    def post_build(self, p, pay):
        if self.len is None:
            
            l = len(p)
            p = p[:18]+struct.pack("!H", l)
        if self.chksum is None:
            ck = checksum(p)
            p = p[:16]+chr(ck>>8)+chr(ck&0xff)+p[18:]
        return p+pay

class OSPFAdverNum(Packet):
    name = "OSPF Number Of Advertisements"
    fields_desc = [
        ShortField("advernumhigh",0),
        ShortField("advernumlow",0),
        ]
bind_layers( IP,           OSPF,           proto=89)
