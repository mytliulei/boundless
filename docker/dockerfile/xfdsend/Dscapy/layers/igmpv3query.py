
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *
from scapy.layers.igmpv3report import *

class IGMPv3Query(Packet):
    name = "IGMPv3Query"
    fields_desc = [ XByteField("version",0x11),
                    XByteField("maxres",0x64),
                    XShortField("chksum", None),
                    IPField("group","0.0.0.0"),
                    XByteField("resv",0x00),
                    XByteField("qqic",0x00),
                    XShortField("sournum", 0x0000),
                  ]
    def post_build(self, p, pay):
        p += pay
        if self.chksum is None:
            ck = checksum(p)
            p = p[:2]+chr(ck>>8)+chr(ck&0xff)+p[4:]
        return p

bind_layers( IP,           IGMPv3Query,           proto=2)
bind_layers( IGMPv3Query,       SrcList,     )
