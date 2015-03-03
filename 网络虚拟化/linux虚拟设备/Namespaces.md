this documentation is from http://www.opencloudblog.com/?p=42
# Linux Network Namespaces

## Introduction

  In the professional networking world it is quite common to use Virtual Routing and Forwarding VRFs for a long time. Cisco, Alcatel-Lucent, Juniper and others are supporting this technology. In the L2 switching world, the concept of VLANs has been used since the 90’s of the last century. One physical switch supports more than one broadcast domain. Most switches are supporting up to 4k Vlans.

  This idea has been adopted to the L3 world. Many network devices are supporting now VRFs. This means, that more than one virtual router (Layer 3 forwarding instance) can be run on one physical device.

  In the Linux world, the VRFs of the professional networking world got the name “network namespace”. In Linux, there are other namespaces available (like mount namespace…). The acticle at http://lwn.net/Articles/531114/  has more details.

  Each network namespace has it’s own routing table, it’s own iptables setup providing nat and filtering. Linux network namespaces offer in addition the capability to run processes within the network namespace.

  But why should someone use this feature. Think about a firewall running on a Linux system. You should assign all service interfaces of the firewall to a network namespace. After this, the default network namespace and the firewall network namespace are running with different routing tables. An applications like SSH is only reachable in the default namespace but not in the firewall namespace. And you may use the same IP addresses in each namespace without any interferance – but be careful on the L2 layer!

  The following sections show the basic usage. A more complex example using also linux bridges or the openvswitch is available in this [Interconnecting Namespaces](#jintername).
  
## Basic network namespace commands

  The tool to handle network namespaces is the command ip. Some users may know this tool as the replacement for the deprecated tools ifconfig, route, netstat…. You must be root for all operations which change the configuration of the network stack.

  Mapping of the commands between the ip and the depricated tools:
```shell
ip addr
ip link set dev <interface> up/down
ip addr add <ip>/<masklen> dev <interface>
ip route
ip route add <net>/<netmasklen> via <gateway>
```
  
### Check your Linux for namespace support
  
  Before trying to play with network namespaces check it your Linux system supports network namespaces. Ubuntu 12.04 and higher versions have the feature on board.

### Creating a network namespace
```shell
#add a new namespace
ip netns add <network namespace name>
#Example:
ip netns add nstest
```
  
### Listing all existing network namespaces in the system
```shell
#list all namespaces
ip netns list
nstest
```
  
### Deleting a network namespace
  
  A network namespace can be deleted using the command
```shell
ip netns delete <network namespace name>
```
  
### Executing a command in a network namespace
  
  The command ip offers the “black magic” to execute commands in the network namespace. The following is used:
```shell
#execute a command in a namespace
ip netns exec <network namespace name> <command>
#Example using the namespace from above:
#shows all ip interfaces and addresses in the namespace
ip netns exec nstest ip addr
```
  A “dirty” trick is to not start each command with the prefix ip netns exec…. Start a shell in the network namespace using
```shell
ip netns exec <network namespace name> bash
```
  But do not forget, that you are now “trapped” in the network namespace. Just type exit to leave.
  
  
