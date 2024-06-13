FROM docker.elastic.co/logstash/logstash:8.2.0

COPY pipeline/*.conf /usr/share/logstash/pipeline/
COPY ./api_data.csv /usr/share/logstash/api_data.csv