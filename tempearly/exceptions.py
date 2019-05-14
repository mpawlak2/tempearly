class TemplateError(Exception):
	"""The base class for a template exceptions."""
	def __init__(self, msg, token):
		self.token = token
		super().__init__(msg)


class TemplateSyntaxError(TemplateError):
	pass


class TemplateKeyError(TemplateError):
	pass
