from moviepy.editor import *
import requests
import hashlib
import os
import sys
import json
import threading
import imageio
imageio.plugins.ffmpeg.download()


class BilibiliCrawler (threading.Thread):
    """
    can resume from break point.
    """
    def __init__(self, orig_url, cid, quality, title, chunk_size=1024*100):
        threading.Thread.__init__(self)
        self.orig_url = orig_url
        self.cid = cid
        self.quality = quality
        self.title = title
        self.chunk_size = chunk_size
        self.current_video_path = os.path.join(sys.path[0], 'data', self.title)
        self.segment_list = []
        self.process_bar = None
        self.sizes = []
        self.etags = []

    def run(self):
        self._download_video()

    def _get_segment_list(self):
        """
        every video may be divided into several segments.
        :return:
        """
        entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
        appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
        params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, self.cid, self.quality, self.quality)
        checksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
        url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, checksum)
        headers = {
            'Referer': self.orig_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/55.0.2883.87 Safari/537.36'
        }
        respond = requests.get(url_api, headers=headers).json()
        for rpd in respond['durl']:
            self.segment_list.append(rpd['url'])

    def _download_video(self):
        config_file_location = os.path.join(self.current_video_path, f'{self.title}_config.json')
        if not os.path.exists(self.current_video_path):
            os.makedirs(self.current_video_path)
        self._construct_config_file(config_file_location)
        seg_num = 0
        file_location = ''
        for seg_url in self.segment_list:
            # if the current segment has been finished, continue to the next one.
            if self._check_seg_finish(config_file_location, seg_num):
                # update process bar
                self.process_bar.update(self._get_size(config_file_location, seg_num))
                seg_num += 1
                continue
            else:
                # update process bar
                self.process_bar.update(self._get_offset(config_file_location, seg_num))
            file_location = os.path.join(self.current_video_path, f'{self.title}-{seg_num}.flv')
            offset = self._get_offset(config_file_location, seg_num)
            header = self._construct_header(offset)
            resp = requests.get(seg_url, headers=header, stream=True, timeout=(20, 60))
            size = int(resp.headers['Content-Length'])
            if not os.path.exists(file_location):
                self._construct_empty_file(file_location, size)
            with open(file_location, 'rb+') as file:
                for chunk in resp.iter_content(chunk_size=self.chunk_size):
                    file.seek(offset)
                    file.write(chunk)
                    offset += len(chunk)
                    self._update_offset(config_file_location, offset, seg_num)
                    self.process_bar.update(len(chunk))
            seg_num += 1
        self._combine_video(file_location)
        self._delete_config_file(config_file_location)

    def _combine_video(self, last_file_location):
        # if len(self.segment_list) == 1:
        #     os.rename(last_file_location, os.path.join(self.current_video_path, self.title+'.flv'))
        #     return

        def file_filter(f):
            if f.endswith('.flv'):
                return True
            else:
                return False

        # the list of segment video
        video_list = []
        # orderly iterate through all the video segment files
        files = list(filter(file_filter, os.listdir(self.current_video_path)))
        for file in sorted(files, key=lambda x: int(x[x.rindex("-") + 1:x.rindex(".")])):
            # if the postfix is .flv
            if os.path.splitext(file)[1] == '.flv':
                # assemble to full video segment path
                file_path = os.path.join(self.current_video_path, file)
                # load video segment
                video = VideoFileClip(file_path)
                # add to list
                video_list.append(video)
        # joint together
        final_clip = concatenate_videoclips(video_list)
        # generate the final video and write to file system
        final_clip.write_videofile(os.path.join(self.current_video_path, r'{}.mp4'.format(self.title)), fps=30,
                                   remove_temp=True, logger='bar')
        self._delete_flv_files(files)

    def get_segments_info(self):
        self._get_segment_list()
        for seg_url in self.segment_list:
            header = self._construct_header(0)
            resp = requests.get(seg_url, headers=header, stream=True, timeout=(20, 60))
            size = int(resp.headers['Content-Length'])
            # etag = resp.headers['ETag']
            self.sizes.append(size)
            # self.etags.append(etag)
        return [self.sizes, self.etags]

    def _construct_header(self, offset):
        header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Range': f'bytes={offset}-',
            'Referer': self.orig_url,  # necessary
            'Origin': 'https://www.bilibili.com',
            'Connection': 'keep-alive'
        }
        return header

    def _construct_empty_file(self, file_location, size):
        try:
            file = open(file_location, 'wb')
            file.seek(int(size) - 1)
            file.write(b'\x00')
            file.close()
        except IOError as e:
            print(e)
            print('There maybe insufficient space on the disk.')
            sys.exit(0)

    def _construct_config_file(self, config_file_location):
        config_data = {
            'size': self.sizes,
            'etag': self.etags,
            'offset': []
        }
        for i in range(len(self.sizes)):
            config_data['offset'].append(0)
        try:
            config_file = open(config_file_location, 'w')
            json.dump(config_data, config_file)
            config_file.close()
        except IOError as e:
            print(e)
            print('Something wrong happened when creating config file.')
            sys.exit(0)

    def _update_offset(self, config_file_location, offset, seg_num):
        with open(config_file_location, 'r+') as config_file:
            json_data = json.load(config_file)
            json_data['offset'][seg_num] = offset
            config_file.seek(0)
            config_file.truncate()
            config_file.seek(0)
            json.dump(json_data, config_file)

    def _get_offset(self, config_file_location, seg_num):
        with open(config_file_location, 'r+') as config_file:
            json_data = json.load(config_file)
            return json_data['offset'][seg_num]

    def _get_size(self, config_file_location, seg_num):
        with open(config_file_location, 'r+') as config_file:
            json_data = json.load(config_file)
            return json_data['size'][seg_num]

    def _check_seg_finish(self, config_file_location, seg_num):
        offset = self._get_offset(config_file_location, seg_num)
        size = self._get_size(config_file_location, seg_num)
        if offset == size:
            return True
        else:
            return False

    def set_process_bar(self, process_bar):
        self.process_bar = process_bar

    def _delete_config_file(self, config_file_location):
        """
        delete config file after finishing downloading files.
        :param config_file_location:
        :return:
        """
        if os.path.exists(config_file_location):
            os.remove(config_file_location)

    def _delete_flv_files(self, files):
        """
        delete the .flv files after combining into .mp4 file.
        :param files:
        :return:
        """
        for file in files:
            if os.path.exists(os.path.join(self.current_video_path, file)):
                os.remove(os.path.join(self.current_video_path, file))
