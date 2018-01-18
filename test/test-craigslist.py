import unittest
from pathlib import Path

from archivebot import craigslist
from archivebot.craigslist import InvalidIdException, InvalidImagePathException


class TestIdScraper(unittest.TestCase):
	def test_IdFromUrl_GivenUrl_ReturnsId(self):
		url = 'https://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		self.assertEqual(craigslist.id_from_url(url), '6451661128')

	def test_IdFromUrl_GivenInvalidUrl_ThrowsError(self):
		url = 'https://indianapolis.craigslist.org/bar/d/bears/645166112.html'
		with self.assertRaises(InvalidIdException):
			craigslist.id_from_url(url)


class TestCraigslistAd(unittest.TestCase):
	def setUp(self):
		self.remote_images = [
			'https://images.craigslist.org/00303_hvg2dCTqGMm_600x450.jpg',
			'https://images.craigslist.org/00d0d_faugXYQcX9f_600x450.jpg',
			'https://images.craigslist.org/00d0d_ftW9aoMNni1_600x450.jpg',
			]
		self.local_images = [
			'/tmp/00303_hvg2dCTqGMm_600x450.jpg',
			'/tmp/00d0d_faugXYQcX9f_600x450.jpg',
			'/tmp/00d0d_ftW9aoMNni1_600x450.jpg',
			]

	def test_CraigslistAd_GivenNoImages_ReturnsAdInstance(self):
		ad = craigslist.CraigslistAd('1234567890', 'a_url', 'body_text')
		self.assertEqual(ad.post_id, '1234567890')
		self.assertEqual(ad.url, 'a_url')
		self.assertEqual(ad.body, 'body_text')
		self.assertEqual(len(ad.images), 0)

	def test_CraigslistAd_GivenImages_ReturnsAdInstance(self):
		ad = craigslist.CraigslistAd(
			'1234567890', 'a_url',
			'body_text', images=self.remote_images
			)
		self.assertEqual(ad.post_id, '1234567890')
		self.assertEqual(ad.url, 'a_url')
		self.assertEqual(ad.body, 'body_text')
		self.assertEqual(len(ad.images), 3)

	def test_CraigslistAd_GivenLocalImages_RaisesError(self):
		with self.assertRaises(InvalidImagePathException):
			craigslist.CraigslistAd(
				'1234567890', 'a_url',
				'body_text', images=self.local_images
				)

	def test_AdCache_GivenImages_ReturnsAdInstance(self):
		ad = craigslist.AdCache(
			'1234567890', 'a_url',
			'body_text', images=self.local_images
			)
		self.assertEqual(ad.post_id, '1234567890')
		self.assertEqual(ad.url, 'a_url')
		self.assertEqual(ad.body, 'body_text')
		self.assertEqual(len(ad.images), 3)

	def test_AdCache_GivenRemoteImages_RaisesError(self):
		with self.assertRaises(InvalidImagePathException):
			craigslist.AdCache(
				'1234567890', 'a_url',
				'body_text', images=self.remote_images
				)


class TestPageScraper(unittest.TestCase):
	"""
	Test that the craigslist post page is scraped correctly.

	There are several saved documents corresponding to the html source of
	conditions that can be found in a post (no images, only one image, etc.)
	They are located in [...]/test/test_data/cl-*.html
	"""
	def setUp(self):
		self.data_dir = Path(__file__).parent / 'test_data'

	def _read_test_file(self, fp):
		with open(fp, 'r') as f:
			return f.read()

	def test_ScrapePage_GivenPage_ScrapesPostId(self):
		source = self._read_test_file(self.data_dir / 'cl-html-multiple-images.html')
		ad = craigslist.scrape_page(source)
		self.assertEqual(ad.post_id, '6451661128')

	def test_ScrapePage_GivenPage_ScrapesUrl(self):
		source = self._read_test_file(self.data_dir / 'cl-html-multiple-images.html')
		ad = craigslist.scrape_page(source)
		url = 'https://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		self.assertEqual(ad.url, url)

	def test_ScrapePage_GivenPage_ScrapesBody(self):
		source = self._read_test_file(self.data_dir / 'cl-html-multiple-images.html')
		ad = craigslist.scrape_page(source)
		partial_text = 'Asking 200 cash value'
		self.assertIn(partial_text, ad.body)

	def test_ScrapePage_GivenLongBody_ScrapesWholeBody(self):
		source = self._read_test_file(self.data_dir / 'cl-html-single-formatted-html.html')
		ad = craigslist.scrape_page(source)
		partial_text = 'a Luxe Living Apartment Community'
		self.assertIn(partial_text, ad.body)

	def test_ScrapePage_GivenFormattedBody_ConvertsBodyToMarkdown(self):
		source = self._read_test_file(self.data_dir / 'cl-html-single-formatted-html.html')
		ad = craigslist.scrape_page(source)
		self.assertIn('**Features**', ad.body)
		self.assertNotIn('<p>', ad.body)
		self.assertNotIn('<br>', ad.body)

	def test_ScrapePage_GivenMultipleImages_ScrapesAllImages(self):
		source = self._read_test_file(self.data_dir / 'cl-html-multiple-images.html')
		ad = craigslist.scrape_page(source)
		self.assertEqual(len(ad.images), 5)

	def test_ScrapePage_GivenSingleImage_ScrapesImage(self):
		source = self._read_test_file(self.data_dir / 'cl-html-single-image.html')
		ad = craigslist.scrape_page(source)
		self.assertEqual(len(ad.images), 1)

	def test_ScrapePage_GivenNoImages_ReturnsNoImages(self):
		source = self._read_test_file(self.data_dir / 'cl-html-no-images.html')
		ad = craigslist.scrape_page(source)
		self.assertEqual(len(ad.images), 0)


if __name__ == '__main__':
	unittest.main()
