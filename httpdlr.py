import requests
import threading
import json
import fcntl
import sys


class HttpDlr (threading.Thread):
    def __init__(self, thread_id, url, range_start, range_end, store_path, file_name, config_file_name, display_lock,
                 process_bar, chunk_size=1024*100, config_file_update_freq=5):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.url = url
        self.range_start = range_start                          # the start of file store range
        self.range_end = range_end                              # the end of file store range
        self.store_path = store_path
        self.file_name = file_name
        self.config_file_name = config_file_name
        self.chunk_size = chunk_size                            # size of every request data
        self.config_file_update_freq = config_file_update_freq  # config file update frequency
        self.offset = 0                                         # file written offset
        self.display_lock = display_lock
        self.process_bar = process_bar                          # display downloading process

    def run(self):
        self.offset = self._get_offset()
        # initiate status of process bar
        self.process_bar.update(self.offset-self.range_start)
        if self.offset > self.range_end:
            sys.exit(0)
        self._get_and_write_data()

    def _get_offset(self):
        """
        get offset from config file
        :return:
        """
        with open(self.store_path+self.config_file_name, 'r+') as config_file:
            fcntl.flock(config_file, fcntl.LOCK_EX)
            json_data = json.load(config_file)
            return json_data['offset'][f'{self.thread_id}']

    def _update_offset(self):
        """
        update offset to config file
        :return:
        """
        with open(self.store_path+self.config_file_name, 'r+') as config_file:
            fcntl.flock(config_file, fcntl.LOCK_EX)
            json_data = json.load(config_file)
            json_data['offset'][f'{self.thread_id}'] = self.offset
            config_file.seek(0)
            config_file.truncate()
            config_file.seek(0)
            json.dump(json_data, config_file)

    def _get_and_write_data(self):
        """
        the main function to download data.
        :return:
        """
        header = {
            'Range': f'bytes={self.offset}-{self.range_end}'
        }
        count = self.config_file_update_freq
        with open(self.store_path+self.file_name, 'rb+') as file:
            # lock file on corresponding range.
            fcntl.lockf(file, fcntl.LOCK_EX, self.range_end - self.range_start + 1, self.range_start)
            try:
                req = requests.get(self.url, stream=True, headers=header, timeout=(20, 60))
                for chunk in req.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        file.seek(self.offset)
                        file.write(chunk)
                        self.offset += len(chunk)
                        # update process bar
                        self.process_bar.update(len(chunk))
                        count -= 1
                        # reduce the json file updating rate.
                        if count == 0:
                            self._update_offset()
                            count = self.config_file_update_freq
            except requests.exceptions.RequestException as e:
                self.display_lock.acquire()
                self.display_lock.release()
                self._resume_get_and_write_data()

            # update config file in the end
            self._update_offset()

    def _resume_get_and_write_data(self):
        """
        resume the http(s) connect to continue downloading when meet connect or read timeout.
        :return:
        """
        self._get_and_write_data()
