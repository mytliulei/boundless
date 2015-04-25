#!/bin/bash

taks_name="test"
dcnoscfg_path="/home/test/dcnos"
dcnos_version="7.3.3.0"
docker_id="docker"
env_cfg_file="docconfig"
env_nosimg_path="./"
env_registry_address="192.168.30.144:8080"

function linkContainer()
{
    #echo "container " $1
    #echo "interface " $2
    #echo "vethname  " $3

    pid=`docker inspect -f '{{.State.Pid}}' $1`

    if [ ! -e /var/run/netns/$pid ]; then
        ln -s /proc/$pid/ns/net /var/run/netns/$pid
    fi
    
    ip link set $3 netns $pid
    ip netns exec $pid ip link set dev $3 name $2
    ip netns exec $pid sysctl -w net.ipv6.conf.$2.disable_ipv6=1
    ip netns exec $pid ip link set $2 up
}

#check env_cfg_file clear.sh nosimg dcn_console file
if [ ! -f "./clear.sh" ]; then
    echo "clear.sh not exists,please check"
    exit 2
fi
if [ ! -f "./$env_cfg_file" ]; then
    echo "$env_cfg_file not exists,please check"
    exit 2
fi

#check nosimg and dcn_console file exists in $env_nosimg_path
if [ ! -f "$env_nosimg_path/nosimg" ]; then
    echo "$env_nosimg_path/nosimg not exists,please check"
    exit 2
fi
if [ ! -f "$env_nosimg_path/dcn_console" ]; then
    echo "$env_nosimg_path/dcn_console,please check"
    exit 2
fi

#pull docker container xfdsend and dcnos_env
#docker_xfdsend_version=`docker images | grep mytliulei/xfdsend.*latest | awk '{print $2}'`
docker_xfdsend_version="test"
if [ $docker_xfdsend_version != "latest" ]; then
    echo "##################################################################"
    echo "pull docker img xfdsend from docker registry $env_registry_address"
    docker pull $env_registry_address/xfdsend:latest
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "command error: docker not installed or not connect docker hub,please check"
        exit 1
    fi
fi

#docker_dcnosenv_version=`docker images | grep mytliulei/dcnos_env.*latest | awk '{print $2}'`
docker_dcnosenv_version="test"
if [ $docker_dcnosenv_version != "latest" ]; then
    echo "##################################################################"
    echo "pull docker img dcnos_env from docker registry $env_registry_address"
    docker pull $env_registry_address/dcnos_env:latest
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "command error: docker not installed or not connect docker hub,please check"
        exit 1
    fi
fi

