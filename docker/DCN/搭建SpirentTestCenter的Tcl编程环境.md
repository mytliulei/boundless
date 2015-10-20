### 介绍

  我们编写脚本来测试网络设备，需要借助商用的测试仪，这样就需要安装测试仪的编程环境（tcl API），一般情况，我们安装测试仪客户端程序就可以了，但这些客户端程序都非常庞大，对于一个执行脚本的机器来说，并不是必须的，现在有两种方法来规避这个问题：

  - 提取与tcl编程有关的文件，在执行机器上只安装这些文件；
  - 构建一个tcl编程环境服务器，即代理服务器，由服务器来执行相关的指令；
  
  第二种方法的优势显然是明显的，执行机不必安装任何与测试仪有关的文件，只需使用时，连接代理服务器，向其发送指令即可。
  
  OK，下面我们就来介绍如何使用docker构建这个编程环境（不包含代理服务器程序）
  
#### 基础镜像
  
  由于docker目前不支持windows，我们使用Spirent发布的linux下的安装程序，同时由于其发布的x64的安装程序在使用tcl8.5时存在问题，我们需要安装i386的安装包，因此需要一个i386的基础镜像
  
  * 镜像：[ioft/i386-ubuntu:14.04.2](https://hub.docker.com/r/ioft/i386-ubuntu/)
  
    通过官方下载镜像
```shell
docker pull ioft/i386-ubuntu:14.04.2
```

#### 安装tcl解释器

  tcl解释器为8.5版本，下载地址:[tcl8.5.18-src.tar.gz](http://sourceforge.net/projects/tcl/files/Tcl/8.5.18/tcl8.5.18-src.tar.gz/download?use_mirror=nchc)
  
  请解压后按照README安装，这里不再叙述，**注意安装时要加linux32，否则会安装成x64版本**

#### 安装SpirentTestCenter客户端程序

  需要登录Spirent官方网站下载，我们以4.46版本为例：Spirent_TestCenter_Auto_Linux_4.46.tar.gz
  
  * 解压安装文件
  * 在tcl8.5的安装目录下建立构建编程包，即将解压的**Spirent_TestCenter_Application_Linux**目录下的所有文件拷贝到`/usr/local/lib/tcl8.5/stc2.0`目录下

#### 加载SpirentTestCenter包

  * 打开bash，输入tclsh8.5
  
  * 输入package require SpirentTestCenter,成功加载后会返回4.46的版本号

### 构建avalanche编程环境

。。。待续 
 
### 构建docker环境

  **注意：以下步骤操作需要root权限** 
   
#### 编写Dockerfile

  * [Dockerfile](../dockerfile/SpirentProxyServer/Dockerfile) 
  
  需要说明的是：
  
  1. 文件最后用的是ENTRYPOINT命令，目的就是不允许容器替换linux32命令，否则容器启动后会变为x64环境
  2. 替换了默认的apt source，改为163的源，这样更快
  3. RUN 后面的命令都要带linux32
  

### 附录: 一些资源

  1. [下载tcl各种包的网站](http://teapot.activestate.com/index)
