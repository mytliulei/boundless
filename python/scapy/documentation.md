
**[Official Scapy Project](http://www.secdev.org/projects/scapy/)**

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
  
  scapy的包创建是按照我们的TCP/IP的四层参考模型来的，链路层，网络层，传输层，应用层
  
  Scapy为各个层都写了类，我们要做的就是把这些类实例化，对packet的一些操作就是调用这里类的方法或者改变类的参数取值，各个层都有各自的创建函数，比如IP（），TCP（），UDP()等等，不同层之间通过“/”来连接。
  
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
  
  参数一般都有默认值，如果我们建立一个类的实例，如IP（），没有传给它参数，那么它的参数就是默认的
  
  > Note: 一般checksum，type等字段默认值为None，使用中不需要赋值，报文组装完毕后会自动计算这些字段
  
  * 报文组装

  按照填充好的各类报文模板，可以组装成实际的报文，scapy通过`/`来组装
```python
>>> p1=Ether(dst="00:00:00:00:00:01",src="00:00:00:00:00:01")/IP(src="192.168.30.22",dst="192.168.30.254")/TCP()
```
  上述构造了一个tcp报文，可以通过ls, show，show2来查看报文的各个字段内容
```python
>>> ls(p1)
dst        : DestMACField         = '00:00:00:00:00:01' (None)
src        : SourceMACField       = '00:00:00:00:00:01' (None)
type       : XShortEnumField      = 2048            (0)
--
version    : BitField             = 4               (4)
ihl        : BitField             = None            (None)
tos        : XByteField           = 0               (0)
len        : ShortField           = None            (None)
id         : ShortField           = 1               (1)
flags      : FlagsField           = 0               (0)
frag       : BitField             = 0               (0)
ttl        : ByteField            = 64              (64)
proto      : ByteEnumField        = 6               (0)
chksum     : XShortField          = None            (None)
src        : Emph                 = '192.168.30.22' (None)
dst        : Emph                 = '192.168.30.254' ('127.0.0.1')
options    : PacketListField      = []              ([])
--
sport      : ShortEnumField       = 20              (20)
dport      : ShortEnumField       = 80              (80)
seq        : IntField             = 0               (0)
ack        : IntField             = 0               (0)
dataofs    : BitField             = None            (None)
reserved   : BitField             = 0               (0)
flags      : FlagsField           = 2               (2)
window     : ShortField           = 8192            (8192)
chksum     : XShortField          = None            (None)
urgptr     : ShortField           = 0               (0)
options    : TCPOptionsField      = {}              ({})
>>> p1.show()
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
>>> p1.show2()
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
>>> packet=Ether(dst="00:00:00:00:00:02",src="00:00:00:00:00:01")/IP(src="192.168.30.22",dst="192.168.30.254")/TCP()/Raw('abcdef')
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
# 发包

  * send 与 sendp
  
  send()是在第三层发送数据包，sendp（）是在第二层，下面是sendp的定义：
```python
def sendp(x, inter=0, loop=0, iface=None, iface_hint=None, count=None, verbose=None, realtime=None, *args, **kargs):
    """Send packets at layer 2
    sendp(packets, [inter=0], [loop=0], [verbose=conf.verb]) -> None
    """
```
  > 参数：
  > - x： 编辑好的报文
  > - iface： 发送的接口
  > - inter： 发送间隔，单位是秒,默认是0
  > - loop： 是否循环发送，默认否
  > - count： 发送数目
    
  其他参数请详见源码
  
  **发送多个不同的报文时，可将这些报文汇集成list，然后发送**
```python
>>> pl=Ether(dst="00:00:00:00:01:01",src="00:00:00:00:00:01")/IP(src="192.168.30.21",dst="192.168.30.254")
>>> p2=Ether(dst="00:00:00:00:01:01",src="00:00:00:00:00:02")/IP(src="192.168.30.22",dst="192.168.30.254")
>>> p3=Ether(dst="00:00:00:00:01:01",src="00:00:00:00:00:03")/IP(src="192.168.30.23",dst="192.168.30.254")
>>> p=[p1,p2,p3]
>>> sendp(p,iface='eth0')
```
  
  * send and receive packets
  
  **交换机测试，这部分可以不看**  

  The send and receive functions family will not only send stimuli and sniff responses but also match sent stimuli with received responses. 

  Function sr(),sr1(),and srloop() all work at layer 3.
  
  sr() is for sending and receiving packets,it returns a couple of packet and answers,and the unanswered packets.
  
  sr1() only receive the first answer.
  
  srloop() is for sending a packet in loop and print the answer each time
  
  Function srp(),srp1(),and srploop() all work at layer 2.
  
  
# 抓包
  
  * sniff
```python
def sniff(count=0, store=1, offline=None, prn = None, lfilter=None, L2socket=None, timeout=None,
          opened_socket=None, stop_filter=None, *arg, **karg):
    """Sniff packets
    sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args) -> list of packets

    count: number of packets to capture. 0 means infinity
    store: wether to store sniffed packets or discard them
    prn: function to apply to each packet. If something is returned,
         it is displayed. Ex:
         ex: prn = lambda x: x.summary()
    lfilter: python function applied to each packet to determine
         if further action may be done
         ex: lfilter = lambda x: x.haslayer(Padding)
    offline: pcap file to read packets from, instead of sniffing them
    timeout: stop sniffing after a given time (default: None)
    L2socket: use the provided L2socket
    opened_socket: provide an object ready to use .recv() on
    stop_filter: python function applied to each packet to determine
             if we have to stop the capture after this packet
             ex: stop_filter = lambda x: x.haslayer(TCP)
    """
```
  > 参数：
  > - iface: 抓包接口
  > - timeout: 抓包时间，默认是None，单位秒
  > - filter: 抓包过滤表达式，格式与tcpdump相同
  
  > 返回值：抓到的报文的list，报文可使用show,show2,hexdump,ls等命令查看
  
  其他参数用法请查阅源码
  
# 统计

  scapy并未提供统计命令或接口,统计方法归纳如下，如有其他方法请发送pull request，或联系mytliulei@gmail.com
  
  * 查看/sys/class/net/设备/statistics/ 下的统计项 
  
