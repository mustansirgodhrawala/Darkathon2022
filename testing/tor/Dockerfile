FROM alpine:latest
RUN apk update && apk upgrade && \
    apk add tor curl bash && \
    rm /var/cache/apk/* && \
    cp /etc/tor/torrc.sample /etc/tor/torrc

EXPOSE 9050-9060

ADD start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

RUN echo | sed -i 's/\r$//' /usr/local/bin/start.sh

CMD /usr/local/bin/start.sh
