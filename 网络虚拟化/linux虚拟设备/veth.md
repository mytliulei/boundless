# veth

  veth interfaces are virtual ethernet interfaces that always exist in pairs. Whatever enters on one interface, exits from the other one, and viceversa. A simple test to check:
  
```shell
ip link add type veth
ip link show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 52:54:00:5a:d2:86 brd ff:ff:ff:ff:ff:ff
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
    link/ether 52:54:00:d7:26:a6 brd ff:ff:ff:ff:ff:ff
23: veth0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
    link/ether ee:c0:0e:d6:ae:09 brd ff:ff:ff:ff:ff:ff
24: veth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
    link/ether 4e:e8:84:bd:01:f0 brd ff:ff:ff:ff:ff:ff
ip addr add 10.0.0.1/24 dev veth0
ip link set veth0 up
ip link set veth1 up
#force sending packets out veth0
ping 10.0.0.2
```

While the ping is running, tcpdump on veth1 will show traffic (most likely ARP).

  One thing to note is that for an interface to be up, the other one must be up too.

  The main use for veth interfaces seems to be in the context of container virtualization, especially LXC. Once a veth pair is created, one end is assigned to the container and one end is assigned to the main host. Communication can then happen either using the pair as a point-to-point direct link (assigning IPs to both ends and doing routing on the host) or via bridging (the host-side interface is added to a bridge, perhaps where other interfaces are already connected, and the guest-side interface is assigned an IP inside the container).

  Since containers are possible because of namespaces, this is also the method used to "assign" the guest-side interface to the container. Note that doing so makes the interface deisappear from the host.

Let's try a simple example. First we start a container without network:
```shell
container# ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
```

Then, on the host, we create a pair of veth:
```shell
host# ip link add vHOST type veth peer name vGUEST
host# ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 52:54:00:5a:d2:86 brd ff:ff:ff:ff:ff:ff
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
    link/ether 52:54:00:d7:26:a6 brd ff:ff:ff:ff:ff:ff
25: vGUEST: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether be:86:db:5b:ec:a5 brd ff:ff:ff:ff:ff:ff
26: vHOST: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether d6:c9:65:e3:bb:e9 brd ff:ff:ff:ff:ff:ff
```
Bring the links up:
```shell
host# ip link set vHOST up
host# ip link set vGUEST up
```
Now we have to find out the PID of the container's main process; there are a few ways to do this, pstree is probably visually easier:
```shell
host# pstree -Apc
...
        |-lxc-start(3615)---init(3619)-+-getty(4236)
        |                              |-getty(4238)
        |                              |-getty(4239)
        |                              |-getty(4240)
        |                              |-login(4237)---bash(4447)
        |                              `-sshd(4223)
...
```
so we want PID 3619, and thus we do
```shell
host# ip link set vGUEST netns 3619
```
Doing this makes the interface disappear from the host:
```shell
host# ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether 52:54:00:5a:d2:86 brd ff:ff:ff:ff:ff:ff
3: eth1: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT qlen 1000
    link/ether 52:54:00:d7:26:a6 brd ff:ff:ff:ff:ff:ff
26: vHOST: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT qlen 1000
    link/ether d6:c9:65:e3:bb:e9 brd ff:ff:ff:ff:ff:ff
```
and appear in the guest container:
```shell
container# ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
25: vGUEST: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP qlen 1000
    link/ether be:86:db:5b:ec:a5 brd ff:ff:ff:ff:ff:ff
```
Now we can configure IPs and we're set:
```shell
host# ip addr add 10.0.0.1/24 dev vHOST
container# ip addr add 10.0.0.2/24 dev vGUEST
container# ping 10.0.0.1
PING 10.0.0.1 (10.0.0.1) 56(84) bytes of data.
64 bytes from 10.0.0.1: icmp_req=1 ttl=64 time=0.103 ms
...
```
As mentioned, another possibility would be adding vHOST to a bridge.
