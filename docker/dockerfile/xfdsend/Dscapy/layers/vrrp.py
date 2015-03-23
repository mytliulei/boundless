
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *

class VRRP(Packet):
    name = "VRRP"
    fields_desc = [ BitField("version", 2, 4),
	            BitField("pkttype", 1, 4),
                    ByteField("id",10),
                    ByteField("pri",100),
                    ByteField("count",1),
                    ByteField("authtype",0),
                    ByteField("advint",1),
                    XShortField("chksum", None),
                    IPField("addr","0.0.0.0"),
                    ]
    def post_build(self, p, pay):
        p += pay
        if self.chksum is None:
            ck = checksum(p)
            p = p[:6]+chr(ck>>8)+chr(ck&0xff)+p[8:]
        return p


bind_layers( IP,           VRRP,           proto=112)
