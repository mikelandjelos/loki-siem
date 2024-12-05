FROM docker.elastic.co/logstash/logstash:8.16.1

RUN bin/logstash-plugin install logstash-output-loki

CMD ["/usr/local/bin/docker-entrypoint"]