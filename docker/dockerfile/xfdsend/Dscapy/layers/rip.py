## This file is part of Scapy
## See http://www.secdev.org/projects/scapy for more informations
## Copyright (C) Philippe Biondi <phil@secdev.org>
## This program is published under a GPLv2 license

from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import UDP
from scapy.utils6 import *
from scapy.layers.inet6 import *

class RIP(Packet):
    name = "RIP header"
    fields_desc = [
        ByteEnumField("cmd",1,{1:"req",2:"resp",3:"traceOn",4:"traceOff",5:"sun",
                               6:"trigReq",7:"trigResp",8:"trigAck",9:"updateReq",
                               10:"updateResp",11:"updateAck"}),
        ByteField("version",1),
        ShortField("null",0),
        ]

class RIPEntry(Packet):
    name = "RIP entry"
    fields_desc = [
        ShortEnumField("AF",2,{2:"IP"}),
        ShortField("RouteTag",0),
        IPField("addr","0.0.0.0"),
        IPField("mask","0.0.0.0"),
        IPField("nextHop","0.0.0.0"),
        IntEnumField("metric",1,{16:"Unreach"}),
        ]
        
class RIPng(RIP):
    name = "RIPng header"
    
class RIPngEntry(Packet):
    name = "RIPng entry"
    fields_desc = [
        IP6Field("addr","::"),
        ShortField("Tag",0),
        ByteField("prefixlen",64),
        ByteField("metric",1),
        ] 

bind_layers( UDP,           RIP,           sport=520)
bind_layers( UDP,           RIP,           dport=520)
bind_layers( UDP,           RIPng,         sport=521)
bind_layers( UDP,           RIPng,         dport=521)
bind_layers( RIP,           RIPEntry,      )
bind_layers( RIPng,         RIPngEntry,    )
bind_layers( RIPEntry,      RIPEntry,      )
bind_layers( RIPngEntry,    RIPngEntry,    )


