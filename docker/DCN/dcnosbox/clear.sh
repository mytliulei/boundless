#!/bin/bash

taks_name="test"
docker_id="docker"
env_name=`cat docconfig | grep name | awk 'BEGIN {FS=":"} {print $2}'`

devlist=`cat docconfig | grep switch | awk '{print $2}'`
for devname in $devlist
do
    echo "stop and rm dcnos docker" $devname
    env_devdocker=$taks_name$docker_id$env_name$devname
    docker_pid=`docker inspect -f '{{.State.Pid}}' $env_devdocker`
    docker stop $env_devdocker
    docker rm $env_devdocker
    ip netns delete $docker_pid
done

xflist=`cat docconfig | grep tester | awk '{print $2}'`
for xf in $xflist
do
    echo "stop and rm tester docker" $xf
    env_xfdocker=$taks_name$docker_id$env_name$xf
    docker_pid=`docker inspect -f '{{.State.Pid}}' $env_xfdocker`
    docker stop $env_xfdocker
    docker rm $env_xfdocker
    ip netns delete $docker_pid
done

