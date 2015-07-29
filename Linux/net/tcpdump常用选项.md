# 简介
  tcpdump是常用的命令行抓包工具，另外一个常用的GUI抓包工具是wireshark，下面主要介绍一下常用的选项
  
# 选项
  
  * 指定接口抓包：
  
  -i interface
  
>  -i  监听的接口. 如果没有指定，tcpdump会使用系统内的up的编号（可通过tcpdump -D查看）最低的接口（除去loopback），比如eth0 

  * 指定抓包个数
  
  -c count
  
> -c 抓包数量. 在收到指定count的报文数量后exit
  
  * 将抓到的包保存到文件
  
  -w file
  
> -w 文件名. 将报文写到指定的文件内，此时不再进行解析和打印到stdout. 当file指定为"-"时，意思是stdout
>
> 需要注意的是：当tcpdump写文件或者输出到pipe时，output会buffered，因此后续的处理程序可能不能立刻读取到抓到的报文，此时，可以使用-U选项来立即更新
>
> tcpdump写文件和读文件时，不会通过文件的扩展名来判断格式，同时写文件时也不会自行加上扩展名；但在一些系统上会依据扩展名来区分报文保存的格式，因此最好保存文件时加上扩展名，比如.pcap

  * 从文件里读取报文
  
  -r file
  
> -r 文件名. 从指定的文件内读取报文，当file指定为"-"时，意思是input

  * 将抓到的报文以HEX和ASCII的方式打印
  
  -XX -X
  
> -XX 大写的2个X，用HEX和ASCII的格式，打印抓到的报文全部内容，**包含link层**
>
> -X  大写的1个X，用HEX和ASCII的格式，打印抓到的报文全部内容，**不包含link层**
  
  * 抓到的报文内容不解析为name
  
  -n

> 对地址不进行域名解析，可以避免DNS反向解析

  * 指定报文的收发方向
  
  -P in|out|inout

> -P in|out|inout 指定接口抓包的方向，不是所有的系统都支持

# 报文过滤表达式

**注意：这篇文档取自tcpdump的指南。原始的版本 www.tcpdump.org 找到**

  过滤器是一个ASCII字符串，它包含了一个过滤表达式。这个表达式会选择那些数据包将会被选中。如果表达式没有给出，那么，网络上所有的包都会被内核过滤引擎所认可。不然，只有那些表达式为'true'的包才会被认可。

##### 这个表达式包含了一个或多个原语。原语通常包含了id(名字或序列)，这些id优先于限定词。以下是三种不同的限定词：

* 输入(type)

  指明了哪些东西是id所代表的。可能的输入是host，net和port。比如：host foo，net 128.3，port 20。如果没有输入限定词，就假定是host
  
* 方向(dir)

  由id指明了一个特定的传输方向。可能的方向是src，dst，src or dst。比如，src foo，dst net 128.3，src or dst port ftp-data。如果没有指定，就假定是src or dst。如果没有链路层(比如，像slip这样的点对点协议)，那么限定词可以使用inbound和outbound，来指明一个方向。
  
* 协议(proto)

  限定词限制了所匹配的协议。可能的协议有：ether，fddi，tr，ip，ip6，arp，rarp，decnet，tcp和udp。比如：ether src foo，arp net 128.3，tcp port 21。如果没有指定协议限定词，那么就假定所有的协议都会被允许。例如：src foo等价于(ip or arp or rarp)src foo(当然，不能有不符合语法的字母出现)，net bar等价于(ip or arp or rarp) net bar，port 53等价于(tcp or udp) port 53。
  
'fddi'通常是'ether'的别名；解析器会认为它们是在特定网络接口上的数据链路层。FDDI的首部包含了和以太网很相似的源地址和目的地址，并且通常也包含了和以太网很相似的数据包类型。所以，在FDDI网域上使用过滤器和在以太网上使用过滤器基本一致。FDDI的首部还包括了其他的数据，不过你不能在过滤器表达式内表示他们。

