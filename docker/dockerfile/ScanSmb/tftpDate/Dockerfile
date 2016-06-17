FROM ubuntu:14.04

MAINTAINER Liu Lei <mytliulei@gmail.com>

# install package
RUN apt-get update \
    && apt-get install -y python \
    python-dev \
    python-pip \
    vim
RUN pip install pyinotify \
    && pip install redis

# setup ftpgroup and ftpuser
RUN groupadd ftpgroup
RUN useradd -g ftpgroup -d /home/ftpusers -s /user/sbin/nologin ftpuser

# mkdir for ftp
RUN mkdir -p /home/ftpusers

RUN chown ftpuser:ftpgroup /home/ftpusers
USER ftpuser
RUN mkdir -p /home/ftpusers/tftp
VOLUME [/home/ftpusers/tftp","/tmp"]
WORKDIR /home/ftpusers
CMD ["echo","this is tftp data volume container"]
