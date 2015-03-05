**[Official Online HTML documentation](http://www.secdev.org/projects/scapy/doc/)**

# 简介
scapy是一个强大的交互式(interactive)的包操作程序，用python写的，有一个python的命令行解释器界面，可直接运行，当然也可以作为第三库，在我们的python程序中import进去使用它的类和方法。

# 下载安装

  scapy可以安装在linux，windows，下面以ubuntu为例
  
  * 在线安装
```shell
sudo apt-get update
sudo apt-get install python-dev python-pip
sudo pip install scapy
```
  * 下载安装
    1. 下载[最新版本](http://scapy.net/)
    2. 安装
  ```shell
  sudo unzip scapy.zip
  cd scapy
  sudo python setup.py install
  ```
    
  > **Note: 下载源码包安装时，可能会由于某些依赖包未安装而失败，建议采用在线安装**
  
# 加载scapy

    1. 启动python解释器
    2. 加载scapy包
```python
>>> from scapy.all import *
```

# 构造包
  
  * 报文模板

  scapy内置了大量的报文模板，在python解释器下，可以通过ls查看
```python
>>> ls()
ARP        : ARP
ASN1_Packet : None
BOOTP      : BOOTP
CookedLinux : cooked linux
DHCP       : DHCP options
DHCP6      : DHCPv6 Generic Message)
DHCP6OptAuth : DHCP6 Option - Authentication
DHCP6OptBCMCSDomains : DHCP6 Option - BCMCS Domain Name List
DHCP6OptBCMCSServers : DHCP6 Option - BCMCS Addresses List
DHCP6OptClientFQDN : DHCP6 Option - Client FQDN
DHCP6OptClientId : DHCP6 Client Identifier Option
DHCP6OptDNSDomains : DHCP6 Option - Domain Search List option
DHCP6OptDNSServers : DHCP6 Option - DNS Recursive Name Server
DHCP6OptElapsedTime : DHCP6 Elapsed Time Option
DHCP6OptGeoConf : 
DHCP6OptIAAddress : DHCP6 IA Address Option (IA_TA or IA_NA suboption)
DHCP6OptIAPrefix : DHCP6 Option - IA_PD Prefix option
DHCP6OptIA_NA : DHCP6 Identity Association for Non-temporary Addresses Option
DHCP6OptIA_PD : DHCP6 Option - Identity Association for Prefix Delegation
DHCP6OptIA_TA : DHCP6 Identity Association for Temporary Addresses Option
DHCP6OptIfaceId : DHCP6 Interface-Id Option
DHCP6OptInfoRefreshTime : DHCP6 Option - Information Refresh Time
...
```
从中可以看到，常用的Ether，Dot1Q，IP，TCP，UDP等报文模板

  可以通过ls(模板名称)，来查看某个报文模板的字段结构
```python
>>> ls(Ether)
dst        : DestMACField         = (None)
src        : SourceMACField       = (None)
type       : XShortEnumField      = (0)
```
  通过Ether报文模板，可以构造包含目的mac，源mac，类型字段的报文
  
  * 报文组装

  按照填充好的各类报文模板，可以组装成实际的报文，scapy通过`/`来组装
```python
>>> packet=Ether(dst="00:00:00:00:00:01",src="00:00:00:00:00:01")/IP(src="192.168.30.22",dst="192.168.30.254")/TCP()
```
  上述构造了一个tcp报文，可以通过show，show2来查看报文的各个字段内容
```python
>>> packet.show()
###[ Ethernet ]###
  dst       = 00:00:00:00:00:01
  src       = 00:00:00:00:00:01
  type      = 0x800
###[ IP ]###
     version   = 4
     ihl       = None
     tos       = 0x0
     len       = None
     id        = 1
     flags     = 
     frag      = 0
     ttl       = 64
     proto     = tcp
     chksum    = None
     src       = 192.168.30.22
     dst       = 192.168.30.254
     \options   \
###[ TCP ]###
        sport     = ftp_data
        dport     = http
        seq       = 0
        ack       = 0
        dataofs   = None
        reserved  = 0
        flags     = S
        window    = 8192
        chksum    = None
        urgptr    = 0
        options   = {}
>>> packet.show2()
###[ Ethernet ]###
  dst       = 00:00:00:00:00:01
  src       = 00:00:00:00:00:01
  type      = 0x800
###[ IP ]###
     version   = 4L
     ihl       = 5L
     tos       = 0x0
     len       = 40
     id        = 1
     flags     = 
     frag      = 0L
     ttl       = 64
     proto     = tcp
     chksum    = 0xbc6a
     src       = 192.168.30.22
     dst       = 192.168.30.254
     \options   \
###[ TCP ]###
        sport     = ftp_data
        dport     = http
        seq       = 0
        ack       = 0
        dataofs   = 5L
        reserved  = 0L
        flags     = S
        window    = 8192
        chksum    = 0xd119
        urgptr    = 0
        options   = {}
```

  另外可以通过hexdump，查看报文的16进制形式
```python
>>> hexdump(packet)
0000   00 00 00 00 00 01 00 00  00 00 00 01 08 00 45 00   ..............E.
0010   00 28 00 01 00 00 40 06  BC 6A C0 A8 1E 16 C0 A8   .(....@..j......
0020   1E FE 00 14 00 50 00 00  00 00 00 00 00 00 50 02   .....P........P.
0030   20 00 D1 19 00 00                                   .....
```

  * 报文payload

  可以通过Raw()来对报文的payload进行填充，通过这种方式来达到构造指定长度的报文
```python
>>> packet=Ether(dst="00:00:00:00:00:01",src="00:00:00:00:00:01")/IP(src="192.168.30.22",dst="192.168.30.254")/TCP()/Raw('abcdef')
```
  * 其他命令

  可以通过lsc()来查看scapy提供的命令
```python
>>> lsc()
arpcachepoison      : Poison target's cache with (your MAC,victim's IP) couple
arping              : Send ARP who-has requests to determine which hosts are up
bind_layers         : Bind 2 layers on some specific fields' values
corrupt_bits        : Flip a given percentage or number of bits from a string
corrupt_bytes       : Corrupt a given percentage or number of bytes from a string
defrag              : defrag(plist) -> ([not fragmented], [defragmented],
defragment          : defrag(plist) -> plist defragmented as much as possible 
dyndns_add          : Send a DNS add message to a nameserver for "name" to have a new "rdata"
dyndns_del          : Send a DNS delete message to a nameserver for "name"
etherleak           : Exploit Etherleak flaw
fragment            : Fragment a big IP datagram
fuzz                : Transform a layer into a fuzzy layer by replacing some default values by random objects
getmacbyip          : Return MAC address corresponding to a given IP address
hexdiff             : Show differences between 2 binary strings
hexdump             : --
hexedit             : --
is_promisc          : Try to guess if target is in Promisc mode. The target is provided by its ip.
linehexdump         : --
ls                  : List  available layers, or infos on a given layer
promiscping         : Send ARP who-has requests to determine which hosts are in promiscuous mode
rdpcap              : Read a pcap file and return a packet list
send                : Send packets at layer 3
sendp               : Send packets at layer 2
sendpfast           : Send packets at layer 2 using tcpreplay for performance
sniff               : Sniff packets
split_layers        : Split 2 layers previously bound
sr                  : Send and receive packets at layer 3
sr1                 : Send packets at layer 3 and return only the first answer
srbt                : send and receive using a bluetooth socket
srbt1               : send and receive 1 packet using a bluetooth socket
srflood             : Flood and receive packets at layer 3
srloop              : Send a packet at layer 3 in loop and print the answer each time
srp                 : Send and receive packets at layer 2
srp1                : Send and receive packets at layer 2 and return only the first answer
srpflood            : Flood and receive packets at layer 2
srploop             : Send a packet at layer 2 in loop and print the answer each time
traceroute          : Instant TCP traceroute
tshark              : Sniff packets and print them calling pkt.show(), a bit like text wireshark
wireshark           : Run wireshark on a list of packets
wrpcap              : Write a list of packets to a pcap file
```