同样的，'tr'也是'ether'的一个别名，它是较早被应用于FDDI的首部，也应用在令牌环网络首部。

除了以上内容，还有一些特殊的限定词和上面的形式不太一样，它们是：gateway，broadcast，less，greater和一些算术表达式。这些内容会在下面介绍。

##### 我们可以使用and，or和not将原语连接起来，来构造一个更复杂的过滤表达式。例如：host foo and not port ftp and not port ftp-data'。如果要简化输入，我们可以把已列出的id限定词省略。比如：tcp dst port ftp or ftp-data or domain' 和 `tcp dst port ftp or tcp dst port ftp-data or tcp dst port domain'是完全等价的。

##### 可使用的原语有：

* dst host host

当IPv4/v6数据包的目标域(destination field)为host时为true，host既可以是地址，也可以是名字。

* src host host

当IPv4/v6数据包的源域(source field)为host时为true。

* host host
当IPv4/v6数据包的源域(source field)或目标域(destination field)为host时为true。以上任何一个host表达式可以是ip，arp，rarp或ip6开头，如下所示：

> ip host host

等价于：

> ether proto ip and host host

如果host是一个多IP地址，那么每一个地址都会被匹配。

* ether dst ehost

当以太网的目的地址为ehost时为true。ehost可以是一个来自/etc/ether的名字，也可以是一个数字代号(参见 ethers(3N)for numeric format)。

* ether src ehost

当以太网的源地址为ehost时为true。

* ether host ehost

当以太网的目的地址，或源地址为ehost时为true。

* gateway host

当host为网关时为true。即，以太网源地址或目的地址是host,但源地址和目的地址不同时为host。host必须能被机器的主机-IP地址(host-name-to-IP-address)机制找到(如主机名文件，DNS，NIS等)，也能被主机-以太网地址(host-name-to-Ethernet-address)机制找到(如/etc/ethers等)。例如：

> ether host ehost and not host host

host / ehost均可使用名字或数字。这个语法目前在IPv6下不能工作。

* dst net net

当IPv4/v6数据包的目的地址的网络号包含了net时为true。net可以是一个来自/etc/networks的名字，也可以是一个网络号(更多内容请参见 networks(4))。

* src net net

当IPv4/v6数据包的源地址的网络号包含了net时为true。

* net net

当IPv4/v6数据包的目的地址，或源地址的网络号包含了net时为true

* net net mask netmask

当IP地址是 net ，子网掩码匹配 netmask 时为true。 可能需要 src 或 dst加以限制。 注意，这个语法不能应用于IPv6。

* net net/len

当IP地址是 net ，子网掩码连续1的个数为 len 时为true。 可能需要 src 或 dst加以限制。

* dst port port

当数据包是ip/tcp, ip/udp, ip6/tcp 或 ip6/udp，并且目的端口号是port时为true。port可以是数字，或是在/etc/services中被使用的名字。(参见 tcp(4P) and udp(4P))。如果使用名字，那么端口号和协议都将被检测。如果使用数字，或者一个不明确的名字，那么只有端口号会被检测。（比如：dst port 513将打印tcp/login数据流和udp/who数据流。port domain将打印tcp/domain的数据流和udp/domain的数据流）。

* src port port

当源端口号是 port时为true。

* port port

当源端口号或目的端口号为 port 时为true。以上任何一个port表达式可以以关键字tcp或udp开头，如下所示：

* tcp src port port

只匹配源端口是 port 的tcp数据包。

* less length

当数据包的长度小于等于length时为true。即：len <= length.

* greater length

当数据包的长度大于等于length时为true。即：len >= length.

* ip proto protocol

