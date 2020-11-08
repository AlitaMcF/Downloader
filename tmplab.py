"""
this file just for testing some code.
"""

import requests
import time
import os
import threading
import json
import fcntl
import time
from time import sleep
from tqdm import tqdm
import _thread


# thread_num = 5
# threads = []
# url = 'https://cdn.pixabay.com/photo/2020/05/24/06/54/dumbo-5212670__480.jpg'
# path = '/Users/shaun/Mixture/Project/Python/InternetProtocol/Downloader/data/'
# file_name = url.split('/')[-1]
# config_file_name = file_name + '_config.json'
#
# # get some info of downloading file
# with requests.get(url, stream=True) as req:
#     content_length = req.headers['Content-Length']
#
# # create a file as large as content_length to occupy storage.
# if not os.path.exists(path+file_name):
#     try:
#         file = open(path+file_name, 'rb+')
#         file.seek(int(content_length)-1)
#         file.write(b'\x00')
#     except IOError as e:
#         print(e)
#         print('The storage maybe insufficient.')
#         os._exit(0)
#     finally:
#         file.close()
#
# with open(path+file_name, 'rb+') as f:
#     f.seek(0)
#     f.write(b'\xaa')


# # multi-thread
# class HttpDlr (threading.Thread):
#     def __init__(self, thread_id, url, range_start, range_end, store_path, file_name, config_file_name, chunk_size=1024,
#                  config_file_update_freq=5):
#         threading.Thread.__init__(self)
#         self.thread_id = thread_id
#         self.url = url
#         self.range_start = range_start
#         self.range_end = range_end
#         self.store_path = store_path
#         self.file_name = file_name
#         self.config_file_name = config_file_name
#         self.chunk_size = chunk_size
#         self.config_file_update_freq = config_file_update_freq
#
#     def run(self):
#         # with open(self.store_path+self.file_name, 'ab+') as file:
#             # fcntl.lockf(file, fcntl.LOCK_EX, self.range_end - self.range_start + 1, self.range_start)
#             # with open(self.store_path + self.config_file_name, 'r+') as config_file:
#                 # update json file every count times, reducing json updating frequency
#         count = self.config_file_update_freq
#
#         # require lock here
#         try:
#             config_file_lock.acquire()
#             config_file = open(self.store_path+self.config_file_name, 'r+')
#             config_file.seek(0)
#             json_data = json.load(config_file)
#             config_file.close()
#             config_file_lock.release()
#         except Exception as e:
#             print(e)
#
#         # the offset of current thread in download file, to write the data in correct position.
#         # offset = json_data[f'offset_thread{self.thread_id}']
#         offset = json_data['offset'][f'{self.thread_id}']
#         # if offset > range_end, means this part has been complete download
#         if offset > self.range_end:
#             print('thread', self.thread_id, 'exit.')
#             return
#
#         header = {
#             'Range': f'bytes={offset}-{self.range_end}'
#         }
#         with requests.get(self.url, stream=True, headers=header, timeout=(5, 7)) as req:
#             # req = requests.get(self.url, stream=True, headers=header)
#             for chunk in req.iter_content(chunk_size=self.chunk_size):
#                 if chunk:
#                     try:
#                         # the file lock will be release when file is closing.
#                         file_lock.acquire()
#                         file = open(self.store_path+self.file_name, 'rb+')
#                         file.seek(offset)
#                         file.write(chunk)
#                         file.close()
#                         file_lock.release()
#                     except Exception as e:
#                         print(e)
#                     offset += len(chunk)
#                     count -= 1
#                     # update offset of current thread to json file.
#                     if count == 0:
#                         try:
#                             # require lock here
#                             config_file_lock.acquire()
#                             config_file = open(self.store_path+self.config_file_name, 'r+')
#                             config_file.seek(0)
#                             json_data = json.load(config_file)
#                             json_data['offset'][f'{self.thread_id}'] = offset
#                             config_file.seek(0)
#                             config_file.truncate()
#                             json.dump(json_data, config_file)
#                             config_file.close()
#                             config_file_lock.release()
#                             count = self.config_file_update_freq
#                         except Exception as e:
#                             print(e)
#
#
#
#         # no matter what, update the offset to json file
#         # require lock
#         try:
#             config_file_lock.acquire()
#             config_file = open(self.store_path+self.config_file_name, 'r+')
#             config_file.seek(0)
#             json_data = json.load(config_file)
#             json_data['offset'][f'{self.thread_id}'] = offset
#             config_file.seek(0)
#             config_file.truncate()
#             json.dump(json_data, config_file)
#             config_file.close()
#             config_file_lock.release()
#         except Exception as e:
#             print(e)
#
#         print('thread', self.thread_id, 'exit.')
#
#
# if __name__ == '__main__':
#     thread_num = 5
#     threads = []
#     config_file_lock = threading.Lock()
#     file_lock = threading.Lock()
#     url = 'https://cdn.pixabay.com/photo/2020/05/24/06/54/dumbo-5212670__480.jpg'
#     path = '/Users/shaun/Mixture/Project/Python/InternetProtocol/Downloader/data/'
#     file_name = url.split('/')[-1]
#     config_file_name = file_name + '_config.json'
#
#     if os.path.exists(path+file_name):
#         os.remove(path+file_name)
#     if os.path.exists(path+config_file_name):
#         os.remove(path+config_file_name)
#
#     # get some info of downloading file
#     with requests.get(url, stream=True) as req:
#         content_length = req.headers['Content-Length']
#         '''
#         todo: check file already has been modified or not if we have downloaded some parts before, use ETag
#         '''
#     # the size of each partition
#     part_size = int(content_length) // thread_num
#
#     if not os.path.exists(path+config_file_name) or os.path.getsize(path+config_file_name) == 0:
#         # construct json config file
#         config_data = {
#             'url': url,
#             'thread_num': thread_num,
#             'size': int(content_length),
#             'offset': {}
#         }
#         for i in range(thread_num):
#             config_data['offset'][i] = i*part_size
#         try:
#             config_file = open(path+config_file_name, 'w')
#             json.dump(config_data, config_file)
#             config_file.close()
#         except IOError as e:
#             print(e)
#             print('Something wrong happened when creating config file.')
#             os._exit(0)
#
#     # create a file as large as content_length to occupy storage.
#     if not os.path.exists(path+file_name) or os.path.getsize(path+file_name) == 0:
#         try:
#             file = open(path+file_name, 'wb')
#             file.seek(int(content_length)-1)
#             file.write(b'\x00')
#             file.close()
#         except IOError as e:
#             print(e)
#             print('The storage maybe insufficient.')
#             os._exit(0)
#
#     for i in range(thread_num):
#         if i == thread_num-1:
#             thread = HttpDlr(i, url, i * part_size, int(content_length)-1, path, file_name, config_file_name)
#         else:
#             thread = HttpDlr(i, url, i*part_size, (i+1)*part_size-1, path, file_name, config_file_name)
#         thread.setDaemon(True)
#         threads.append(thread)
#         thread.start()
#
#     # wait until all threads finished.
#     for t in threads:
#         t.join()
#     if os.path.getsize(path+file_name) == int(content_length):
#         print('Downloaded successfully.')
#     else:
#         print('Download failed.')


