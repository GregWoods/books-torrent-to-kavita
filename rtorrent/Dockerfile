FROM alpine:latest
RUN mkdir -p /config
COPY ./config/.rtorrent.rc /config/.rtorrent.rc
RUN apk add --no-cache rtorrent
CMD ["rtorrent"]