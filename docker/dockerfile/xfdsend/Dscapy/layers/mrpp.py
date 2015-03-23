from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *



#0         1          2          3          4        4
#12345678 90123456 78901234 56789012 34567890 12345678
#        +--------+--------+--------+--------+--------+--------+
#        |         Destination MAC Address (6 bytes)           |
#        +--------+--------+--------+--------+--------+--------+
#        |         Source MAC Address (6 bytes)                |
#        +--------+--------+--------+--------+--------+--------+
#        |    EtherType    |PRI | VLAN ID    |  Frame Length   |
#        +--------+--------+--------+--------+--------+--------+
#        |    DSAP/SSAP    | CONTROL|     OUI = 0x00E02B       |
#        +--------+--------+--------+--------+--------+--------+
#        |     0x00bb      |  0x99  |  0x0b  |  MRPP_LENGTH    |
#        +--------+--------+--------+--------+--------+--------+
#        |MRPP_VER|MRPPTYPE|  CTRL_VLAN_ID   |    0x0000       |
#        +--------+--------+--------+--------+--------+--------+
#        |  0x0000         |    SYSTEM_MAC_ADDR (6 bytes)      |
#        +--------+--------+--------+--------+--------+--------+
#        |                 |   HELLO_TIMER   |    FAIL_TIMER   |
#        +--------+--------+--------+--------+--------+--------+
#        | STATE  | 0x00   |   HELLO_SEQ     |     0x0000      |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#        |                 RESERVED (0x000000000000)           |
#        +--------+--------+--------+--------+--------+--------+
#
#      Where:
#
#          Destination MAC Address is always vendorBaseMac+2.
#          PRI contains 3 bits of priority, with 1 other bit reserved.
#          EtherType is always 0x8100.
#          DSAP/SSAP is always 0xAAAA.
#          CONTROL is always 0x03.
#          MRPP_LENGTH is 0x40.
#          MRPP_VERS is 0x0001.
#          CTRL_VLAN_ID is the VLAN ID for the Control VLAN in use.
#          SYSTEM_MAC_ADDR is the System MAC Address of the sending node.
#          HELLO_TIMER is the value set by the Master Node.
#          FAIL_TIMER is the value set by the Master Node.
#          HELLO_SEQ is the sequence number of the Hello Frame.
#
#      MRPP Type (MRPPTYPE) values:
#          HEALTH              = 1
#          RING-UP-FLUSH-FDB   = 2
#          RING-DOWN-FLUSH-FDB = 3
#          LINK-DOWN           = 4
#          All other values are reserved.
#
#      STATE values:
#          IDLE           = 0
#          COMPLETE       = 1
#          FAILED         = 2
#          LINKS-UP       = 3
#          LINK-DOWN      = 4
#          PRE-FORWARDING = 5
#          All other values are reserved.

##Layers
class Mrpp(Packet):
    name = "mrpp packet,from DSAP/SSAP to end"
    fields_desc = [ XShortField("dsap", 0xAAAA),
    		    XByteField("control",0x03),
    		    X3BytesField("OUI",0x00E02B),
    		    XShortField("resv1", 0x00BB),
    		    XShortField("resv2", 0x990B),
    		    XShortField("mrpplen", 0x0040),
                    XByteField("mrppver",0x01),
                    XByteField("mrpptype",0x01),
                    XShortField("ctrlvlanid", 0x0FFE),
                    XShortField("resv3",0x0000),
                    XShortField("resv4",0x0000),
                    MACField("sysmacaddr", "00:00:00:00:00:01"),
                    XShortField("hellotimer", 0x0001),
                    XShortField("failtimer", 0x0003),
                    XByteField("state",0x00),
                    XByteField("resv5",0x00),
                    XShortField("helloseq", 0xD29A),
                    XShortField("resv6", 0x0000), 
                    X3BytesField("reserved1",0x000000),
                    X3BytesField("reserved2",0x000000),
                    X3BytesField("reserved3",0x000000),
                    X3BytesField("reserved4",0x000000),
                    X3BytesField("reserved5",0x000000),
                    X3BytesField("reserved6",0x000000),
                    X3BytesField("reserved7",0x000000),
                    X3BytesField("reserved8",0x000000),
                    X3BytesField("reserved9",0x000000),
                    X3BytesField("reserved10",0x000000),
                    X3BytesField("reserved11",0x000000),
                    X3BytesField("reserved12",0x000000) ]