# aa = 'HtTps'
# if aa.lower() in ['http', 'https']:
#     print('yes')

#
# path = './data/'
# file_name = 'doit.jpg'
# with open(path+file_name, 'w') as f:
#     f.write('x00')

# url = 'https://cdn.pixabay.com/photo/2020/05/24/06/54/dumbo-5212670__480.jpg'
# with requests.get(url, stream=True) as req:
#     content_length = req.headers['Content-Length']
#     ETag = req.headers['ETag']
#     try:
#         md5 = req.headers['Content-MD5']
#     except KeyError as e:
#         md5 = ''
# print(md5)

# from tqdm import trange, tqdm
#
# for i in trange(100):
#     time.sleep(0.1)
#
# with tqdm(total=100) as pbar:
#     for i in range(10):
#         sleep(0.1)
#         pbar.update(10)

# response = requests.get(eg_link, stream=True)
# with open(eg_out, "wb") as fout:
#     with tqdm(
#         # all optional kwargs
#         unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
#         desc=eg_file, total=int(response.headers.get('content-length', 0))
#     ) as pbar:
#         for chunk in response.iter_content(chunk_size=4096):
#             fout.write(chunk)
#             pbar.update(len(chunk))


# i = ['fa', 'fdf', 'rere']
# b = ['fer', 20, 3]
# infos = []
# infos.append(i)
# infos.append(b)
# print(infos)
# for i in infos:
#     print(i[0], i[1], i[2])

def display_pbar(x):
    with tqdm(total=1000*x) as pbar:
        for i in range(1000):
            sleep(0.1)
            pbar.update(1)


_thread.start_new_thread(display_pbar, (1,))
_thread.start_new_thread(display_pbar, (10,))


with tqdm(total=100) as pbar:
    for i in range(10):
        pbar.update(10)