当数据包是IP数据包，并且它的协议类型为protocol时为true。protocol可以是一个数字，也可以是icmp, icmp6，igmp，igrp，pim，ah，esp，vrrp，udp 或 tcp中的一个。注意，tcp，udp， icmp是关键字，所以，它们要使用反斜杠()来转义，就好比C-shell中的\。注意，这个原语不会去追踪协议首部链。

* ip6 proto protocol

当数据包是IPv6数据包，并且它的协议类型为protocol时为true。注意，这个原语不会去追踪协议首部链。

* ip6 protochain protocol

当数据包是IPv6数据包，并且，在它的协议首部链中，包含了protocol类型的协议首部时，为true。 例如：

* ip6 protochain 6

能匹配所有的，拥有TCP协议首部的IPv6的数据包。在IPv6首部和TCP首部之间，可能包含认证首部，路由首部和跳数选项首部。由这个原语所生成的BPF(BSD Packet Filter，包过滤机制)码是复杂的，而且不能被BPF优化器优化，所以，在某些程度上，它的速度比较慢。

* ip protochain protocol

功能和 ip6 protochain protocol相同，只是这个应用于 IPv4。

* ether broadcast

当数据包是以太网广播数据包时为true。关键字ether是可选的。

* ip broadcast

当数据包是IP广播数据包时为true。它会检查所有的广播，包括地址全是0的和地址全是1的，然后，检查子网掩码。

* ether multicast

当数据包是以太网多播数据包时为true。关键字ether是可选的。 下面是一个常用短语`ether[0] & 1 != 0'

* ip multicast

当数据包是IP多播数据包时为true。

* ip6 multicast

当数据包是IPv6多播数据包时为true。

* ether proto protocol

当数据包是以太类型的protocol时为true。protocol可以是一个数字，也可以是ip, ip6, arp, rarp, atalk, aarp,decnet, sca, lat, mopdl, moprc,iso, stp, ipx, netbeui中的一个。注意，这些符号也都是关键字，所以，他们都需要用反斜杠()转义。
[在使用FDDI(比如'fddi protocol arp')和令牌环(比如'tr protocol arp')和其他大多数这种协议时，协议根据802.2逻辑链路控制(LLC)来识别，这些信息通常在FDDI或令牌环首部的开始。
当需要识别大多数协议的标识，比如FDDI或令牌环时, Tcpdump只检查LLC报头的ID数据域，它们以SNAP格式存储，并且，组织单位识别码(Organizational Unit Identifier(OUI))为0x000000，以封装以太网。它不会检查这个包是不是SNAP格式的，并在0x000000单元有OUI。
然而，iso是个特例，它会检查LLC首部的目的服务存取点DSAP(Destination Service Access Point)和源服务存取点SSAP(Source Service Access Point)，stp和netbeui会检查LLC首部的DSAP，atalk会检查数据包是不是SNAP格式的，并且OUI是不是0x080007。Appletalk 同样如此。

在以太网的例子中，tcpdump检查大部分协议的以太网类型字段，iso，sap 和 netbeui除外，因为它们会检查802.3帧，然后检查LLC首部，就像它对FDDI和令牌环那样。atalk，它检查以太网帧的Appletalk etype和SNAP格式的以太网帧，arrp，它在以太网帧中检查Appletalk ARP etype，或是在OUI为0x000000的802.2 SNAP帧中查找，还有ipx，他会在以太网帧中检查IPX etype，在LLC首部检查IPX DSAP，没有用802.3封装的LLC首部的IPX，和SNAP帧中的IPX etype。]

*  decnet src host

当DECNET的源地址为host时为true，它可能是一个格式为'10.123'的地址，也可能是一个DECNET主机名。[DECNET主机名称只有在配置成可运行DECNET的Ultrix系统中才得到支持。]

* decnet dst host

当DECNET的目的地址为host时为true。

* decnet host host

当DECNET的源地址或目的地址为host时为true。
ip, ip6, arp, rarp, atalk, aarp, decnet, iso, stp, ipx, netbeui
缩写是：

> ether proto p

p 是以上协议中的一个。 注意： tcpdump 目前并不知道，如何解析出这些协议。

* vlan [vlan_id]

当数据包是IEEE 802.1Q VLAN数据包时为true。若[vlan_id]被指定，则仅当数据包为指定的vlan_id，值才为true。注意，在假设数据包为VLAN数据包的前提下，表达式中的第一个关键字vlan会改变剩余表达式的解码偏移量。

* tcp, udp, icmp

缩写是：

> ip proto p or ip6 proto p

p 是以上协议中的一个。

 * iso proto protocol

当数据包的协议类型为protocol的OSI数据包时值为true。Protocol可以是一个数字或以下名称中的一个：clnp，esis或isis。
clnp, esis, isis

缩写是：
> iso proto p

p 是以上协议中的一个。注意，tcpdump并不能完成这些协议的全部解析工作。

* expr relop expr

若关系式如下：relop是 >, <, >=, <=, =, != 中的一个，并且expr是一个由正整常数（用标准C语言的语法表示），标准二进制运算符[ +, -, *, /, &, | ]，运算符的长度，和指定数据包存取，则值为true。要存取数据包内的数据，可以使用以下的语法：

* proto [ expr : size ]

Proto 是 ether, fddi, tr, ip, arp, rarp, tcp, udp, icmp or ip6中的一个，它为索引操作指明了协议层。注意，tcp,udp和其他较高层的协议类型只能应用于IPv4，而不能用于IPv6(这个问题可能在将来能得到解决)。被指定的协议层的字节偏移量由expr给出。Size是可选的，它指明了数据域中，我们所感兴趣的字节数。它可以是1，2，或4，默认为1。运算符的长度，由关键字len给出，指明了数据包的长度。
例如，ether[0] & 1 != 0'会捕捉所有的多播数据流。表达式ip[0] & 0xf != 5'能捕捉所有带可选域的IP数据包。表达式`ip[6:2] & 0x1fff = 0'仅捕捉未分段的数据报和段偏移量是0的数据报。这个检查隐含在tcp和udp的下标操作中。例如，tcp[0]通常指第一个字节的TCP首部，而不是指第一个字节的分段。

