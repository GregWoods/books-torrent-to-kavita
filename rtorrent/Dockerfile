FROM alpine:latest
RUN mkdir -p /config
COPY ./config/.rtorrent.rc /root/rtorrent.rc
ENV RTORRENT_RC=/config/rtorrent.rc
RUN apk add --no-cache rtorrent
CMD ["rtorrent"]