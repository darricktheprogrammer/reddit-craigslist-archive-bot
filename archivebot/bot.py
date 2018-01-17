import re


def extract_urls(post):
	"""
	Extract any urls that point to a craigslist post from the text of a post.

	Args:
		txt (String): The text of a post or submission
	Returns:
		List

		0 or more craigslist post urls
	"""
	return re.findall(r'[\w\.:/]+?craigslist.org.+?.*?\.html', post)


class RedditPost(object):
	"""
	Adapter class for submissions and comments.

	Due to the light needs of the archive bot, a lot of the type-specific
	properties can be merged for easier usage within the bot (such as
	`submission.selftext` and `comment.body` can be merged into `post.text`.

	Args:
		post ([praw.models.Submission, praw.models.Comment]):
	"""
	def __init__(self, post):
		super(RedditPost, self).__init__()
		self._original_post = post
		if self._is_submission(post):
			text = self._parse_submission(post)
		else:
			text = self._parse_comment(post)
		self.text = text

	def _parse_submission(self, post):
		return post.selftext

	def _parse_comment(self, post):
		return post.body

	def _is_submission(self, post):
		return 'comment_sort' in vars(post)

	def reply(self, body):
		"""
		Reply to the original post

		Args:
			body (String): Markdown formatted text that serves as the body
				of the comment.
		Returns:
			praw.models.Comment

			A new comment post made in reply to this post.
		"""
		return self._original_post.reply(body)


class Archive(object):
	"""
	Representation of an Imgur album in Archive format.

	Args:
		url (String): The url to the entire Imgur album
		title (String): The title of the Imgur album. It should be something
			along the lines of
			`reddit-cl-bot archive $CraigslistAd.id`
		ad (CraigslistAd, AdCache): The original ad that is being archived
		screenshot (String): Direct url to the Craigslist post screenshot which
			is the first image in the album.
	Kwargs:
		images (List): (optional) A list of direct urls to the images found in
						the Craigslist post.
	Returns:
		Archive
	"""
	def __init__(self, url, title, ad, screenshot, images=None):
		super(Archive, self).__init__()
		self.url = url
		self.title = title
		self.ad = ad
		self.screenshot = screenshot
		self.images = images or []

