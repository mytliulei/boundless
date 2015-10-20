# VERSION     0.1

FROM ioft/i386-ubuntu:14.04.2
MAINTAINER Liu Lei <liuleic@gmail.com>

RUN rm -rf /var/lib/apt/lists/*
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak
COPY ./sources.list /etc/apt/sources.list
RUN linux32 apt-get update \ 
    && linux32 apt-get install -y gcc \
    python2.7 \
    python2.7-dev \
    python-pip 
RUN mkdir -p /tmp/tcl
RUN mkdir -p /tmp/spirent
COPY ./tcl8.5.9-src.tar.gz /tmp/tcl/
COPY ./Spirent_TestCenter_Auto_Linux_4.46.tar.gz /tmp/spirent/
WORKDIR /tmp/tcl
RUN tar -zxvf tcl8.5.9-src.tar.gz
WORKDIR tcl8.5.9/unix
RUN linux32 ./configure --disable-shared
RUN linux32 make
RUN linux32 make install
WORKDIR /tmp/spirent
RUN tar -zxvf Spirent_TestCenter_Auto_Linux_4.46.tar.gz
RUN mkdir -p /usr/local/lib/tcl8.5/stc2.0
RUN cp -r Spirent_TestCenter_4.46/Spirent_TestCenter_Application_Linux/* /usr/local/lib/tcl8.5/stc2.0/
WORKDIR /
#EXPOSE 
ENTRYPOINT ["linux32"]


