#!/bin/bash

# written by Liu Lei <mytliulei@gmail.com>

t_eth=`ip route | grep default | awk '{print $5}'`
t_ipmask=`ip addr show $t_eth | grep "inet " | awk '{print $2}'`
t_ip=`echo $t_ipmask | cut -d "/" -f1`

redis_id=`docker ps -aq -f name="redis-server"`
ftpd_v_id=`docker ps -aq -f name="ftpd_data"`
ftpd_id=`docker ps -aq -f name="pureftpd"`

#check redis container exists
if [ "$redis_id" == "" ]; then
    #start redis container
    docker run -d -p 6379:6379 --name redis-server 192.168.30.144:8080/redis
else
    docker start redis-server
fi

#check ftpd volumes container exists
if [ "$ftpd_v_id" == "" ]; then
    #start ftpd volumes and monitor fs container
    docker run -d -ti --name ftpd_data 192.168.30.144:8080/pure-ftpd_data -i $t_ip
else
    docker start ftpd_data
fi

#check ftpd container exists
if [ "$ftpd_id" == "" ]; then
    #start pureftpd container
    docker run -d -p 21:21 -p 20:20 -p 30000:30000 -p 30001:30001 -p 30002:30002 -p 30003:30003 -p 30004:30004 -p 30005:30005 -p 30006:30006 -p 30007:30007 -p 30008:30008 -p 30009:30009 --volumes-from ftpd_data --name pureftpd --privileged --dns 127.0.0.1 192.168.30.144:8080/pure-ftpd -O clf:/var/log/pureftpd.log -P $t_ip
else
    docker start pureftpd
fi


