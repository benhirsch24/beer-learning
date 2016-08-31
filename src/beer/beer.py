from bs4 import BeautifulSoup
import urllib2
import collections
import os
import numpy

class Beer:
    def __init__(self, data_dir):
        self.name = ''
        self.file_name = ''
        self.data_dir = data_dir
        self.style = ''
        self.fermentables = []
        self.hops = []
        self.yeasts = []

    def file_name(self):
        return os.path.join(self.data_dir)

    def parse_from_url(self, url):
        self.name = url.split('/')[-1]
        file_name = self.file_name(beer_name)
        html = urllib2.urlopen(url).read()
        with open(file_name, 'w') as f:
            f.write(html)
        self.parse_from_html(html)

    def parse_from_html(self, html):
