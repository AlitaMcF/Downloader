from downloader import Downloader


if __name__ == '__main__':
    url_list = ['https://cdn.pixabay.com/photo/2020/05/24/06/54/dumbo-5212670__480.jpg',
                'https://download.jetbrains.8686c.com/cpp/CLion-2020.2.4.dmg',
                'https://download.jetbrains.8686c.com/idea/ideaIC-2020.2.3.dmg']
    downloader = Downloader(url_list)
    downloader.launch()
