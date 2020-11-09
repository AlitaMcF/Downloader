import requests
import os
import threading
import json
import sys
import hashlib
from httpdlr import HttpDlr
from tqdm import tqdm


class Downloader:
    def __init__(self, url_list, path='./data/'):
        self.display_lock = threading.Lock()
        self.url_list = url_list
        self.path = path

    def launch(self):
        """
        the main function of Downloader.
        :return:
        """
        for url in self.url_list:
            protocol = url.split(':')[0]
            if protocol.lower() in ['http', 'https']:
                self._http_download(url)

    def _http_download(self, url):
        """
        handle http(s) downloading.
        :param url:
        :return:
        """
        threads = []
        try:
            file_name = url.split('/')[-1]
            config_file_name = file_name + '_config.json'
            # self._delete_file(file_name, config_file_name)
            [content_length, etag, md5] = self._get_download_file_info_http(url)
            # process bar
            process_bar = tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=file_name.ljust(35, '-'),
                               total=content_length)
            thread_num = self._count_thread_num(content_length)
            # the size of each partition
            part_size = content_length // thread_num
            self._check_config_file(url, config_file_name, file_name, thread_num, content_length, etag)
            self._check_file(file_name, content_length)
            self._thread_run_http(thread_num, url, part_size, content_length, file_name, config_file_name, process_bar,
                                  threads)
            self._check_integrity(md5, file_name, config_file_name)
            process_bar.close()
        except Exception as e:
            print(e)
            sys.exit(0)

    def _thread_run_http(self, thread_num, url, part_size, content_length, file_name, config_file_name, process_bar,
                         threads):
        """
        create and manage http(s) downloading threads.
        :param thread_num:
        :param url:
        :param part_size:
        :param content_length:
        :param file_name:
        :param config_file_name:
        :param process_bar:
        :return:
        """
        for i in range(thread_num):
            if i == thread_num - 1:
                thread = HttpDlr(i, url, i * part_size, int(content_length) - 1, self.path, file_name, config_file_name,
                                 self.display_lock, process_bar=process_bar)
            else:
                thread = HttpDlr(i, url, i * part_size, (i + 1) * part_size - 1, self.path, file_name, config_file_name,
                                 self.display_lock, process_bar=process_bar)
            thread.setDaemon(True)
            threads.append(thread)
            thread.start()
        # wait until all threads finished.
        for t in threads:
            t.join()

    def _check_file(self, file_name, content_length):
        """
        check if current file is valid or not.
        :param file_name:
        :param content_length:
        :return:
        """
        if not os.path.exists(self.path + file_name) or os.path.getsize(self.path + file_name) == 0:
            self._construct_file_empty(file_name, content_length)

    def _check_config_file(self, url, config_file_name, file_name, thread_num, content_length, etag):
        """
        check if current config file is valid or not.
        :param url:
        :param config_file_name:
        :param file_name:
        :param thread_num:
        :param content_length:
        :param etag:
        :return:
        """
        if not os.path.exists(self.path + config_file_name) or os.path.getsize(self.path + config_file_name) == 0:
            self._construct_config_file(url, config_file_name, thread_num, content_length, etag)
        else:
            with open(self.path+config_file_name, 'r') as config_file:
                json_data = json.load(config_file)
                # check ETag, if different, means the file has been changed. Re-download the full file.
                if json_data['ETag'] != etag:
                    self._construct_config_file(url, config_file_name, thread_num, content_length, etag)
                    self._construct_file_empty(file_name, content_length)

    def _construct_file_empty(self, file_name, content_length):
        """
        occupy enough space at the beginning to avoid errors like space insufficient during downloading.
        :param file_name:
        :param content_length:
        :return:
        """
        try:
            file = open(self.path + file_name, 'wb')
            file.seek(int(content_length) - 1)
            file.write(b'\x00')
            file.close()
        except IOError as e:
            print(e)
            print('There maybe insufficient space on the disk.')
            sys.exit(0)

    def _construct_config_file(self, url, config_file_name, thread_num, content_length, etag):
        """
        config file is a necessary and key file for recording downloading status.
        It contains some info as follow and will be deleted automatically after fully downloading.
        :param url:
        :param config_file_name:
        :param thread_num:
        :param content_length:
        :param etag: used for checking modifying time.
        :return:
        """
        config_data = {
            'url': url,
            'thread_num': thread_num,
            'size': int(content_length),
            'ETag': etag,
            'offset': {}
        }
        for i in range(thread_num):
            config_data['offset'][i] = i * (int(content_length) // thread_num)
        try:
            config_file = open(self.path + config_file_name, 'w')
            json.dump(config_data, config_file)
            config_file.close()
        except IOError as e:
            print(e)
            print('Something wrong happened when creating config file.')
            sys.exit(0)

    def _get_download_file_info_http(self, url):
        """
        get some necessary info of the downloaded file, http(s) protocol downloader.
        :param url:
        :return:
        """
        with requests.get(url, stream=True) as req:
            content_length = int(req.headers['Content-Length'])
            etag = req.headers['ETag']
            try:
                md5 = req.headers['Content-MD5']
            except KeyError as e:
                md5 = ''
        return [content_length, etag, md5]

    def _delete_file(self, file_name, config_file_name):
        """
        delete the existing file forcibly.
        :param file_name:
        :param config_file_name:
        :return:
        """
        if os.path.exists(self.path + file_name):
            os.remove(self.path + file_name)
        if os.path.exists(self.path + config_file_name):
            os.remove(self.path + config_file_name)

    def _count_thread_num(self, content_length):
        """
        decide how many threads to use fixedly.
        :param content_length:
        :return:
        """
        if content_length < 10*1024*1024:
            return 1
        elif content_length < 100*1024*1024:
            return 3
        else:
            return 5

    def _check_integrity(self, md5, file_name, config_file_name):
        """
        check if the file is integrated or not in the end.
        :param md5:
        :param file_name:
        :param config_file_name:
        :return:
        """
        if md5 != '':
            local_md5 = hashlib.md5(open(self.path + file_name, 'rb').read()).hexdigest()
            if local_md5 == md5:
                if os.path.exists(self.path + config_file_name):
                    os.remove(self.path + config_file_name)
            else:
                md5 = ''  # do nothing
        else:
            with open(self.path+config_file_name, 'r') as config_file:
                json_data = json.load(config_file)
                thread_num = json_data['thread_num']
                content_length = json_data['size']
                part_size = content_length // thread_num
                for i in range(thread_num):
                    if not json_data['offset'][f'{i}'] in [part_size*(i+1), content_length]:
                        return
                if os.path.exists(self.path+config_file_name):
                    os.remove(self.path+config_file_name)
