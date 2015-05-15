### 介绍

我们使用商用测试仪（比如ixia）模拟一些协议来测试设备，比如模拟host，测试arp，ping，dhcp等；同时我们也利用测试仪提供的api来编写脚本。
    
由于成本的原因，我们自己开发了测试仪软件，具备发包，抓包，统计等，但没有模拟net协议的功能。
    
这里，利用linux的macvlan和net namespace，尝试模拟host


#### macvlan

与传统的在单网卡上配置多个ip不同，macvlan设备有自己的mac地址，这样可以在一个网卡上虚拟多个mac-ip对。
    
    
#### net namespace

将创建的macvlan设备划到单独的netnamespace，这样我们就可以不影响宿主机器的net环境。
    
### 测试仪拓扑及验证方法

这是我们的测试仪拓扑，eth1为测试仪端口（实体环境下，为实际的物理网卡；虚拟环境下为veth），我们在eth1下建立macvlan设备eth1.mv1，并划到namespace test1下，配置地址10.1.1.10

```shell
ip netns add test1
ip link add eth1.mv1 link eth1 type macvlan
ip link set eth1.mv1 netns test1
ip netns exec test1 ip link set eth1.mv1 up
ip netns exec test1 ip addr add 10.1.1.10/24 dev eth1.mv1
```

### 验证静态地址 

  我们在虚拟环境下，验证该方法是否可以模拟host
    
    1. 建立一对veth，为veth1，veth2，并将veth2划到test的netns下
```shell
ip netns add test
ip link add veth1 type veth peer name veth2
ip link set veth2 netns test
ip link set veth1 up
ip netns exec test ip link set veth2 up
ip netns exec test ip addr add 10.1.1.1/24 dev veth2 
```
    2. 在veth1上建立mv1和mv2，并分别划到n1，n2的netns下，配置地址
```
ip netns add n1
ip netns add n2
ip link add veth1.mv1 link veth1 type macvlan
ip link add veth1.mv2 link veth1 type macvlan
ip link set veth1.mv1 netns n1
ip link set veth1.mv2 netns n2
ip netns exec n1 ip link set veth1.mv1 up
ip netns exec n2 ip link set veth1.mv2 up
ip netns exec n1 ip addr add 10.1.1.10/24 dev veth1.mv1
ip netns exec n2 ip addr add 10.1.1.11/24 dev veth1.mv2
```
    4. veth1 ping mv1 mv2
```shell
root@ip netns exec test ping 10.1.1.10 -c 5
PING 10.1.1.10 (10.1.1.10) 56(84) bytes of data.
64 bytes from 10.1.1.10: icmp_seq=1 ttl=64 time=0.069 ms
64 bytes from 10.1.1.10: icmp_seq=2 ttl=64 time=0.072 ms
64 bytes from 10.1.1.10: icmp_seq=3 ttl=64 time=0.056 ms
64 bytes from 10.1.1.10: icmp_seq=4 ttl=64 time=0.073 ms
64 bytes from 10.1.1.10: icmp_seq=5 ttl=64 time=0.069 ms

--- 10.1.1.10 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 3999ms
rtt min/avg/max/mdev = 0.056/0.067/0.073/0.012 ms

root@ip netns exec test ping 10.1.1.11 -c 5
PING 10.1.1.11 (10.1.1.11) 56(84) bytes of data.
64 bytes from 10.1.1.11: icmp_seq=1 ttl=64 time=0.069 ms
64 bytes from 10.1.1.11: icmp_seq=2 ttl=64 time=0.072 ms
64 bytes from 10.1.1.11: icmp_seq=3 ttl=64 time=0.056 ms
64 bytes from 10.1.1.11: icmp_seq=4 ttl=64 time=0.073 ms
64 bytes from 10.1.1.11: icmp_seq=5 ttl=64 time=0.069 ms

--- 10.1.1.11 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 3999ms
rtt min/avg/max/mdev = 0.056/0.067/0.073/0.012 ms
```
    5. 在veth2上show neigh
```shell
ip netns exec test  ip neigh show
10.1.1.11 dev veth2 lladdr 8e:28:8f:4a:c3:f9 REACHABLE
10.1.1.10 dev veth2 lladdr fe:8a:44:4a:d0:00 REACHABLE
```
    
  物理网卡下，验证方法同上
  
  ok,到这里，已经初步验证了 配置静态地址时macvlan可以模拟host
  
  接下里，我们来验证 macvlan 作为dhcp client 。。。
    
