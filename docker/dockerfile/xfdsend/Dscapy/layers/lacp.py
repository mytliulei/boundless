from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *



class Lacppdu(Packet):
    name = "LACP PDU packet,from version number to end"
    fields_desc = [ XByteField("subtype",0x01),
    		    XByteField("version",0x01),
    		    XByteField("tlvtype1",0x01),
    		    XByteField("act_len",0x14),
    		    XShortField("act_pri", 0x8000),
    		    MACField("act_sys","00:00:01:00:00:01"),
    		    XShortField("act_key", 0x0001),
    		    XShortField("act_portpri", 0x8000),
    		    XShortField("act_port", 0x0001),
    		    XByteField("act_state",0x3D),
    		    X3BytesField("reserved1",0x000000),
    		    XByteField("tlvtype2",0x02),
    		    XByteField("partner_len",0x14),
    		    XShortField("partner_pri",0x0000),
    		    MACField("partner_sys","00:00:01:00:00:01"),
    		    XShortField("partner_key", 0x0001),
    		    XShortField("partner_portpri", 0x0000),
    		    XShortField("partner_port", 0x0001),
    		    XByteField("partner_state",0xBC),
    		    X3BytesField("reserved2",0x000000),
    		    XByteField("tlvtype3",0x03),
    		    XByteField("col_len",0x10),
    		    XShortField("col_maxdelay", 0x0005),
    		    StrField("reserved3","\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"),
    		    XByteField("tlvtype4",0x00),
    		    XByteField("terminator_len",0x00),
    		    StrField("reserved4","\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00") ]