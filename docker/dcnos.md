### 介绍

  dcnos是DCN的网络操作系统，目前开发了x86模拟器，从而可以脱离物理交换机来运行平台的代码
   
  这里提供一种方法来将x86模拟器的运行环境打包的docker中，x86模拟器的配置文件及nosimg存放在host本机上，使用volumes加载到容器中（即保存不同环境中的配置文件和共享nosimg），这样就实现了运行环境与数据的分离，避免频繁build docker images
 
  * [Dockerfile](./dockerfile/dcnos/Dockerfile) 
  
  * [Docker img](https://registry.hub.docker.com/u/mytliulei/dcnos_env/)

### 使用方法

#### 安装docker
  
  这里提供[windows](https://docs.docker.com/installation/windows/)和[ubuntu](https://docs.docker.com/installation/ubuntulinux/)上安装的步骤,其他请参考https://docs.docker.com/
  
  **建议使用ubuntu**
  
##### 下载docker image

  * docker hub下载

```shell
docker pull mytliulei/dcnos_env:latest
```

  * 从内网ftp下载

ftp://10.1.145.36/docker/img/dcnos_env.tar

  下载后load
  
```shell
docker load -i dcnos_env.tart
```

##### 准备x86模拟器

  将x86模拟器的nos目录(不包括里面的img目录)拷贝到host本机内，如/home/test/下；将x86模拟器的nos目录下的img目录拷贝到host本机内，如/home/test/下
  
```shell
ll /home/test/nos/
总用量 32
drwxr-xr-x 3 root root 4096  3月 23 15:21 ./
drwxr-xr-x 3 root root 4096  3月 23 13:26 ../
-rw-r--r-- 1 root root   54  3月 23 15:06 devconfig
drwxr-xr-x 2 root root 4096  3月 23 13:45 img/
-rwxr-xr-x 1 root root 1372  3月 23 13:32 start.sh*
-rwxr-xr-x 1 root root  467  3月 23 13:32 stop.sh*

ll /home/test/img/
总用量 87396
drwxr-xr-x 2 root root     4096  3月 23 13:53 ./
drwxr-xr-x 3 root root     4096  3月 23 13:27 ../
-rwxr-xr-x 1 root root    17233  3月 23 13:30 dcn_console*
-rwxr-xr-x 1 root root 89463353  3月 23 13:28 nosimg*
```
  
  x86模拟器下载： ftp://10.1.145.36/docker/dcnos.rar
  
  将start.sh,stop.sh,dcn_console，nosimg变为可执行文件
  
```shell
chmod +x /home/test/nos/*.sh
chmod +x /home/test/nos/img/*
```

##### 添加端口到容器
```shell
pid=`docker inspect -f '{{.State.Pid}}' s1`
ln -s /proc/$pid/ns/net /var/run/netns/$pid
ip link set s1p1 netns $pid
ip netns exec $pid sysctl -w net.ipv6.conf.s1p1.disable_ipv6=1
ip netns exec $pid ip link set s1p1 up
```

  Note: s1p1的对端是tp1,设置方法见[发包工具](./发包工具.md)

  这样将添加了s1p1到容器中
  
##### 修改devconfig
  打开host本机的devconfig文件，位置在本机的nos目录下，里面是模拟器与端口的对用关系，devconfig文件中请去掉hostip这一行，添加port1 s1p1
  
```shell
cat devconfig
devtype 302
mac 00:03:0f:01:27:72
port1 tp1
```

  注意：如果启动多个容器来模拟多个设备时，要修改mac地址
  
##### 启动容器

```shell
docker run -d --name s1 -P -v /home/test/nos/:/home/nos/ -v /home/test/img/:/home/nos/img/ -privileged mytliulei/dcnos_env:latest
docker exec s1 /etc/init.d/xinetd start
```


##### 启动x86模拟器

  * 获取本机telnet到容器的端口号
```shell
 docker port s1
 23/tcp -> 0.0.0.0:49186
 ```
  * telnet到容器
  
  * 进入/home/nos/目录，执行./start.sh
```shell
cd /home/nos
./start.sh
```
