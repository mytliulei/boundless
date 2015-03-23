
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *

class IGMPv3Report(Packet):
    name = "IGMPv3Report"
    fields_desc = [ XByteField("version",0x22),
                    XByteField("res1",0x00),
                    XShortField("chksum", None),
		    XShortField("res2",0x0000),
                    XShortField("numrec",0x0001),
                    ]
    def post_build(self, p, pay):
        p += pay
        if self.chksum is None:
            ck = checksum(p)
            p = p[:2]+chr(ck>>8)+chr(ck&0xff)+p[4:]
        return p

class IGMPv3Record(Packet):
    name = "IGMPv3Record"
    fields_desc = [ XByteField("rectype",0x01),
                    XByteField("datalen",0x00),
                    XShortField("numsour",0x0001),
                    IPField("group","0.0.0.0"),
                    ]

class SrcList(Packet):
    name = "SrcList"
    fields_desc = [IPField("source","0.0.0.0"),]

bind_layers( IP,           IGMPv3Report,           proto=2)
bind_layers( IGMPv3Report,       IGMPv3Record,     )
bind_layers( IGMPv3Record, SrcList,     )
