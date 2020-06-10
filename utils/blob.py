# -*- coding: utf-8 -*-
import json
import utils.logging as logging

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from utils.gzip import GzipFile, gunzip_bytes, is_gzipped
from utils.encoders import DjangoPartialModelJsonEncoder


logger = logging.Logger(__name__)


def get_object(prefix):
    """Retrieve an object from S3 and load into memory.
    """
    with default_storage.open(prefix) as fo:
        content = fo.read()
        if is_gzipped(content):
            content = gunzip_bytes(content)
    if isinstance(content, (bytes,)):
        content = content.decode()
    return json.loads(content)


def put_object(prefix, content, gzipped=True):
    """Load a blob into S3.
    """
    FileClass = GzipFile if gzipped else ContentFile

    if default_storage.exists(prefix):
        default_storage.delete(prefix)

    content = json.dumps(content, cls=DjangoPartialModelJsonEncoder)

    logger.info(
        'Loading prefix to S3 (gzip: {}): {}'.format(gzipped, prefix)
    )

    return default_storage.save(prefix, FileClass(content))
