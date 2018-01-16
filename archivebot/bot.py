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
