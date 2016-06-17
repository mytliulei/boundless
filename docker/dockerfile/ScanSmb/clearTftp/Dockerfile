FROM ubuntu:14.04

MAINTAINER Liu Lei <mytliulei@gmail.com>

# install package
RUN apt-get update \
    && apt-get install -y python \
    python-pip \
    vim

COPY del_file_cron.py /root/del_file_cron.py
COPY root /var/spool/cron/crontabs/root
RUN chown root:crontab /var/spool/cron/crontabs/root
RUN chmod 600 /var/spool/cron/crontabs/root
CMD ["cron", "-f"]
