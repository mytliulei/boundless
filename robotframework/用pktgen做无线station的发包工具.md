# 简介

在[DCNRobot](https://github.com/mytliulei/DCNRobot)的项目中，测试仪有2种：

* ixia：商用测试仪，我们提供一系列的关键字来控制，一般用于性能测试及某些协议模拟
* 自研发包工具Dsend：实现了发包，抓包，统计的功能，缺点是不能发送大流量的报文，但一般功能测试已足够

**但**，无线测试的需求是：在Station上发送报文，如果用自研的发包工具，不方便的地方有：

* 发包工具是C/S结构：每次测试时启动，不灵活；
* 安装麻烦：需要安装一系列的依赖包，开始打算采用docker技术，但项目组说，充当Sta的机器有的不支持64位

因此，根据无线的需求，采用pktgen来充当发包工具，优点：

* 内核自带，无须安装
* robot通过ssh下发命令即可，无须启动服务器程序
* 虽然pktgen只支持mac，ip，udp，vlan，但sta目前对发包类型的需求比较简单，已足够支持

pktgen：pktgen是linux内核自带的发包工具，[中文文档](https://github.com/torvalds/linux/blob/master/Documentation/networking/pktgen.txt)，[发包的例子](https://github.com/torvalds/linux/tree/21bdb584af8cca7c6df3c44cba268be050a234eb/samples/pktgen)

# 使用说明

* [关键字lib源码](https://github.com/mytliulei/DCNRobot/blob/master/src/lib/Pktgen.py)
* [关键字Resource源码](https://github.com/mytliulei/DCNRobot/blob/master/src/resource/Sta.txt)

### 编辑报文

* 采用分层编辑报文，目前提供的关键字有：Build Ether; Build Dot1Q; Build Ip; Build Ipv6; 具体用法参见各关键字说明；
* 通过关键字Build Packet组装各层报文；
* 注意: 各层报文要按从从低到高顺序编辑；
* 注意:目前只支持单层tag；
* 支持mac，ip，ipv6的递增，但需要注意的是，递增的时候是各个指定项同时递增，与ixia的递增方式不同
* 举例:

> | Sta.Build Ether | dst=00:00:00:00:00:02 | src=00:00:00:00:00:01 |
>
> | Sta.Build Dot1q | vlan=${10} | prio=${7} |
>
> | Sta.Build Ip | dst=10.1.1.1 | src=20.1.1.2 |
>
> | Sta.Build Packet |

### 编辑的报文及发送属性设置到接口

* 通过关键字Set Stream Packet将编辑好的报文设置到端口
* 通过关键字Set Stream Control设置流的发送参数
* 注意: 发送速率有bps和pps两个参数，设置时只能设置1个参数，不能同时指定
* 注意: 参数count是发送的数目，设置为0时是持续发送，但因为目前不支持速率统计，在测试中这种方式很难做精确的检查

### 发包和停止

* 关键字: Start Transmit 和 Stop Transmit
* 注意：当执行Start Transmit的时候，上述设置的属性才会通过ssh下发给sta，每下发一个属性，检查一次结果，设置不正确时，会报错

### 抓包过滤

* 抓包关键字: Start Capture；
* 停止抓包关键字: Stop Capture；
* 获取抓包的数量: Get Capture Packet Num；
* 获取过滤报文的数量: Get Filter Capture Packet Num；
* 注意: 必须在抓包结束后，过滤报文的关键字才能使用；
* 按不同条件，可以对抓到的报文反复使用不同的过滤条件过滤; 具体使用方法见关键字说明

### 收发包统计

*由于无线对统计没有需求，因此暂时不做，如果要做的话，计划扫描/sys/class/net/iface/statistics/下的统计项来获取*

# pktgen使用注意事项：

* 各个属性的配置可以参见[中文文档的说明](https://github.com/torvalds/linux/blob/master/Documentation/networking/pktgen.txt)
* 使用中发现2.72的版本，没有rate，ratep的属性，只能用delay来代替
* *当count设置为0时，不能用echo stop > /proc/net/pktgen/pgctrl来停止，只能用kill的方式停止，不知为何:question:*
* 附录：[pktgen the linux packet generator](./doc_quote/pktgen_the_linux_packet_generator.pdf)

# tcpdump抓包的说明：

* 抓包的实现： 按照抓包动作的时间，在/tmp/下生产一个pcap文件，用tcpdump将抓到的报文暂存在sta上，命令为：
```shell
tcpdump -n -i iface -w /tmp/filename.pcap 
```
* 过滤报文： 用tcpdump读取第一步抓包的文件，通过过滤条件，获取报文的数量及内容,命令为：
```
tcpdump -n -r /tmp/filename.pcap express | wc -l
tcpdump -n -r /tmp/filename.pcap -XX filter_express
```
* 新内核的tcpdump版本支持区分tx/rx的报文，参数为-P in|out|inout，实现上做了自适应，通过tcpdump -h来区分
