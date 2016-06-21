FROM ubuntu:14.04

MAINTAINER Liu Lei <mytliulei@gmail.com>

# install package
RUN apt-get update \
    && apt-get install -y python \
    vim tftpd-hpa
RUN groupadd ftpgroup
RUN useradd -g ftpgroup -d /home/ftpusers -s /bin/bash ftpuser

RUN mkdir -p /home/ftpusers
RUN chown ftpuser:ftpgroup /home/ftpusers
EXPOSE 69/udp
ENTRYPOINT ["/usr/sbin/in.tftpd","--foreground","--listen","--user ftpuser", "--address [::]:69","--secure","/home/ftpusers/tftp"]
