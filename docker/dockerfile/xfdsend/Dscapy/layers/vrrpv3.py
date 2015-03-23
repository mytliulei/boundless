import struct
from scapy.packet import *
from scapy.fields import *
from scapy.utils6 import *
from scapy.layers.inet6 import *

class VRRPv3(Packet):
    name = "VRRPv3"
    fields_desc = [ BitField("version", 3, 4),
                    BitField("pkttype", 1, 4),
                    ByteField("id",10),
                    ByteField("pri",100),
                    ByteField("count",1),
                    ShortField("advint",500),
                    XShortField("cksum", None),
                    IP6Field("addr","::"),
                    ]
    
    def post_build(self, p, pay):
        p += pay
        if self.cksum == None: 
            chksum = in6_chksum(112, self.underlayer, p)
            p = p[:6]+struct.pack("!H", chksum)+p[8:]
        return p


bind_layers( IPv6,           VRRPv3,           nh=112)
bind_layers( IPv6,           VRRPv3,           hlim=255)
