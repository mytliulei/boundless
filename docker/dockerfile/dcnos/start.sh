#!/bin/bash

trap "" SIGTSTP

cd /home/nos

#defultNum=32
#configNum=`cat devconfig | grep maxvlan | awk '{print $2}'`
#
#if [[ $configNum =~ ^[0-9]+$ ]]; then
#    maxVlanNum=$configNum
#else
#    maxVlanNum=$defultNum
#fi

###get mac
##hostmac=`ip link show dev eth0 | grep ether | awk '{print $2}'`
##echo "mac 00:03:0f:"${hostmac:9:17} > devconfig
##
###get host ip
##hostip=`ip address show dev eth0 | grep "inet " | awk '{print $2}' | awk 'BEGIN {FS="/"} {print $1}'`
##echo "hostip" $hostip >> devconfig
##
###get port 
##ethlist=`ip link show | grep eth[0-9] | awk 'BEGIN {FS=":"} {print $2}'`
##for ethname in $ethlist
##do
##    if [ $ethname == "eth0" ]; then
##        continue
##    fi
##
##    seq=`echo $ethname | awk 'BEGIN {FS="[^0-9]+"} {print $2}'`
##    echo "port"$seq  $ethname >> devconfig
##done

devlist=$(cat devconfig | grep port | awk '{print $2}')
for dev in $devlist
do
    ifconfig $dev promisc

#    for ((j=1; j<=$maxVlanNum; j++))
#    do
#        #echo "add vlan dev "$dev"."$j
#        vconfig add $dev $j >& /dev/null
#        ifconfig $dev"."$j up >& /dev/null
#    done
done

/home/nos/img/nosimg&
/home/nos/img/dcn_console

#for dev in $devlist
#do
#    for ((j=1; j<=$maxVlanNum; j++))
#    do
#        #echo "delete vlan dev "$dev"."$j
#        vconfig rem $dev"."$j >& /dev/null
#    done
#    
#    ifconfig $dev -promisc
#done
