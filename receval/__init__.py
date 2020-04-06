__version__ = '0.1.0'

from configurations import importer

# Enable django-configuration support for PyCharm
importer.install(check_options=True)