有些偏移量和域值可以以名字来表示，而不是数值。以下协议首部域的偏移量是正确的：icmptype (ICMP 类型域), icmpcode (ICMP 代码域), and tcpflags (TCP 标志域)。

ICMP 类型域有以下这些： icmp-echoreply, icmp-unreach, icmp-sourcequench, icmp-redirect, icmp-echo, icmp-routeradvert, icmp-routersolicit, icmp-timxceed, icmp-paramprob, icmp-tstamp, icmp-tstampreply, icmp-ireq, icmp-ireqreply, icmp-maskreq, icmp-maskreply.

TCP 标志域有以下这些： tcp-fin, tcp-syn, tcp-rst, tcp-push, tcp-push, tcp-ack, tcp-urg.

##### 原语可以用以下内容组合：

用圆括号括起来的原语和操作符 (圆括号在Shell中是特殊符号，所以必须要转义)。

* 取反操作 (!' 或 not').

* 连接操作 (&&' 或 and').

* 选择操作 (||' 或 or').

取反操作的优先级最高。 连接操作和选择操作有相同的优先级，并且它们的结合方向为从左向右。 注意：做连接的时候是需要显示的 and 操作符的，而不是把要连接的东西写在一起。

如果给出一个标识符，却没有关键字，那么就会假定用最近使用的关键字。 例如：

not host vs and ace

等价于

not host vs and host ace

不能和下面的混淆

not ( host vs or ace )

表达式参数即可以作为单个参数，也可以作为多个参数传递给tcpdump，后者更加方便一些。一般的，如果表达式包含一个Shell的元字符，那么用一个参数传递比较容易，最好把它括起来，多个参数在传递前，用空格连接起来。
