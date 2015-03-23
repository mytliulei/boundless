from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *



class Uldp(Packet):
    name = "uldp packet,from Length to end"
    fields_desc = [ XShortField("len", 0x0022),
    		    XShortField("uldpid", 0x0001),
    		    XByteField("version",0x01),
    		    XByteField("type",0x01),
    		    XByteField("flag",0x00),
    		    XByteField("auth_mode",0x00),
    		    StrField("password","\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
    		    XShortField("hello_interval", 0x000A),
    		    XShortField("reserved", 0x0000),
    		    MACField("devicemac","00:03:0f:00:00:01"),
    		    XShortField("portid", 0x0001),
    		    MACField("portmac","00:00:00:00:00:00"),
    		    XShortField("portindex", 0x0000) ]