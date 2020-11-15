# Downloader
Support http(s), ftp, ~~p2p~~ protocols and bilibili crawler.

### Demo

![http demo](https://github.com/AlitaMcF/Downloader/blob/master/image/downloader_demo.png)

### Functions

1. The downloader can download multiple files simultaneously.
2. There may be several threadings take charge of downloading a single file, which depends on the size of file.
3. The next downloading can continue from the last time location. In other words, it supports resuming.
4. The speed of Bilibili crawler is slower compared with http(s) protocol downloading, namely, only one threading take charge of one single bilibili file. The reason that downloader do not use multithreading is avoiding triggering bilibili's Risk Control Strategy, which can cause the blocking of IP or API.

### Code explanation
* \_\_main\_\_.py: the entry function.
* downloader.py: the main class of Downloader.
* httpdlr.py: http(s) protocol downloading class.
* bilibilidlr.py: bilibili crawler.

### Some dependence setups.

1. If the code inform Error fetching file **ffmpeg-osx-v3.2.4** (depends on your environment), download this file manually and put it into directory (based on macOS): ```/Users/yourusername/Library/Application\ Support/imageio/ffmpeg/```. Manually download it from: https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/ffmpeg-osx-v3.2.4
2. The version of **imageio** library is v2.4.1, or the code would throw error.
