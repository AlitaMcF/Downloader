# Downloader
Support http(s), ftp, ~~p2p~~ protocols and bilibili crawler.

* \_\_main\_\_.py: the entry function.
* downloader.py: the main class of Downloader.
* httpdlr.py: http(s) protocol downloading class.

#### Http protocol downloading demo.

![http demo](https://github.com/AlitaMcF/Downloader/blob/master/image/downloader_http_demo.png)

#### Some dependence setup.

1. If the code inform Error fetching file **ffmpeg-osx-v3.2.4** (depends on your environment), download this file manually and put it into directory (based on macOS): ```/Users/yourusername/Library/Application\ Support/imageio/ffmpeg/```. Manually download it from: https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/ffmpeg-osx-v3.2.4
2. The version of **imageio** library is v2.4.1, or the code would throw error.

