from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *
from scapy.layers.inet import *


##Layers
##BFD Control packet
#
#BFD Control packet Constraint Part
# 0                   1                   2                   3
#     0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |Vers |  Diag   |Sta|P|F|C|A|D|M|  Detect Mult  |    Length     |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                       My Discriminator                        |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                      Your Discriminator                       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                    Desired Min TX Interval                    |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                   Required Min RX Interval                    |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |                 Required Min Echo RX Interval                 |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#BFD Control packet Optional Part
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#    |   Auth Type   |   Auth Len    |  Authentication Data...       |
#    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#
#BFD Control packet Constraint Part
#protocal version(3bit)
#diagnostic code(5bit)
#session state(2bit)
#message flags(6bit)
#detect time multiplier(1byte)
#message length(1byte)
#my discriminator(4byte)
#your discriminator(4byte)
#desired min tx interval(4byte)
#required min rx interval(4byte)
#required min echo interval(4byte)


#BFD Control packet Constraint Part
#authentication type(1byte)
#authentication length(1byte)
#authentication key id(1byte)


class BFDPart1(Packet):
    name = "BFD control packet Constraint Part"
    fields_desc = [ BitField("Vers",1,3),
                    BitField("Diag",0,5),
                    BitField("Sta",3,2),
                    BitField("Flags",8,6),
                    ByteField("DetectMult",0x05),
                    ByteField("Length",0x18),
                    IntField("MyDiscrim", 0x00000001),
                    IntField("YourDiscrim", 0x00000001),
                    IntField("MinTx", 0x00061A80),
                    IntField("MinRx", 0x00061A80),
                    IntField("MinEcho", 0x00061A80) ]

class BFDPart2(Packet):
    name = "BFD control packet Optional Part"
    fields_desc = [ ByteField("AuthType",0x01),
                    ByteField("AuthLent",0x13),
                    ByteField("AuthKeyId",0x01),
                    IntField("AuthData1", 0x31323334),
                    IntField("AuthData2", 0x35360000),
                    IntField("AuthData3", 0x00000000),
                    IntField("AuthData4", 0x00000000), ]

class BFDPart3(Packet):
    name = "BFD control packet add Part"
    fields_desc = [ ByteField("option",0x11)]