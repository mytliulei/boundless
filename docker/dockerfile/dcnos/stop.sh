#!/bin/bash

nospid=$(ps -e | grep nosimg | awk '{print $1}')

for npid in $nospid
do
    kill $npid
done


#killall nosimg

#defultNum=32
#configNum=`cat devconfig | grep maxvlan | awk '{print $2}'`

#if [[ $configNum =~ ^[0-9]+$ ]]; then
#    maxVlanNum=$configNum
#else
#    maxVlanNum=$defultNum
#fi

devlist=$(cat devconfig | grep port | awk '{print $2}')

for dev in $devlist
do
#    for ((j=1; j<=$maxVlanNum; j++))
#    do
#        #echo "delete vlan dev "$dev"."$j
#        vconfig rem $dev"."$j >& /dev/null
#    done
    
    ifconfig $dev -promisc
done
