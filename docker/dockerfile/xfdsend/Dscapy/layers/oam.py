import struct
from scapy.packet import *
from scapy.layers.l2 import *
from scapy.fields import *

class OAM(Packet):
    name = "OAM packet"
    fields_desc = [ XByteField("subtype",0x03),
                    XShortField("pduflag", 0x0050),
                    XByteField("pducode",0x00),
                    XByteField("informationtype",0x01),
                    XByteField("informationlength",0x10),
                    XByteField("version",0x01),
                    BitField("revision",0,4),
                    BitField("state",0,8),
                    BitField("parseraction",0,8),
                    BitField("multiplexer", 0,4),
                    XByteField("configuration",0x09),
                    XShortField("pduconfiguration", 0x05EE),
                    X3BytesField("OUI",0x00030F),
                    BitField("venderinformation",193,32),
                    XByteField("remotetype",0x02),
                    XByteField("remotelength",0x10),
                    XByteField("remoteversion",0x01),
                    BitField("remoterevision",0,4),
                    BitField("remotestate",0,8),
                    BitField("remotepaser",0,8),
                    BitField("remotemultiplexer",0,4),
                    XByteField("remoteconfiguration",0x09),
                    XShortField("remotepduconfig",0x05EE),
                    X3BytesField("remoteoui",0x00030F),
                    IntField("remotevendor",193)
                     ]




#bind_layers( Ether,         OAM,        type=0x8809)
