import unittest
import logging
from copy import deepcopy
from unittest.mock import Mock

from archivebot import bot, custommodels


# disable application logging during tests
logging.disable(logging.CRITICAL)


class TestExtraction(unittest.TestCase):
	"""
	There will usually only be one craigslist url, but because there can be
	more than one, `scrape_url` always returns a list.
	"""
	def setUp(self):
		self.body = '''
		My fiancé and I are desperately trying to find an apartment. Of course we found one of [Craigslist](%url%) for an amazing price. We assumed it was priced the way it was because it was furnished. They said they would mail the keys to us, after we make a payment. I said to them no, that we would like to view the apartment, and if anything would be mailed to us, it should be the lease agreement. That we could wait for the keys, and don’t want to send money just to view a space.
		My dilemma is I have given them my name, date of birth and address. I even sent a picture of my fiancé and myself because they sent a photo of their “family”.
		In fact another “landlord” said he was also overseas and the situations were similar, so I thought “Oh, people must do this all the time. We are in an age of internet and communications. You don’t need to meet in person anymore!”
		I didn’t think anything of it, until they responded to my message insisting that we trust one another.
		After that I told them I would have to decline their offer.
		The other situation, someone actually called me explaining the details of the property, and what I could expect. They also said they would call to speak to me further. It was the landlords realtor representative. However again, they expect me to send money.
		Can they do anything with my information?
		I’ve already received notifications in my e-mail that someone tried to sign in my paypal.
		I provided first and last name, Date of birth Phone number Address
		My paypal is not updated with my current phone number. Which is why I think they couldn’t get in.
		%url2%'''

	def test_ExtractUrls_GivenFullUrl_ReturnsUrl(self):
		url = 'https://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 1)

	def test_ExtractUrls_GivenFullUrlWithOnlyHTTP_ReturnsUrl(self):
		url = 'http://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 1)

	def test_ExtractUrls_GivenMultipleUrls_ReturnsMultipleUrls(self):
		url = 'http://indianapolis.craigslist.org/bar/d/bears/6451661128.html'
		url2 = 'https://dallas.craigslist.org/ftw/zip/d/20000-pounds-free-remotes/6426178725.html'
		text = self.body.replace('%url%', url)
		text = text.replace('%url2%', url)
		self.assertEqual(len(bot.extract_urls(text)), 2)

	def test_ExtractUrls_GivenForumUrl_ReturnsEmptyList(self):
		url = 'https://forums.craigslist.org/?forumID=3'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenCraigslistScamsPage_ReturnsEmptyList(self):
		url = 'https://www.craigslist.org/about/scams'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenCraigslistScamsPageWithRegularHTTP_ReturnsEmptyList(self):
		url = 'http://www.craigslist.org/about/scams'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenCraigslistSearchPage_ReturnsEmptyList(self):
		url = 'https://tampa.craigslist.org/d/for-sale/search/sss'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenCraigslistTermsPage_ReturnsEmptyList(self):
		url = 'https://www.craigslist.org/about/terms.of.use'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenNonCraigslistPage_ReturnsEmptyList(self):
		url = 'https://www.google.com'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)

	def test_ExtractUrls_GivenNonCraigslistPageEndingWithHtml_ReturnsEmptyList(self):
		url = 'https://www.google.com/about.html'
		text = self.body.replace('%url%', url)
		self.assertEqual(len(bot.extract_urls(text)), 0)


class TestBot(unittest.TestCase):
	def setUp(self):
		self.mock_submission = Mock(selftext='abc', comment_sort='', url='')
		self.mock_comment = Mock(body='xyz')
		self.mock_submission.reply = Mock(return_value=None)
		self.mock_comment.reply = Mock(return_value=None)

	def test_RedditPost_GivenSubmission_PullsTextFromSelftext(self):
		post = bot.RedditPost(self.mock_submission)
		self.assertEqual(post.text, self.mock_submission.selftext)

	def test_RedditPost_GivenComment_PullsTextFromBody(self):
		post = bot.RedditPost(self.mock_comment)
		self.assertEqual(post.text, self.mock_comment.body)

	def test_RedditPost_ReplyToSubmission_CallsPrawReply(self):
		post = bot.RedditPost(self.mock_submission)
		post.reply('')
		self.mock_submission.reply.assert_called()

	def test_RedditPost_ReplyToComment_CallsPrawReply(self):
		post = bot.RedditPost(self.mock_comment)
		post.reply('')
		self.mock_comment.reply.assert_called()