#env name
env_name=`cat $env_cfg_file | grep name | awk 'BEGIN {FS=":"} {print $2}'`
env_name=${env_name// /}
echo "##################################################################"
echo "Now config the virtual test env of "$env_name

#config path dev config
env_cfg_path="$dcnoscfg_path/dev/$taks_name/$env_name"

#start up dcnos docker container
devlist=`cat $env_cfg_file | grep switch | awk '{print $2}'`
idevnum=1
swarray_num=3
swarray_porti=0
swarray_maci=1
swarray_devtypei=2

for devname in $devlist
do
    echo "--------------------------------------------------------------"
    echo "start dcnos docker" $devname
    mkdir -p $env_cfg_path/$devname/nos/
    mkdir -p $dcnoscfg_path/img/$dcnos_version/img/
    env_devdocker=${taks_name}${docker_id}${env_name}${devname}
    docker run -d --name $env_devdocker -P -v $env_cfg_path/$devname/nos/:/home/nos/ -v $dcnoscfg_path/img/$dcnos_version/img/:/home/nos/img/ --privileged $env_registry_address/dcnos_env:latest
    docker exec $env_devdocker /etc/init.d/xinetd start
    if [ ! -f "$env_cfg_path/$devname/nos/start.sh" ]; then
        docker exec $env_devdocker cp /home/start.sh /home/nos/start.sh
        docker exec $env_devdocker cp /home/stop.sh /home/nos/stop.sh
    fi
    if [ ! -f "$dcnoscfg_path/img/$dcnos_version/img/nosimg" ]; then
        cp $env_nosimg_path/nosimg $dcnoscfg_path/img/$dcnos_version/img/nosimg
        cp $env_nosimg_path/dcn_console $dcnoscfg_path/img/$dcnos_version/img/dcn_console
        chmod +x $dcnoscfg_path/img/$dcnos_version/img/nosimg
        chmod +x $dcnoscfg_path/img/$dcnos_version/img/dcn_console
    fi
    if [ -f "$env_cfg_path/$devname/nos/startup.cfg" ]; then
        docker exec $env_devdocker rm -f /home/nos/startup.cfg
    fi
    for i in $(seq $swarray_num)
    do

        swarray[$idevnum]=""
        ((idevnum++))
    done
done

#start xf tester docker container
xflist=`cat $env_cfg_file | grep tester | awk '{print $2}'`
ixfnum=1
xfarray_num=1
xfarray_porti=0
for xf in $xflist
do
    echo "--------------------------------------------------------------"
    echo "start tester docker" $xf
    env_xfdocker=$taks_name$docker_id$env_name$xf
    docker run -t -i -P -d --name $env_xfdocker $env_registry_address/xfdsend:latest /bin/bash
    #xfarray[$xf]=""
    for i in $(seq $xfarray_num)
    do

        xfarray[$ixfnum]=""
        ((ixfnum++))
    done
done


#creat veth interface
echo "------------------------------------------------------------------"
echo "make connection between devices using veth"
env_veth=$docker_id
linelist=`cat $env_cfg_file | grep line | awk 'BEGIN {FS=":"} {print $2}'`
for line in $linelist
do
    echo "make veth" $env_veth$line"-1" $env_veth$line"-2"
    ip link add $env_veth$line"-1" type veth peer name $env_veth$line"-2"
    linearray[$line]=2
done

mkdir -p /var/run/netns

#move vet interface to container
mod="line"
file=`cat $env_cfg_file`
swflag=0
swincr=0
testerflag=0
testerincr=0
for word in $file
do
    if [ $word == "switch" ]; then
        mod="switch"
        swflag=1
        ((swincr++))
        testerflag=0
        continue
    elif [ $word == "tester" ]; then
        mod="tester"
        swflag=0
        testerflag=1
        ((testerincr++))
        continue
    elif [[ $word =~ "port"[0-9] ]]; then
        mod="port"
        seq=`echo $word | awk 'BEGIN {FS="[^0-9]+"} {print $2}'`
        continue
    elif [ $word == "mac" ]; then
        mod="mac"
        continue
    elif [ $word == "devtype" ]; then
        mod="devtype"
        continue
    fi

    if [ $mod == "switch" ]; then
        devname=$word
        continue
    elif [ $mod == "tester" ]; then
        devname=$word
        continue
    elif [ $mod == "mac" ]; then
        if [ $swflag -eq 1 ]; then
            let macindex=swincr*swarray_num-swarray_maci
            swarray[$macindex]=$word
        fi
    elif [ $mod == "devtype" ]; then
        if [ $swflag -eq 1 ]; then
            let typeindex=swincr*swarray_num-swarray_devtypei
            swarray[$typeindex]=$word
        fi
    elif [ $mod == "port" ]; then
        linenum=$word
        vethnum=${linearray[$linenum]}
        if [ $vethnum -eq 0 ]; then
            echo "error on line" $linenum $devname
            echo "run clear.sh to clear the docker container"
            ./clear.sh
            exit 3
        fi

        echo "move "$env_veth$linenum"-"$vethnum "to switch" $devname "as eth"$seq
        env_devdocker=$taks_name$docker_id$env_name$devname
        linkContainer $env_devdocker "eth"$seq $env_veth$linenum"-"$vethnum
        linearray[$linenum]=$[${linearray[$linenum]} - 1]
        if [ $testerflag -eq 1 ]; then
            let xfportindex=testerincr*xfarray_num-xfarray_porti
            xfarray[$xfportindex]+="eth"$seq","
            continue
        fi
        if [ $swflag -eq 1 ]; then
            let portindex=swincr*swarray_num-swarray_porti
            swarray[$portindex]+="port$seq;eth$seq "
            continue
        fi
    fi

done

#start xf tester daemon in docker
ixfnum=1
for xf in $xflist
do
    ixfnx=$xfarray_num
    echo "------------------------------------------------------------------"
    echo "start tester damon" $xf
    env_xfdocker=$taks_name$docker_id$env_name$xf
    xfiface=${xfarray[$ixfnum]}
    ((ixfnum++))
    ((ixfnx--))
    echo "start XiaoFish -d -m 1 -i ${xfiface:0:end-1}"
    docker exec $env_xfdocker python /home/XiaoFish.py -d -m 2 -i ${xfiface:0:end-1}
    for i in $(seq $ixfnx)
    do
        ((ixfnum++))
    done
done

#config devconfig,to run dcnos img in docker
idevnum=1
for devname in $devlist
do
    iswnum=$swarray_num
    echo "------------------------------------------------------------------"
    echo "config dcnos devconfig" $devname
    echo "devtype" ${swarray[$idevnum]}
    echo "devtype" ${swarray[$idevnum]} > $env_cfg_path/$devname/nos/devconfig
    ((idevnum++))
    ((iswnum--))
    echo "mac" ${swarray[$idevnum]}
    echo "mac" ${swarray[$idevnum]} >> $env_cfg_path/$devname/nos/devconfig
    ((idevnum++))
    ((iswnum--))
    for stri in ${swarray[$idevnum]}
    do
        wstr=${stri//;/ }
        echo $wstr
        echo $wstr >> $env_cfg_path/$devname/nos/devconfig
    done
    ((idevnum++))
    ((iswnum--))
    for i in $(seq $iswnum)
    do
        ((idevnum++))
    done
done

#print dev telnet address and xf rypc address
t_eth=`ip route | grep default | awk '{print $5}'`
t_ipmask=`ip addr show $t_eth | grep "inet " | awk '{print $2}'`
t_ip=`echo $t_ipmask | cut -d "/" -f1`
echo ""
echo "##################################################################"
echo "$env_name test env is completed"
echo "##################################################################"
for devname in $devlist
do
    env_devdocker=$taks_name$docker_id$env_name$devname
    t_port=`docker port $env_devdocker | grep 23 | awk 'BEGIN {FS=":"} {print $2}'`
    echo "--------------------------------------------------------------"
    echo "you can login "$devname" by telnet "$t_ip":"$t_port" on moni or Dauto"
    echo ""
    echo "username/password is admin:admin"
    echo ""
    echo "and type 'cd /home/nos'"
    echo ""
    echo "and type './start.sh' to run dcnos"
    echo ""
    echo "then you can get the switch console"
    echo "--------------------------------------------------------------"
done
echo "##################################################################"
for xf in $xflist
do
    env_xfdocker=$taks_name$docker_id$env_name$xf
    t_port=`docker port $env_xfdocker | grep 11918 | awk 'BEGIN {FS=":"} {print $2}'`
    echo "--------------------------------------------------------------"
    echo "you can control tester "$xf" by "$t_ip":"$t_port
    echo ""
    echo "if running moni script,you can config the "$t_ip":"$t_port" in DsendConfig.py"
    echo ""
    echo "if running python script,you can config "$t_ip" in xxx_config_topu.py,"
    echo ""
    echo "and config ConnectDsend(ip,port='$t_port') in xxx_initial.py or xxx_main.py"
    echo "--------------------------------------------------------------"
done
echo "##################################################################"
