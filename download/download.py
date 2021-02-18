import os
import random
from hashlib import md5
from typing import Union
import ffmpy3
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, \
    QTextBrowser, QGridLayout, QMessageBox
from PyQt5.QtGui import QIcon
import sys
import requests
import time
from fake_useragent import UserAgent
from lxml import etree

import ico


class Download(QWidget):
    label_a: Union[QLabel, QLabel]
    text_browser: Union[QTextBrowser, QTextBrowser]
    btn_clear: Union[QPushButton, QPushButton]
    btn_download: Union[QPushButton, QPushButton]
    line_edit_string: Union[QLineEdit, QLineEdit]
    label_info: Union[QLabel, QLabel]

    def __init__(self):
        super(Download, self).__init__()
        self.initUI()
        self.timeout = 10
        self.btn_download.clicked.connect(lambda: self.process(self.btn_download))
        self.btn_clear.clicked.connect(lambda: self.process(self.btn_clear))

    def initUI(self):
        self.setWindowTitle('下载器')
        self.resize(500, 400)
        self.label_info = QLabel('请输入要下载视频的网页地址[点击右侧网站获取]:')
        self.label_a = QLabel('<a href="http://jisudhw.com/">网站</a>')
        # 如果设为True，用浏览器打开网页，如果设为False，调用槽函数
        self.label_a.setOpenExternalLinks(True)
        self.line_edit_string = QLineEdit()
        self.line_edit_string.setPlaceholderText('例如:http://jisudhw.com/?m=vod-detail-id-36616.html')
        self.line_edit_string.setToolTip('请在点击网站后，在该网站中获取网页内容中带有下载地址的网址')
        self.btn_download = QPushButton('下载')
        self.btn_clear = QPushButton('清空')
        self.text_browser = QTextBrowser()

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.label_info, 0, 0, 1, 2)
        grid_layout.addWidget(self.label_a, 0, 2, 1, 1)
        grid_layout.addWidget(self.line_edit_string, 1, 0, 1, 1)
        grid_layout.addWidget(self.btn_download, 1, 1, 1, 1)
        grid_layout.addWidget(self.btn_clear, 1, 2, 1, 1)
        grid_layout.addWidget(self.text_browser, 2, 0, 1, 3)

        self.setLayout(grid_layout)

    def get_html(self, url, encoding):
        headers = {'User-Agent': UserAgent().random}
        res = requests.get(url=url, headers=headers, timeout=self.timeout)
        html = res.content.decode(encoding, 'ignore')
        return html

    @staticmethod
    def xpath_parse(pattern, html):
        parse_html = etree.HTML(html)
        r_list = parse_html.xpath(pattern)
        return r_list

    def text_browser_print(self, string):
        self.text_browser.append(string)
        QApplication.processEvents()

    def save_m3u8(self, m3u8, filename):
        self.text_browser_print(f'<span style="color:blue">{filename}</span>开始下载')
        ffmpy3.FFmpeg(inputs={m3u8: None}, outputs={f'{filename}.mp4': None}).run()
        self.text_browser_print(f'<span style="color:blue">{filename}</span>完成下载')

    def parse_html(self, html):
        title_pattern = '//h2/text()'
        value_pattern = '//ul/li/text()'
        title = self.xpath_parse(title_pattern, html)[0]
        values = self.xpath_parse(value_pattern, html)
        dir_path = f'download/{title}/'
        if not os.path.exists(dir_path):
            self.text_browser_print(f'正在创建文件夹<b style="color:red">{dir_path}</b>')
            os.makedirs(dir_path)
        else:
            self.text_browser_print(f'文件夹<b style="color:red">{dir_path}</b>已存在')
        m3u8_value = []
        for value in values:
            if 'm3u8' in value:
                m3u8_value.append(value)
        if len(m3u8_value) == 0:
            QMessageBox.warning(
                self,
                '错误',
                f'xpath匹配异常:len(m3u8_value)值为{len(m3u8_value)}')
            return
        elif len(m3u8_value) == 1:
            filename = dir_path + f'{title}-{m3u8_value[0].split("$")[0]}.mp4'
            self.save_m3u8(m3u8_value[0].split("$")[-1], filename)
        else:
            for m3u8 in m3u8_value:
                filename = dir_path + f'{title}-{m3u8.split("$")[0]}.mp4'
                self.save_m3u8(m3u8.split("$")[-1], filename)

    def process(self, btn):
        if btn.text() == '下载':
            if not self.line_edit_string.text():
                QMessageBox.warning(
                    self,
                    '错误',
                    '请输入要下载视频的网页地址')
                return
            url = self.line_edit_string.text()
            try:
                html = self.get_html(url, 'utf-8')
                self.parse_html(html)

            except Exception as e:
                QMessageBox.warning(
                    self,
                    '错误',
                    f'未知异常:{e}')
                return
        elif btn.text() == '清空':
            self.text_browser.clear()
            self.line_edit_string.clear()
        else:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ico.base642image('download.ico', ico.ICO)
    app.setWindowIcon(QIcon('download.ico'))
    d = Download()
    d.show()
    os.remove('download.ico')
    sys.exit(app.exec_())
