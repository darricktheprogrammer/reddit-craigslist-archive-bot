import unittest

from archivebot.custommodels import Archive, CraigslistAd, AdCache
from archivebot.errors import InvalidImagePathException


class TestArchive(unittest.TestCase):
	def test_Archive_GivenNoImagesThenUpdated_AllowsEmptyImagesInFuture(self):
		# This is to test that the lambda works as a default, and does not
		# retain reference to the same list in future objects.
		archive_images = [
			'https://i.imgur.com/abcd001.jpg',
			'https://i.imgur.com/abcd002.jpg',
			'https://i.imgur.com/abcd003.jpg'
			]
		archive = Archive(
			url='https://imgur.com/a/zzzz1', title='xxx',
			ad='', screenshot='https://i.imgur.com/abcd000.jpg')
		archive.images = archive_images
		archive2 = Archive(
			url='https://imgur.com/a/zzzz2', title='xxx',
			ad='', screenshot='https://i.imgur.com/abcd001.jpg')
		self.assertEqual(len(archive2.images), 0)


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

	def test_CraigslistAd_UpdatingToLocalImages_ThrowsError(self):
		ad = CraigslistAd(
			title='', post_id='', url='',
			body='', images=self.remote_images)
		with self.assertRaises(InvalidImagePathException):
			ad.images = self.local_images

	def test_CraigslistAd_UpdatingToRemoteImages_ValidatesImages(self):
		ad = CraigslistAd(title='', post_id='', url='', body='')
		ad.images = self.remote_images

	def test_AdCache_UpdatingToRemoteImages_ThrowsError(self):
		ad = AdCache(
			title='', post_id='', url='',
			body='', images=self.local_images)
		with self.assertRaises(InvalidImagePathException):
			ad.images = self.remote_images

	def test_AdCache_UpdatingToLocalImages_ValidatesImages(self):
		ad = AdCache(title='', post_id='', url='', body='')
		ad.images = self.local_images


if __name__ == '__main__':
	unittest.main()
