import unittest

from archivebot import bot


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


if __name__ == '__main__':
	unittest.main()