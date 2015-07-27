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

# 
