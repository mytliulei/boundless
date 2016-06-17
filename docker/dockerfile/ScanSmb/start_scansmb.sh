#!/bin/bash

# written by Liu Lei <mytliulei@gmail.com>

t_eth=`ip route | grep default | awk '{print $5}'`
t_ipmask=`ip addr show $t_eth | grep "inet " | awk '{print $2}'`
t_ip=`echo $t_ipmask | cut -d "/" -f1`

redis_id=`docker ps -aq -f name="redis-server"`
tftpd_v_id=`docker ps -aq -f name="tftpd_data"`
tftpd_id=`docker ps -aq -f name="tftpd"`
disfile_id=`docker ps -aq -f name="discover_file"`
cron_tftp_id=`docker ps -aq -f name="cron_clear_tftp"`

#check redis container exists
if [ "$redis_id" == "" ]; then
    #start redis container
    docker run -d -p 6379:6379 --name redis-server redis
else
    docker start redis-server
fi

#check tftpd_data volumes container exists
if [ "$tftpd_v_id" == "" ]; then
    #start ftpd volumes and monitor fs container
    docker run -d -ti --name tftpd_data mytliulei/tftp_data
fi

#check tftpd container exists
if [ "$tftpd_id" == "" ]; then
    #start pureftpd container
    docker run -d -p 69:69/udp --volumes-from tftpd_data --name tftpd --privileged mytliulei/tftp_server
else
    docker start tftpd
fi

#check scan smb path container exists
if [ "$disfile_id" == "" ]; then
    #start pureftpd container
    docker run -d --volumes-from tftpd_data --name discover_file mytliulei/discover_file
else
    docker start discover_file
fi

#check cron_clear_ftp container exists
if [ "$cron_tftp_id" == "" ]; then
    #start cron_clear_ftp container
    docker run -d --volumes-from tftpd_data --name cron_clear_tftp mytliulei/clear_tftp
else
    docker start cron_clear_tftp
fi
