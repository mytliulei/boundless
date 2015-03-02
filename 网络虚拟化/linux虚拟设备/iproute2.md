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
  
<h1 id="j0"> Typographic conventions</h1>

  Metasyntactic variables are written in shell-style syntax, ${something}. Optional command parts are in square brackets.
  
1. [Address management](#j1)
  * [Show all addresses](#j11)
  * [Show addresses for a single interface](#j12)
  * [Show addresses only for running interfaces](#j13)
  * [Show only static or dynamic IPv6 addresses](#j14)
  * [Add an address to an interface](#j15)
  * [Add an address with human-readable description](#j16)
  * [Delete an address](#j17)
  * [Remove all addresses from an interface](#j18)
  * [Notes](#j19)
2. [Route management](#j2)
  * [Connected routes](#j21)
  * [View all routes](#j22)
  * [View routes to a network and all its subnets](#j23)
  * [View routes to a network and all supernets](#j24)
  * [View routes to exact subnet](#j25)
  * [View only the route actually used by the kernel](#j26)
  * [View route cache (pre 3.6 kernels only)](#j27)
  * [Add a route via gateway](#j28)
  * [Add a route via interface](#j29)
  * [Change or replace a route](#j210)
  * [Delete a route](#j211)
  * [Default route](#j212)
  * [Blackhole routes](#j213)
  * [Other special routes](#j214)
  * [Routes with different metric](#j215)
  * [Multipath routing](#j216)
  
<h1 id="j1"> Address management</h1>

  In this section ${address} value should be a host address in dotted decimal format, and ${mask} can be either a dotted decimal subnet mask or a prefix length. That is, both 192.0.2.10/24 and 192.0.2.10/255.255.255.0 are equally acceptable.

  If you are not sure if something is a correct host address, use "ipcalc" or similar program to check.
  
  <b id="j11">Show all addresses</b>
  ```shell
  ip address show
  ```
  All "show" commands can be used with "-4" or "-6" options to show only IPv4 or IPv6 addresses.
  
  <b id="j12">Show addresses for a single interface</b>
  ```shell
  ip address show ${interface name}
  ```
  Examples:
  ```shell
  ip address show eth0
  ```
  
  <b id="j13">Show addresses only for running interfaces</b>
  ```shell
  ip address show up
  ```
  
  <b id="j14">Show only static or dynamic IPv6 addresses</b>
  
  Show only statically configured addresses:
  ```shell
  ip address show [dev ${interface}] permanent
  ```
  Show only addresses learnt via autoconfiguration:
  ```shell
  ip address show [dev ${interface}] dynamic
  ```
  
  <b id="j15">Add an address to an interface</b>
  ```shell
  ip address add ${address}/${mask} dev ${interface name}
  ```
  Examples:
  ```shell
  ip address add 192.0.2.10/27 dev eth0
  ip address add 2001:db8:1::/48 dev tun10
  ```
  You can add as many addresses as you want. The first address will be primary and will be used as source address by default.

  <b id="j16">Add an address with human-readable description</b>
  ```shell  
  ip address add ${address}/${mask} dev ${interface name} label ${interface name}:${description} 
  ```
  Examples:
  ```shell
  ip address add 192.0.2.1/24 dev eth0 label eth0:my_wan_address
  ```
  Interface name with a colon before label is required, some backwards compaibility issue.
  
  <b id="j17">Delete an address</b>
  ```shell
  ip address delete ${address}/${prefix} dev ${interface name}
  ```
  Examples:
  ```
  ip address delete 192.0.2.1/24 dev eth0
  ```
  Interface name argument is required. Linux does allow to use the same address on multiple interfaces and it has valid use cases.
  
  <b id="j18">Remove all addresses from an interface</b>
  ```
  ip address flush dev ${interface name}
  ```
  Examples:
  ```
  ip address flush dev eth1
  ```
  
  <b id="j19">Notes</b>
  
  Note that there is no way to rearrange addresses and replace the primary address. Make sure you set the primary address first.
  
<h1 id="j2"> Route management</h1>

  In this section ${address} refers to subnet address in dotted decimal format, and ${mask} refers to subnet mask either in prefix length or dotted decimal format. That is, both 192.0.2.0/24 and 192.0.2.0/255.255.255.0 are equally acceptable.

  **Note:** as per the section below, if you set up a static route, and it becomes useless because the interface goes down, it will be removed and never get back on its own. You may not have noticed this behaviour because in many cases additional software (e.g. NetworkManager or rp-pppoe) takes care of restoring routes associated with interfaces.

  If you are going to use your Linux machine as a router, consider installing a routing protocol stack suite like Quagga or BIRD. They serve as routing control plane, keeping configured routes and restoring them after link failures properly in general case, and also providing dynamic routing protocol (e.g. OSPF and BGP) functionality.

  <b id="j21">Connected routes</b>

  Some routes appear in the system without explicit configuration (against your will).

  Once you assign an address to an interface, a route to the subnet it belongs is automatically created via the interface you assigned it too. This is exactly the reason "ip address add" command wants subnet mask, otherwise the system would be unable to find out its subnet address and create connected routes properly.

  When an interface goes down, connected routes associated with it are removed. This is used for inaccessible gateway detection so routes through gateways that went inaccessible are removed. Same mechanism prevents you from creating routes through inaccessible gateways.

  <b id="j22">View all routes</b>
  ```
  ip route
  ip route show
  ```
  Show commands accept -4 and -6 options to view only IPv4 or IPv6 routes. If no options given, IPv4 routes are displayed. To view IPv6 routes, use:
  ```
  ip -6 route
  ```
  
  <b id="j23">View routes to a network and all its subnets</b>
  ```
  ip route show to root ${address}/${mask}
  ```
  For example, if you use 192.168.0.0/24 subnet in a part of your network and it's broken into 192.168.0.0/25 and 192.168.0.128/25, you can see all those routes with:
  ```
  ip route show to root 192.168.0.0/24
  ```
  Note: the word "to" in this and other show commands is optional.
  
  <b id="j24">View routes to a network and all supernets</b>
  ```
  ip route show to match ${address}/${mask}
  ```
  If you want to view routes to 192.168.0.0/24 and all larger subnets, use:
  ```
  ip route show to match 192.168.0.0/24
  ```
  As routers prefer more specific routes to less specific, this is often useful for debugging in situations when traffic to a specific subnet is sent the wrong way because a route to it is missing but routes to larger subnets exist.
  
  <b id="j25">View routes to exact subnet</b>
  ```
  ip route show to exact ${address}/${mask}
  ```
  If you want to see the routes to 192.168.0.0/25, but not to, say 192.168.0.0/25 and 192.168.0.0/16, you can use:
  ```
  ip route show to exact 192.168.0.0/24
  ```
  
  <b id="j26">View only the route actually used by the kernel</b>
  ```
  ip route get ${address}/${mask}
  ```
  Example:
  ```
  ip route get 192.168.0.0/24
  ```
  Note that in complex routing scenarios like multipath routing, the result may be "correct but not complete", as it always shows one route that will be used first. In most situations it's not a problem, but never forget to look at the corresponsing "show" command output too.
  
  <b id="j27">View route cache (pre 3.6 kernels only)</b>
  ```
  ip route show cached
  ```
  Until the version 3.6, Linux used route caching. In older kernels, this command displays the contents of the route cache. It can be used with modifiers described above. In newer kernels it does nothing.

  <b id="j28">Add a route via gateway</b>
  ```
  ip route add ${address}/${mask} via ${next hop}
  ```
  Examples:
  ```
  ip route add 192.0.2.128/25 via 192.0.2.1
  ip route add 2001:db8:1::/48 via 2001:db8:1::1
  ```

  <b id="j29">Add a route via interface</b>
  ```
  ip route add ${address}/${mask} dev ${interface name}
  ```
  Example:
  ```
  ip route add 192.0.2.0/25 dev ppp0
  ```
  Interface routes are commonly used with point-to-point interfaces like PPP tunnels where next hop address is not required.
  
  <b id="j210">Change or replace a route</b>
  
  You may use "change" command to change parameters of existing routes. "Replace" command can be used to add new route or modify existing one if it doesn't exist. Examples:
  ```
  ip route change 192.168.2.0/24 via 10.0.0.1
  ip route replace 192.0.2.1/27 dev tun0
  ```
  
  <b id="j211">Delete a route</b>
  ```
  ip route delete ${rest of the route statement}
  ```
  Examples:
  ```
  ip route delete 10.0.1.0/25 via 10.0.0.1
  ip route delete default dev ppp0
  ```

  <b id="j212">Default route</b>

  There is a shortcut to add default route.
  ```
  ip route add default via ${address}/${mask}
  ip route add default dev ${interface name}
  ```
  These are equivalent to:
  ```
  ip route add 0.0.0.0/0 ${address}/${mask}
  ip route add 0.0.0.0/0 dev ${interface name}
  ```
  With IPv6 routes it also works and is equivalent to ::/0
  ```
  ip -6 route add default via 2001:db8::1
  ```
  
  <b id="j213">Blackhole routes</b>
  ```
  ip route add blackhole ${address}/${mask}
  ```
  Examples:
  ```
  ip route add blackhole 192.0.2.1/32
  ```
  Traffic to destinations that match a blackhole route is silently discarded.

  Blackhole routes have dual purpose. First one is straightforward, to discard traffic sent to unwanted destinations, e.g. known malicious hosts.

  The second one is less obvious and uses the "longest match rule" as per RFC1812. In some cases you may want the router to think it has a route to a larger subnet, while you are not using it as a whole, e.g. when advertising the whole subnet via dynamic routing protocols. Large subnets are commonly broken into smaller parts, so if your subnet is 192.0.2.0/24, and you have assigned 192.0.2.1/25 and 192.0.2.129/25 to your interfaces, your system creates connected routes to the /25's, but not the whole /24, and routing daemons may not want to advertise /24 because you have no route to that exact subnet. The solution is to setup a blackhole route to 192.0.2.0/24. Because routes to smaller subnets are preferred over larger subnets, it will not affect actual routing, but will convince routing daemons there's a route to the supernet.

  <b id="j214">Other special routes</b>
  ```
  ip route add unreachable ${address}/${mask}
  ip route add prohibit ${address}/${mask}
  ip route add throw ${address}/${mask}
  ```
  These routes make the system discard packets and reply with an ICMP error message to the sender.
  
*unreachable*

  Sends ICMP "host unreachable".
  
*prohibit*

  Sends ICMP "administratively prohibited".
  
*throw*

  Sends "net unreachable".
  
  Unlike blackhole routes, these can't be recommended for stopping unwanted traffic (e.g. DDoS) because they generate a reply packet for every discarded packet and thus create even greater traffic flow. They can be good for implementing internal access policies, but consider firewall for this purpose first.

  "Throw" routes may be used for implementing policy-based routing, in non-default tables they stop current table lookup, but don't send ICMP error messages.

  <b id="j215">Routes with different metric</b>
  ```
  ip route add ${address}/${mask} via ${gateway} metric ${number}
  ```
  Examples:
  ```
  ip route add 192.168.2.0/24 via 10.0.1.1 metric 5
  ip route add 192.168.2.0 dev ppp0 metric 10
  ```
  If there are several routes to the same network with different metric value, the one with the lowest metric will be preferred.

  Important part of this concept is that when an interface goes down, routes that would be rendered useless by this event disappear from the routing table (see "Connected Routes" section), and the system will fall back to higher metric routes.

  This feature is commonly used to implement backup connections to important destinations.

  <b id="j26">Multipath routing</b>
  ```
  ip route add ${addresss}/${mask} nexthop via ${gateway 1} weight ${number} nexthop via ${gateway 2} weight ${number}
  ```
  Multipath routes make the system balance packets across several links according to the weight (higher weight is preferred, so gateway/interface with weight of 2 will get roughly two times more traffic than another one with weight of 1). You can have as many gateways as you want and mix gateway and interface routes, like:
  ```
  ip route add default nexthop via 192.168.1.1 weight 1 nexthop dev ppp0 weight 10
  ```
  **Warning:** the downside of this type of balancing is that packets are not guaranteed to be sent back through the same link they came in. This is called "asymmetric routing". For routers that simply forward packets and don't do any local traffic processing such as NAT, this is usually normal, and in some cases even unavoidable.

  If your system does anything but forwarding packets between interfaces, this may cause problems with incoming connections and some measures should be taken to prevent it.
  
