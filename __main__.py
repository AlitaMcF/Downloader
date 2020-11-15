from downloader import Downloader


if __name__ == '__main__':
    # url_list = [
    #     #     # 'https://cdn.pixabay.com/photo/2020/05/24/06/54/dumbo-5212670__480.jpg',
    #     #     # 'https://download.jetbrains.8686c.com/cpp/CLion-2020.2.4.dmg',
    #     #     # 'https://download.jetbrains.8686c.com/idea/ideaIC-2020.2.3.dmg',
    #     #     'https://www.bilibili.com/video/av19516333/',
    #     #     # 'https://www.bilibili.com/video/BV1hV411a7W9?spm_id_from=333.851.b_7265706f7274466972737431.7',
    #     #     # 'https://www.bilibili.com/video/av46958874/?spm_id_from=333.334.b_63686965665f7265636f6d6d656e64.16'
    #     # ]
    print('Downloader. Supports HTTP, FTP protocols and Bilibili crawler.')
    print('Input your url or list, split by SPACE:')
    raw_url_list = input()
    url_list = raw_url_list.split(' ')
    print(url_list)
    downloader = Downloader(url_list)
    downloader.launch()
