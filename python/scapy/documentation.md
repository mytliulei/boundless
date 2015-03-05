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
