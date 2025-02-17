# docker build --platform linux/amd64 -t l241025097/python_rich:3.8.0 .
FROM l241025097/python:3.8.0
ADD src.tar /home/jd
RUN cp /home/jd/src/crons/execute.cron /etc/cron.d/execute.cron
RUN chmod 0644 /etc/cron.d/execute.cron
RUN crontab /etc/cron.d/execute.cron
WORKDIR /home/jd/src
CMD cron && /usr/local/bin/python app.py
