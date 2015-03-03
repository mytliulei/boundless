# MACVLAN
  有时我们可能需要一块物理网卡绑定多个 IP 以及多个 MAC 地址，虽然绑定多个 IP 很容易，但是这些 IP 会共享物理网卡的 MAC 地址，可能无法满足我们的设计需求，所以有了 MACVLAN 设备，其工作方式如下：

  ![linux-network-macvlan1.png](./img/linux-network-macvlan1.png)
  
  MACVLAN 会根据收到包的目的 MAC 地址判断这个包需要交给哪个虚拟网卡。单独使用 MACVLAN 好像毫无意义，但是配合network namespace 使用，我们可以构建这样的网络：

  ![linux-network-macvlan2.png](./img/linux-network-macvlan2.png)
  
  由于 macvlan 与 eth0 处于不同的 namespace，拥有不同的 network stack，这样使用可以不需要建立 bridge 在 virtual namespace 里面使用网络。
