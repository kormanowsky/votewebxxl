###
# VoteWebXXL config file
###
import os
import tempfile

# VoteWebXXL version
VERSION = "1.1"

# CSRF token key
CSRF_TOKEN = "csrfmiddlewaretoken"

# python-magic magic file path
MAGIC_FILE = os.path.normpath(os.path.join(os.environ['VIRTUAL_ENV'], 'Lib\site-packages\magic\libmagic\magic.mgc'))

# system folder for temporary files
SYSTEM_TMP_FOLDER = tempfile.gettempdir()

# image types allowed for upload
ALLOWED_IMAGE_TYPES = [
    'image/png',
    'image/jpeg',
    'image/bmp',
    'image/gif'
]