class TestPageRequest(unittest.TestCase):
	def setUp(self):
		self.url = 'http://indianapolis.craigslist.org/bar/d/bears/6451661128.html'

	def test_RequestPage_GivenValidUrl_ReturnsTextOfPage(self):
		response = Mock(ok=True, text='<html source>')
		with unittest.mock.patch('archivebot.bot.requests.get') as patch:
			patch.return_value = response
			self.assertEqual('<html source>', bot.request_page(self.url))

	def test_RequestPage_GivenInvalidUrl_RaisesError(self):
		response = Mock(status_code=404, ok=False)
		with unittest.mock.patch('archivebot.bot.requests.get') as patch:
			patch.return_value = response
			with self.assertRaises(bot.PageNotFoundError):
				bot.request_page(self.url)

	def test_RequestPage_ServerError_RaisesError(self):
		response = Mock(status_code=500, ok=False)
		with unittest.mock.patch('archivebot.bot.requests.get') as patch:
			patch.return_value = response
			with self.assertRaises(bot.PageUnavailableError):
				bot.request_page(self.url)


class TestFormat(unittest.TestCase):
	def setUp(self):
		images = [
			'https://i.imgur.com/abcd001.jpg',
			'https://i.imgur.com/abcd002.jpg',
			'https://i.imgur.com/abcd003.jpg'
			]
		self.ad = custommodels.CraigslistAd(
			title='Post title',
			body='Post description line 1.\n\nPost description line 2.',
			url='http://indianapolis.craigslist.org/bar/d/bears/6451661128.html',
			)
		self.archive = custommodels.Archive(
			url='https://imgur.com/a/zzzz1', title='xxx',
			ad=self.ad, screenshot='https://i.imgur.com/abcd000.jpg',
			images=images)

	def test_Formatter_GivenArchive_FormatsTitle(self):
		formatter = bot.PostFormatter()
		self.assertIn('### Post title ###', formatter.format(self.archive))

	def test_Formatter_GivenArchive_FormatsTitleAsQuote(self):
		formatter = bot.PostFormatter()
		self.assertIn('> ### Post title ###', formatter.format(self.archive))

	def test_Formatter_GivenOriginalPost_FormatsOriginalPost(self):
		formatter = bot.PostFormatter()
		linktext = '[original post](http://indianapolis.craigslist.org/bar/d/bears/6451661128.html)'
		self.assertIn(linktext, formatter.format(self.archive))

	def test_Formatter_GivenAlbumUrl_FormatsAlbumUrl(self):
		formatter = bot.PostFormatter()
		linktext = '[imgur album](https://imgur.com/a/zzzz1)'
		self.assertIn(linktext, formatter.format(self.archive))

	def test_Formatter_GivenScreenshot_FormatsScreenshot(self):
		formatter = bot.PostFormatter()
		linktext = '[screenshot](https://i.imgur.com/abcd000.jpg)'
		self.assertIn(linktext, formatter.format(self.archive))

	def test_Formatter_GivenAdBody_FormatsAdBody(self):
		formatter = bot.PostFormatter()
		text = 'Post description line 1'
		self.assertIn(text, formatter.format(self.archive))

	def test_Formatter_GivenAdBody_FormatsAdBodyAsQuote(self):
		formatter = bot.PostFormatter()
		text = '> Post description line 1'
		self.assertIn(text, formatter.format(self.archive))

	def test_Formatter_GivenMultiLineAdBody_FormatsAllLinesAsQuote(self):
		formatter = bot.PostFormatter()
		text = '> Post description line 1.\n>\n> Post description line 2.'
		self.assertIn(text, formatter.format(self.archive))

	def test_Formatter_GivenMultipleImages_FormatsImages(self):
		formatter = bot.PostFormatter()
		text = '[image 1](https://i.imgur.com/abcd001.jpg) | [image 2](https://i.imgur.com/abcd002.jpg) | [image 3](https://i.imgur.com/abcd003.jpg)'
		self.assertIn(text, formatter.format(self.archive))

	def test_Formatter_GivenImage_FormatsImagesAsQuote(self):
		formatter = bot.PostFormatter()
		a = deepcopy(self.archive)
		a.images = a.images[:1]
		text = '> [image 1](https://i.imgur.com/abcd001.jpg)'
		self.assertIn(text, formatter.format(a))

	def test_Formatter_GivenMultipleImage_FormatsImagesAsQuote(self):
		formatter = bot.PostFormatter()
		text = '> [image 1](https://i.imgur.com/abcd001.jpg) | [image 2](https://i.imgur.com/abcd002.jpg) | [image 3](https://i.imgur.com/abcd003.jpg)'
		self.assertIn(text, formatter.format(self.archive))

	def test_Formatter_GivenNoImages_HasNoTrailingQuoteMarks(self):
		formatter = bot.PostFormatter()
		a = deepcopy(self.archive)
		a.images = []
		self.assertIn('> Post description line 2.\n', formatter.format(a))
		self.assertNotIn('> Post description line 2.\n>', formatter.format(a))

	def test_Formatter_GivenMultipleImages_ReturnsCorrectFullReply(self):
		expected_reply = (
			'This Craigslist post has been archived so it can continue to be viewed after expiration.\n\n'
			'[original post](http://indianapolis.craigslist.org/bar/d/bears/6451661128.html) | [imgur album](https://imgur.com/a/zzzz1) | [screenshot](https://i.imgur.com/abcd000.jpg)\n\n'
			'> ### Post title ###\n'
			'>\n'
			'> Post description line 1.\n'
			'>\n'
			'> Post description line 2.\n'
			'>\n'
			'> [image 1](https://i.imgur.com/abcd001.jpg) | [image 2](https://i.imgur.com/abcd002.jpg) | [image 3](https://i.imgur.com/abcd003.jpg)\n\n'
			'***\n\n'
			'[^github](https://github.com/darricktheprogrammer/reddit-cl-bot) ^| [^send ^message/report](/#)'
			)
		formatter = bot.PostFormatter()
		self.assertEqual(expected_reply, formatter.format(self.archive))

	def test_Formatter_GivenSingleImage_ReturnsCorrectFullReply(self):
		expected_reply = (
			'This Craigslist post has been archived so it can continue to be viewed after expiration.\n\n'
			'[original post](http://indianapolis.craigslist.org/bar/d/bears/6451661128.html) | [imgur album](https://imgur.com/a/zzzz1) | [screenshot](https://i.imgur.com/abcd000.jpg)\n\n'
			'> ### Post title ###\n'
			'>\n'
			'> Post description line 1.\n'
			'>\n'
			'> Post description line 2.\n'
			'>\n'
			'> [image 1](https://i.imgur.com/abcd001.jpg)\n\n'
			'***\n\n'
			'[^github](https://github.com/darricktheprogrammer/reddit-cl-bot) ^| [^send ^message/report](/#)'
			)
		a = deepcopy(self.archive)
		a.images = a.images[:1]
		formatter = bot.PostFormatter()
		self.assertEqual(expected_reply, formatter.format(a))

	def test_Formatter_GivenNoImages_ReturnsCorrectFullReply(self):
		expected_reply = (
			'This Craigslist post has been archived so it can continue to be viewed after expiration.\n\n'
			'[original post](http://indianapolis.craigslist.org/bar/d/bears/6451661128.html) | [imgur album](https://imgur.com/a/zzzz1) | [screenshot](https://i.imgur.com/abcd000.jpg)\n\n'
			'> ### Post title ###\n'
			'>\n'
			'> Post description line 1.\n'
			'>\n'
			'> Post description line 2.\n\n'
			'***\n\n'
			'[^github](https://github.com/darricktheprogrammer/reddit-cl-bot) ^| [^send ^message/report](/#)'
			)
		a = deepcopy(self.archive)
		a.images = []
		formatter = bot.PostFormatter()
		self.assertEqual(expected_reply, formatter.format(a))


if __name__ == '__main__':
	unittest.main()
