import os
import time
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import defaultdict


def get_page_from_disk(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    else:
        return None


def get_page_online(url, path=None, sleep_sec=None):
    html = urlopen(url).read().decode('utf-8')
    if path is not None:
        with open(path, 'w') as f:
            f.write(html)
    if sleep_sec is not None:
        time.sleep(sleep_sec)
    return html


def get_page(url, path, sleep_sec=None):
    return get_page_from_disk(path) or get_page_online(url, path, sleep_sec)


class Scraper:
    """ Gets the html page of the episode transcripts """

    def __init__(self, data_dir, episode_index_url):
        self.data_dir = data_dir
        self.episode_index_url = episode_index_url
        # FIXME: should be lazy: no need to download or parse if the wanted episodes are already on disk
        self.url_map = self.get_url_map(episode_index_url)

    def get_url_map(self, episode_index_url):

        def is_episode_code(html_tag):
            # codes are like: '3.06', '5.14'
            p = re.compile('\d\.\d\d')
            return html_tag.name == 'b' and html_tag.string is not None and p.match(html_tag.string) is not None

        path = os.path.join(self.data_dir, 'episode_index.html')
        index_html = get_page(episode_index_url, path)
        soup = BeautifulSoup(index_html, 'html.parser')
        divs = soup.find_all(attrs={'class': 'entryText s2-entrytext'})
        if len(divs) != 1:
            raise ValueError('Error: found {} objects matching the class')
        div = divs[0]
        episode_code_tags = div.find_all(is_episode_code)

        urls = defaultdict(dict)
        for tag in episode_code_tags:
            season_str, episode_str = tag.string.split('.')
            season = int(season_str)
            episode = int(episode_str)
            episode_link = tag.next_sibling.next_sibling.attrs['href']
            season_links = urls[season]
            assert (episode not in season_links)
            season_links[episode] = episode_link
        return urls

    def get_episode(self, season, episode, url=None, sleep_sec=None):
        filename = '{}.{}.html'.format(season, episode)
        path = os.path.join(self.data_dir, filename)
        url = url or self.url_map[season][episode]
        return get_page(url, path, sleep_sec)

    def get_all_episodes(self, sleep_sec=1):
        html_pages = defaultdict(dict)
        for season, episodes in self.url_map.items():
            print('{}...'.format(season), end=' ')
            for episode, url in episodes.items():
                html_pages[season][episode] = self.get_episode(season, episode, url, sleep_sec)
        return html_pages
