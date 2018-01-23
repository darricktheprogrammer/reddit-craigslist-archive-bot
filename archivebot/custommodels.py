import re

from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, TextField

from .errors import InvalidImagePathException


# By using None instead of defining the database, any database settings can be
# defined at runtime.
DATABASE = SqliteDatabase(None)


class ImageListField(CharField):
	"""
	Custom Field type to store a list of images.

	Rather than store and manipulate a string, or create a whole separate
	model just for images, the ImageListField allows for saving the list into
	the database as a string while manipulating a list of strings in python.

	See http://docs.peewee-orm.com/en/latest/peewee/models.html#creating-a-custom-field
	for more information on peewee custom fields.
	"""
	def db_value(self, value):
		return '%%'.join(value)

	def python_value(self, value):
		return value.split('%%')


class CustomModel(Model):
	"""
	Base peewee subclass for defining the database.

	See  http://docs.peewee-orm.com/en/latest/peewee/models.html#models-and-fields
	for peewee's recommended usage.
	"""
	class Meta:
		database = DATABASE


class BaseCraigslistAd(CustomModel):
	"""
	Represents a Craigslist ad and all of its components

	Args:
		title (String): The title of the post
		post_id (String): The id of the post as found in the url and in the
			`post id` section at the bottom of the page.
		url (String):
		body (String):
	Kwargs:
		images (List): A list of images found in the page.
	"""
	# Match anything. Let subclasses worry about their own matching.
	image_path_regex = '.*'
	title = CharField()
	post_id = CharField(index=True, max_length=10)
	url = CharField()
	body = TextField()
	_images = ImageListField(default=lambda: [], db_column='images')

	def __init__(self, *args, **kwargs):
		super(BaseCraigslistAd, self).__init__(*args, **kwargs)
		for image in self.images:
			self._validate_image_path(image)

	@property
	def images(self):
		return self._images

	@images.setter
	def images(self, value):
		for image in value:
			self._validate_image_path(image)
		self._images = value

	def _validate_image_path(self, pth):
		"""
		Validate the path to an image as necessary for each subclass.

		Subclasses will have their own idea where images should belong. By
		validating, it will ensure that, for instance, a live instance will
		have a valid url, while a cached instance will have a valid file path
		in the file system.

		Args:
			pth (String): The path to the image
		Returns:
			Void
		Raises:
			InvalidImagePathException
		"""
		if not re.match(self.image_path_regex, pth):
			raise InvalidImagePathException


class CraigslistAd(BaseCraigslistAd):
	"""Live posting hosted on craigslist.org"""
	image_path_regex = r'^https://images\.craigslist\.org/\w+\.jpg$'


class AdCache(BaseCraigslistAd):
	"""Downloaded, local instance of an ad."""
	image_path_regex = r'^/[\./\w]+\.jpg$'


class Archive(CustomModel):
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
	url = CharField()
	title = CharField()
	ad = ForeignKeyField(CraigslistAd)
	screenshot = CharField()
	images = ImageListField(default=lambda: [])

	def save(self, *args, **kwargs):
		# The ad must be saved first, otherwise the ForeignKey points to nothing
		self.ad.save(*args, **kwargs)
		return super(Archive, self).save(*args, **kwargs)
