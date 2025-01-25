FROM alpine:3.21

RUN apk add --no-cache openssl

WORKDIR /app
VOLUME /app

COPY ./deploy/scripts/entrypoint.sh /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]

CMD [ "/bin/sh" ]
