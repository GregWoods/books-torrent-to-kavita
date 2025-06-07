# Easy Kavikta eBook Import

The very slick book management software kavita doesn't have a UI for uploading books, you must copy the books into the Kavita folder. However, each book should be in its own folder.
Manually downloading each book, looking up the book title so you can create the correctly named folder, then copying the book into the folder is a pain.

Downloading books from Humble Bundle purchases is also painful. The "Bulk" download is nothing of the sort, it sequentially opens file download dialogs one after the other. But simultaneous download restrictions in place, and book files being dozens of Mb in size, it is a slow and error prone process

These 2 container speed up this process,

***rTorrent*** simply monitors a specificfolder (setup as a docker volume in the compose file) for .torrent files, and downloads those torrents into another specific flder

***move-books*** is a python script which monitors the downloaded files folder for ebooks. When it finds one, it extracts the title from the book's metadata, creates a new folder in the kavita books folder, and moves the book into that new folder.

Ideally, I'd have a web service which would accept the URL of the Humble Bundle purchase page, scrape it, and perform the actual file downloads before moving them into Kavikta. Unfortunately, anti-scraping measures has made this difficult without further work.

## Locally, for testing

```docker compose up --build -f compose.dev.yaml```

## Production

uses samba shares for my specific network setup

```sudo docker compose up --build --detach```


## Build and Upload to Docker Hub

```
docker login
cd rtorrent
docker build -t gregkwoods/rtorrent:latest .
docker push gregkwoods/rtorrent:latest
```
