from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *

class IGMP(Packet):
    name = "IGMP"
    fields_desc = [ XByteField("version",0x11),
                    XByteField("maxres",0x64), 
                    XShortField("chksum", None),
                    IPField("group","0.0.0.0"),
                    ]
    def post_build(self, p, pay):
        p += pay
        if self.chksum is None:
            ck = checksum(p)
            p = p[:2]+chr(ck>>8)+chr(ck&0xff)+p[4:]
        return p



bind_layers( IP,           IGMP,           proto=2)
