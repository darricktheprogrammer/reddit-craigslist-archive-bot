import unittest

from archivebot import craigslist
from archivebot.craigslist import InvalidIdException, InvalidImagePathException


# TODO
# test scraping data


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


class TestUrlScraper2(unittest.TestCase):
	"""
	There will usually only be one craigslist url, but because there can be
	more than one, `scrape_url` always returns a list.
	"""
	# def test_ScrapeUrl_GivenUrl_ReturnsId(self):
	# 	url = 'https://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
	# 	self.assertEqual(craigslist.id_from_url(url), '6451661128')

	# def test_IdFromUrl_GivenInvalidUrl_ThrowsError(self):
	# 	url = 'https://indianapolis.craigslist.org/bar/d/bears/645166112.html'
	# 	with self.assertRaises(InvalidIdException):
	# 		craigslist.id_from_url(url)
	pass


if __name__ == '__main__':
	unittest.main()
