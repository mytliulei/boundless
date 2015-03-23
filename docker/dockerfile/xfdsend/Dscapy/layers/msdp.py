from scapy.packet import *
from scapy.fields import *
from scapy.layers.inet import *


class MSDP(Packet):
    name = "MSDP packet"
    fields_desc = [ XByteField("type",0x01),
                    XShortField("length", 0x0003),
                    ]


bind_layers( TCP,           MSDP,           dport=639)
