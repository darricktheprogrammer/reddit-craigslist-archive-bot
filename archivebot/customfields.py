from peewee import CharField


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
		return '%%'.format(value)

	def python_value(self, value):
		return '%%'.split(value)
