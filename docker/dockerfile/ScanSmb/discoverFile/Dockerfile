FROM ubuntu:14.04

MAINTAINER Liu Lei <mytliulei@gmail.com>

# install package
RUN apt-get update \
    && apt-get install -y python \
    python-pip \
    vim
RUN pip install pysmb \
    && pip install redis

# setup ftpgroup and ftpuser
RUN groupadd ftpgroup
RUN useradd -g ftpgroup -d /home/ftpusers -s /bin/bash ftpuser

# mkdir for ftp
RUN mkdir -p /home/ftpusers

RUN chown ftpuser:ftpgroup /home/ftpusers
COPY DiscoverFile.py /home/ftpusers/DiscoverFile.py
RUN chown ftpuser:ftpgroup /home/ftpusers/DiscoverFile.py
COPY ftpuser /var/spool/cron/crontabs/ftpuser
RUN chmod 600 /var/spool/cron/crontabs/ftpuser
RUN chown ftpuser:crontab /var/spool/cron/crontabs/ftpuser
CMD ["cron", "-f"]
WORKDIR /home/ftpusers/
