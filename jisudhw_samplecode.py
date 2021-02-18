import os
import requests
from bs4 import BeautifulSoup
import time
import random
import sys
from retrying import retry
from fake_useragent import UserAgent
import ffmpy3
from lxml import etree


class OkzywSpider(object):
    def __init__(self):
        self.url = 'http://jisudhw.com/?m=vod-detail-id-66866.html'
        self.timeout = 3

    def get_html(self, url, encoding):
        headers = {'User-Agent': UserAgent().random}
        res = requests.get(url=url, headers=headers, timeout=self.timeout)
        html = res.content.decode(encoding, 'ignore')
        return html

    @staticmethod
    def bs4_parse(html):
        soup = BeautifulSoup(html, 'lxml')
        return soup

    @staticmethod
    def xpath_parse(pattern, html):
        parse_html = etree.HTML(html)
        r_list = parse_html.xpath(pattern)
        return r_list

    def parse_html(self, html):
        soup = self.bs4_parse(html)
        title = self.xpath_parse('//h2/text()', html)[0]
        if not os.path.exists(title):
            print(f'创建目录{title}')
            os.makedirs(title)
        for video_url in soup.find_all('input'):
            if 'm3u8' in video_url.get('value'):
                filename = os.path.join(title, video_url.get('value').split('/')[3])
                print(f'{filename}.mp4 开始下载')
                ffmpy3.FFmpeg(inputs={video_url.get('value'): None}, outputs={f'{filename}.mp4': None}).run()
                print(f'{filename}.mp4 完成下载')

    def run(self):
        html = self.get_html(self.url, 'utf-8')
        self.parse_html(html)


if __name__ == '__main__':
    start = time.time()
    oks = OkzywSpider()
    oks.run()
    end = time.time()
    print('耗时:%.2f' % (end - start))
