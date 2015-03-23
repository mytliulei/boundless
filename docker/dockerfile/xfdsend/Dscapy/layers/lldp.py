from scapy.packet import *
from scapy.fields import *
from scapy.layers.l2 import *



##Layers
class ChassisID(Packet):
    name = "LLDPChassisID"
    fields_desc = [ BitField("type",1,7),
                    BitField("length",None,9),
                    ByteField("subtype",4),
                    StrField("chassisid","012345") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay
    

class ChassisIDIncr(Packet):
    name = "LLDPChassisID"
    fields_desc = [ BitField("type",1,7),
                    BitField("length",None,9),
                    ByteField("subtype",4),
                    MACField("chassisid","00:00:00:01:01:01") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay


class PortID(Packet):
    name = "LLDPPortID"
    fields_desc = [ BitField("type",2,7),
                    BitField("length",None,9),
                    ByteField("subtype",7),
                    StrField("portid","1") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay
        

class TTL(Packet):
    name = "LLDPTTL"
    fields_desc = [ BitField("type",3,7),
                    BitField("length",2,9),
                    ShortField("ttl",120) ]



class PortDescription(Packet):
    name = "LLDPPortDescription"
    fields_desc = [ BitField("type",4,7),
                    BitField("length",None,9),
                    StrField("portdescription","abc") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay


class SystemName(Packet):
    name = "LLDPSystemName"
    fields_desc = [ BitField("type",5,7),
                    BitField("length",None,9),
                    StrField("systemname","abc") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay


class SystemDescription(Packet):
    name = "LLDPSystemDescription"
    fields_desc = [ BitField("type",6,7),
                    BitField("length",None,9),
                    StrField("systemdescription","abc") ]
    def post_build(self, p, pay):
        if self.length is None:
            l = len(p)-2
            lh = l/256
            ll = l - lh*256
            p = chr(((self.type&0x7f)<<1) | lh&0x1)+chr(ll&0xff)+p[2:]    
        return p+pay


class SystemCapabilities(Packet):
    name = "LLDPSystemCapabilities"
    fields_desc = [ BitField("type",7,7),
                    BitField("length",4,9),
                    ShortField("systemcapabilities",2),
                    ShortField("enablecapabilities",1) ]

class MEDCapabilities(Packet):
    name = "MEDCapabilities"
    fields_desc = [ BitField("type",127,7),
                    BitField("length",7,9),
                    X3BytesField("OUI",0x0012bb),
                    ByteField("subtype",1),
                    ShortField("capabilities",0),
                    ByteField("devicetype",4)]
    
class MEDCapabilities(Packet):
    name = "MEDCapabilities"
    fields_desc = [ BitField("type",127,7),
                    BitField("length",7,9),
                    X3BytesField("OUI",0x0012bb),
                    ByteField("subtype",1),
                    ShortField("capabilities",0),
                    ByteField("devicetype",4)]



class EndTlv(Packet):
    name = "LLDPEndTlv"
    fields_desc = [ BitField("type",0,7),
                    BitField("length",0,9) ]



