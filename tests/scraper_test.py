import unittest

import os

from main.scraper import Scraper


class ScraperTest(unittest.TestCase):

    def test_use_file_on_disk_if_present(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(this_dir, 'resources/')
        episode_index_url = 'url/not/used'
        scraper = Scraper(data_dir, episode_index_url)
        episode = scraper.get_episode(2, 3)
        self.assertEqual(episode, 'some content blah blah')


if __name__ == '__main__':
    unittest.main()
