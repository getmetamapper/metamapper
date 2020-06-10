# -*- coding: utf-8 -*-
import unittest
import utils.gzip as gzip


PLAIN_TXT = 'Hello there.'

BZIPPED_TXT = (
    b'BZh91AY&SY\xc3\x9f!\x18\x00\x00\x01\x15'
    b'\x80@\x01\x00@\x02D\x94\x00 \x00"\x01\x93'
    b'\xd4 \xc9\x88{\x9c\x98\x88\xa3\xc5\xdc\x91'
    b'N\x14$0\xe7\xc8F\x00')

GZIPPED_TXT = (
    b'\x1f\x8b\x08\x00\xfd0\xcc^\x02\xff\xf3H'
    b'\xcd\xc9\xc9W(\xc9H-J\xd5\x03\x00\xa7z'
    b'\xe3}\x0c\x00\x00\x00')


class UtilsGzipFileTests(unittest.TestCase):
    """Test extension of File class used to gzip-encode data.
    """
    def test_implements_file_interface(self):
        """It should gzip the content within the file.
        """
        file = gzip.GzipFile(PLAIN_TXT)
        byte = b''

        for b in file.chunks():
            byte += b

        self.assertEqual(gzip.gunzip_bytes(byte), PLAIN_TXT)


class UtilsGzipFcnTests(unittest.TestCase):
    """Test helper functions in gzip module.
    """
    def test_is_gzipped_positive(self):
        """It should return true if the string is gzipped.
        """
        self.assertTrue(gzip.is_gzipped(GZIPPED_TXT))

    def test_is_gzipped_negative(self):
        """It should return false if the string is not gzipped.
        """
        self.assertFalse(gzip.is_gzipped(BZIPPED_TXT))

    def test_is_gzipped_accepts_string(self):
        """It should accept a string or a bytes object.
        """
        self.assertFalse(gzip.is_gzipped(PLAIN_TXT))

    def test_gunzip_bytes(self):
        """It should convert a gzipped bytes object to a string.
        """
        self.assertEqual(gzip.gunzip_bytes(GZIPPED_TXT), PLAIN_TXT)

    def test_gzip_bytes(self):
        """It should convert a string to gzipped bytes. GZIP is not deterministic, so this
        test is a sort of workaround.
        """
        gzipped = gzip.gzip_bytes(PLAIN_TXT).getvalue()

        self.assertTrue(gzip.is_gzipped(gzipped))
        self.assertEqual(gzip.gunzip_bytes(gzipped), PLAIN_TXT)
