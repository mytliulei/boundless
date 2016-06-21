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
RUN useradd -g ftpgroup -d /home/ftpusers -s /etc ftpuser

# mkdir for ftp
RUN mkdir -p /home/ftpusers
RUN chown ftpuser:ftpgroup /home/ftpusers
USER ftpuser
RUN mkdir -p /home/ftpusers/ftp
RUN mkdir -p /home/ftpusers/ftp/build
RUN mkdir -p /home/ftpusers/ftp/img
RUN mkdir -p /home/ftpusers/tftp
VOLUME ["/home/ftpusers/ftp","/home/ftpusers/tftp","/tmp"]
COPY monitorfs.py /home/ftpusers/monitorfs.py
WORKDIR /home/ftpusers
ENTRYPOINT ["python","monitorfs.py"]
