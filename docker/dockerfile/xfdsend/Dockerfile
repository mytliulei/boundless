#xiaofish deamon
#
# VERSION     0.1

FROM ubuntu:14.04
MAINTAINER Liu Lei <liuleic@digitalchina.com>

RUN apt-get update \ 
    && apt-get install -y python \
    python-dev \
    python-pip \
    tcpdump
RUN pip2 install scapy \
    && pip2 install rpyc \
    && pip2 install robotremoteserver \
    && pip2 install daemonocle

ADD XiaoFish.py /home/
EXPOSE 11918
COPY ./Dscapy/*.py /usr/local/lib/python2.7/dist-packages/scapy/
COPY ./Dscapy/layers/*.py /usr/local/lib/python2.7/dist-packages/scapy/layers/
#ENTRYPOINT ["python","/home/XiaoFish.py","-m 2"]
CMD ["python","/home/XiaoFish.py","-m 2"]
