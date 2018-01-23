"""
Integration testing to make sure saving and querying the db work as expected.

Overall, this is some naive testing, that is targeted toward how I expect the
bot to work. It is not exhaustive, but can be added to as I find other uses
that I was not expecting from the outset.
"""
import unittest

from copy import deepcopy

from archivebot.custommodels import DATABASE, Archive, CraigslistAd


class DatabaseTest(unittest.TestCase):
	"""
	Base class which handles the setup/teardown of all tests involving the database.
	"""
	def setUp(self):
		self.db = DATABASE
		self.db.init(':memory:')
		self.db.connect()
		self.db.create_tables([Archive, CraigslistAd], safe=True)

		self.archive_images = [
			'https://i.imgur.com/abcd001.jpg',
			'https://i.imgur.com/abcd002.jpg',
			'https://i.imgur.com/abcd003.jpg'
			]

		self.ad = CraigslistAd(
			post_id='1234567890',
			body='Post description line 1.\n\nPost description line 2.',
			url='http://indianapolis.craigslist.org/bar/d/bears/6451661128.html',
			)
		self.archive = Archive(
			url='https://imgur.com/a/zzzz1', title='xxx',
			ad=self.ad, screenshot='https://i.imgur.com/abcd000.jpg',
			images=self.archive_images)

	def tearDown(self):
		self.db.close()


class DatabaseIO(DatabaseTest):
	def test_Archive_WhenSaved_SavesToDatabase(self):
		# `save()` returns the number of rows modified
		self.assertEqual(self.archive.save(), 1)

	def test_CraigslistAd_WhenSaved_SavesToDatabase(self):
		# `save()` returns the number of rows modified
		self.assertEqual(self.ad.save(), 1)

	def test_Archive_WhenQueried_ReturnsPopulatedInstance(self):
		self.archive.save()
		ad = CraigslistAd.get(CraigslistAd.post_id == '1234567890')
		archive = Archive.get(Archive.ad == ad)
		self.assertEqual(archive.url, 'https://imgur.com/a/zzzz1')
		self.assertEqual(archive.ad.post_id, '1234567890')
		self.assertEqual(archive.ad.url, 'http://indianapolis.craigslist.org/bar/d/bears/6451661128.html')

	def test_CraigslistAd_IfAdNotFound_ThrowsError(self):
		with self.assertRaises(CraigslistAd.DoesNotExist):
			CraigslistAd.get(CraigslistAd.post_id == '1234567890')

	def test_CraigslistAd_WithImages_ReturnsImagesAsListAfterSaving(self):
		archive = deepcopy(self.archive)
		archive.images = self.archive_images
		archive.save()
		archive_load = Archive.get(Archive.url == 'https://imgur.com/a/zzzz1')
		self.assertEqual(len(archive_load.images), 3)
		self.assertEqual(archive_load.images[0], 'https://i.imgur.com/abcd001.jpg')


if __name__ == '__main__':
	unittest.main()
