
from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *

class ULPPARP(Packet):
    name = "ULPPARP"
    fields_desc = [ ShortField("vlanid", 1),
	            ShortField("type", 0xdc0b),
                    ByteField("ctrltype", 2),
                    ByteField("macnum", 0),
                    ShortField("ctrlvlan", 1),
                    ShortField("pktlen", 518),
                    BitField("bitmap", 0, 4096),
                    ]
    def post_build(self, p, pay):
        p += pay
        return p

