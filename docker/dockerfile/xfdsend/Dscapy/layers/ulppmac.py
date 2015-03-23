
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *

class ULPPMAC(Packet):
    name = "ULPPARP"
    fields_desc = [ ShortField("vlanid", 1),
	            ShortField("type", 0xdc0b),
                    ByteField("ctrltype", 1),
                    ByteField("macnum", 0),
                    ShortField("ctrlvlan", 1),
                    ShortField("pktlen", 6),
                    ]
    def post_build(self, p, pay):
        p += pay
        return p

class MacList(Packet):
    name = "MacList"
    fields_desc = [ ShortField("vid", 0),
                    MACField("mac", ETHER_ANY),
                    ]
    def post_build(self, p, pay):
        p += pay
        return p

bind_layers( ULPPMAC, MacList, )
