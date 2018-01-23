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


if __name__ == '__main__':
	unittest.main()
