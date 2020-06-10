# -*- coding: utf-8 -*-
import io
import gzip

from django.core.files.base import File


def is_gzipped(string):
    """bool: Check to see if the provided string is gzipped.
    """
    assertion = '\x1f\x8b\x08'
    if isinstance(string, (bytes,)):
        assertion = b'\x1f\x8b\x08'
    return string.startswith(assertion)


def gzip_bytes(bytes_obj):
    """byte: Compress a string as gzip in memory.
    """
    if isinstance(bytes_obj, (str,)):
        bytes_obj = bytes_obj.encode()
    out_ = io.BytesIO()
    with gzip.GzipFile(fileobj=out_, mode='w') as fo:
        fo.write(bytes_obj)
    return out_


def gunzip_bytes(bytes_obj):
    """byte: Uncompressed a gzipped bytestring and return it.
    """
    in_ = io.BytesIO()
    in_.write(bytes_obj)
    in_.seek(0)
    with gzip.GzipFile(fileobj=in_, mode='rb') as fo:
        gunzipped_bytes_obj = fo.read()
    return gunzipped_bytes_obj.decode()


class GzipFile(File):
    """Encode string content as gzipped File object.
    """
    def __init__(self, content, name=None):
        out = gzip_bytes(content.encode())
        super().__init__(out, name=name)
        self.size = len(content)

    def __str__(self):
        return 'Raw content'

    def __bool__(self):
        return True

    def open(self, mode=None):
        self.seek(0)
        return self

    def close(self):
        pass

    def write(self, data):
        self.__dict__.pop('size', None)
        return self.file.write(data)
