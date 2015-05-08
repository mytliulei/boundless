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
    docker run -d -p 6379:6379 --name redis-server dcn_autotest/redis
else
    docker start redis-server
fi

#check ftpd volumes container exists
if [ "$ftpd_v_id" == "" ]; then
    #start ftpd volumes and monitor fs container
    docker run -d -ti --name ftpd_data dcn_autotest/pure-ftpd_data -i $t_ip
else
    docker start ftpd_data
fi

#check ftpd container exists
if [ "$ftpd_id" == "" ]; then
    #start pureftpd container
    docker run -d -p 21:21 --volumes-from ftpd_data --name pureftpd dcn_autotest/pure-ftpd
else
    docker start pureftpd
fi

