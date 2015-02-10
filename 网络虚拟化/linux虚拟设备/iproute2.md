**this documentation is from www.github.com/dmbaturin/iproute2-cheatsheet**
# Overview

  iproute2 is the Linux networking toolkit that replaced net-tools (ifconfig, route, arp etc.)

  Old style network utilities like ifconfig and route are still there just for backwards compatibility and do not provide access to new features like policy-based routing or network namespaces.

  Note that iproute2 has been a **standard Linux tool** since the early 2000's. It's included in every distro by default, or at least available from the repos (OpenWRT is one of the cases).

  iproute2 was originally written by Alex Kuznetsov and is now maintained by Stephen Hemminger.

  This document aims to provide comprehensive but easy to use documentation for the "ip" command included in iproute2 package. There are more, such as ss (netstat replacement, fairly straightforward), tc (QoS management), but documenting them in this style, especially tc, would be a separate big project.

  Instead of listing commands and describing what they do, it lists common tasks network administrators need to perform and gives commands to solve them, hence the "cheatsheet".

  Contributions are always welcome, you can find the "source code" at www.github.com/dmbaturin/iproute2-cheatsheet.

  This document is provided "as is", without any warranty. The authors are not liable for any damage related to using it.
  
# General notes

  All commands that change any settings (that is, not just display them) require root privileges.

  There are configuration files in /etc/iproute2, mainly for assinging symbolic names to network stack entities such as routing tables. Those files are re-read at every "ip" call and you don't need to do anything to apply the changes.
  
# Typographic conventions

  Metasyntactic variables are written in shell-style syntax, ${something}. Optional command parts are in square brackets.
  
1. [Address management](#j1)
  * [Show all addresses]
  * [Show addresses for a single interface]
  * [Show addresses only for running interfaces]
  * [Show only static or dynamic IPv6 addresses]
  * [Add an address to an interface]
  * [Add an address with human-readable description]
  * [Delete an address]
  * [Remove all addresses from an interface]
  * [Notes]
2. [Route management]
  * [Connected routes]
  * [View all routes]
  * [View routes to a network and all its subnets]
  * [View routes to a network and all supernets]
  * [View routes to exact subnet]
  * [View only the route actually used by the kernel]
  * [View route cache (pre 3.6 kernels only)]
  * [Add a route via gateway]
  * [Add a route via interface]
  * [Change or replace a route]
  * [Delete a route]
  * [Default route]
  * [Blackhole routes]
  * [Other special routes]
  * [Routes with different metric]
  * [Multipath routing]
  
# Address management

  In this section ${address} value should be a host address in dotted decimal format, and ${mask} can be either a dotted decimal subnet mask or a prefix length. That is, both 192.0.2.10/24 and 192.0.2.10/255.255.255.0 are equally acceptable.

  If you are not sure if something is a correct host address, use "ipcalc" or similar program to check.
  
  **Show all addresses**
  ```shell
  ip address show
  ```
  All "show" commands can be used with "-4" or "-6" options to show only IPv4 or IPv6 addresses.
  
  **Show addresses for a single interface**
  ```shell
  ip address show ${interface name}
  ```
  Examples:
  ```shell
  ip address show eth0
  ```
  
  **Show addresses only for running interfaces**
  ```shell
  ip address show up
  ```
  
  **Show only static or dynamic IPv6 addresses**
  
  Show only statically configured addresses:
  ```shell
  ip address show [dev ${interface}] permanent
  ```
  Show only addresses learnt via autoconfiguration:
  ```shell
  ip address show [dev ${interface}] dynamic
  ```
  
  **Add an address to an interface**
  ```shell
  ip address add ${address}/${mask} dev ${interface name}
  ```
  Examples:
  ```shell
  ip address add 192.0.2.10/27 dev eth0
  ip address add 2001:db8:1::/48 dev tun10
  ```
  You can add as many addresses as you want. The first address will be primary and will be used as source address by default.

  **Add an address with human-readable description**
  ```shell  
  ip address add ${address}/${mask} dev ${interface name} label ${interface name}:${description} 
  ```
  Examples:
  ```shell
  ip address add 192.0.2.1/24 dev eth0 label eth0:my_wan_address
  ```
  Interface name with a colon before label is required, some backwards compaibility issue.
  
  **Delete an address**
  ```shell
  ip address delete ${address}/${prefix} dev ${interface name}
  ```
  Examples:
  ```
  ip address delete 192.0.2.1/24 dev eth0
  ```
  Interface name argument is required. Linux does allow to use the same address on multiple interfaces and it has valid use cases.
  
  **Remove all addresses from an interface**
  ```
  ip address flush dev ${interface name}
  ```
  Examples:
  ```
  ip address flush dev eth1
  ```
  
  **Notes**
  
  Note that there is no way to rearrange addresses and replace the primary address. Make sure you set the primary address first.
  
  
  
