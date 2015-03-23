from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *
from scapy.layers.inet import *
from scapy.layers.inet6 import *


##Layers
#Hello Message Format
#
#   The PIM Hello message, as defined by PIM-SM [4], has the following
#   format:
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |PIM Ver| Type  |   Reserved    |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |          Option Type          |         Option Length         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                         Option Value                          |
#   |                              ...                              |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                               .                               |
#   |                               .                               |
#   |                               .                               |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |          Option Type          |         Option Length         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                         Option Value                          |
#   |                              ...                              |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#   PIM Ver, Type, Reserved, Checksum
#     Described above.
#
#   Option Type
#     The type of option given in the Option Value field.  Available
#     types are as follows:
#
#       0              Reserved
#       1              Hello Hold Time
#       2              LAN Prune Delay
#       3 - 16         Reserved
#       17             To be assigned by IANA
#       18             Deprecated and SHOULD NOT be used
#       19             DR Priority (PIM-SM Only)
#       20             Generation ID
#       21             State Refresh Capable
#       22             Bidir Capable
#       23 - 65000     To be assigned by IANA
#       65001 - 65535  Reserved for Private Use [9]
#
#     Unknown options SHOULD be ignored.

class Pim6v2Header(Packet):
    name = "Pim6v2 Header"
    fields_desc = [ BitField("ver",2,4),
                    BitField("type",9,4),
                    ByteField("reserved",0),
                    XShortField("chksum",None) ]
                    
    def post_build(self, p, pay):
        p += pay
        if self.chksum is None:
            ck = checksum(p)
            p = p[:2]+chr(ck>>8)+chr(ck&0xff)+p[4:]
        return p

class PimDm6HelloOpt1(Packet):
    name = "PimDm6 Hello Optiontype 1: Hello Hold Time"
    fields_desc = [ ShortField("type", 1),
                    ShortField("length", 2),
                    ShortField("holdtime", 105) ]


class PimDm6HelloOpt19(Packet):
    name = "PimDm6 Hello Optiontype 19: DR Priority (PIM-SM Only)"
    fields_desc = [ ShortField("type", 19),
                    ShortField("length", 4),
                    IntField("dr_priority",1)]


class PimDm6HelloOpt2(Packet):
    name = "PimDm6 Hello Optiontype 2: T,LAN Prune Delay ,Override Interval "
    fields_desc = [ ShortField("type", 2),
                    ShortField("length", 4),
                    BitField("T",0,1),
                    BitField("lan_prune_delay",1003,15),
                    ShortField("override_interval", 3000) ]


class PimDm6HelloOpt20(Packet):
    name = "PimDm6 Hello Optiontype 20: Generation ID"
    fields_desc = [ ShortField("type", 20),
                    ShortField("length", 4),
                    IntField("generation_id", 9823) ] 

class PimDm6HelloOpt21(Packet):
    name = "PimDm6 Hello Optiontype 21: State Refresh Capable"
    fields_desc = [ ShortField("type", 21),
                    ShortField("length", 4),
                    BitField("version",1,8),
                    BitField("lan_prune_delay",60,8),                    
                    ShortField("reserved", 0) ]                 
 
class PimDm6HelloOpt24(Packet):
    name = "PimDm6 Hello Optiontype 24: To be assigned by IANA"
    fields_desc = [ ShortField("type", 24),
                    ShortField("length",18),
                    ShortField("unknow1",512),                                      
                    ShortField("unknow2",8210) ] 
#stuff            
class PimDm6HelloStuff(Packet):
    name = "PimDm6 Hello stuff"
    fields_desc = [ ShortField("unknow1",0),
                    ShortField("unknow2",0),
                    ShortField("unknow3",0), 
                    ShortField("unknow4",0),
                    ShortField("unknow5",0),
                    ShortField("unknow6",0),                                     
                    ShortField("unknow7",2)]                     


##Layers
#
# State Refresh Message Format
#
#   PIM State Refresh Messages have the following format:
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |PIM Ver| Type  |   Reserved    |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |         Multicast Group Address (Encoded Group Format)        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |             Source Address (Encoded Unicast Format)           |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |           Originator Address (Encoded Unicast Format)         |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |R|                     Metric Preference                       |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                             Metric                            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |    Masklen    |    TTL        |P|N|O|Reserved |   Interval    |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
#   PIM Ver, Type, Reserved, Checksum
#     Described above.


class Pim6RefreshMessage(Packet):
    name = "Pim-Dmv6 Refresh Message"
    fields_desc = [ IntField("Additem1", 0x02000080),
                    IP6Field("group", "FF16::1"),
                    ShortField("Additem2", 0x0200),
                    IP6Field("source", "2039::9"),
                    ShortField("Additem3", 0x0200),
                    IP6Field("orig_address","FE80::0203:0FFF:FE01:0101"),
                    BitField("R",0,1),
                    BitField("metric_preference",120,31),
                    IntField("metric",2),
                    ByteField("masklen",128),
                    ByteField("TTL",63),
                    BitField("P",0,1),
                    BitField("N",1,1),
                    BitField("O",0,1),
                    BitField("reserved",0,5),
                    ByteField("interval",60)]


##Layers
#
## Assert Message Format
# 
#   PIM Assert Messages, as defined in PIM-SM [4], have the following
#   format:
#
#    0                   1                   2                   3
#    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |PIM Ver| Type  |   Reserved    |           Checksum            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |         Multicast Group Address (Encoded Group Format)        |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |             Source Address (Encoded Unicast Format)           |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |R|                     Metric Preference                       |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#   |                             Metric                            |
#   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+  


class Pim6AssertMessage(Packet):
    name = "Pim-Dm6 Assert Message"
    fields_desc = [ IntField("Additem1", 0x01000020),
                    IP6Field("group", "FF16::1"),
                    ShortField("Additem2", 0x0100),
                    IP6Field("source", "FF16::1"),
                    BitField("R",0,1),
                    BitField("metric_preference",120,31),
                    IntField("metric",2)]


bind_layers(IPv6,           Pim6v2Header,           nh=103) 