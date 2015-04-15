#xiaofish deamon
#
# VERSION     0.1

FROM ubuntu:14.04
MAINTAINER Liu Lei <liuleic@digitalchina.com>

RUN dpkg --add-architecture i386
RUN apt-get update \ 
    && apt-get install -y libc6:i386 \
    libncurses5:i386 \
    libstdc++6:i386 \
    tcpdump \
    telnetd \
    telnet \
    xinetd \
    openssh-server
RUN useradd admin -g root
RUN echo admin:admin | chpasswd
COPY ./telnet/telnet /etc/xinetd.d/
COPY ./telnet/passwd /etc/
COPY ./telnet/xinetd.conf /etc/
EXPOSE 22 23
RUN mv /etc/securetty /etc/securetty.bak
RUN mkdir -p /var/run/sshd
CMD ["/usr/sbin/sshd","-D"]
RUN echo "root:123456" | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
COPY ./start.sh /home/
COPY ./stop.sh /home/
RUN chmod +x /home/start.sh
RUN chmod +x /home/stop.sh
