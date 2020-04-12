
import gzip
import brotli
import zlib


def decode_content(content, content_encoding):
    if not content or not content_encoding:
        return content

    # Handle multiple encodings recursively
    multiple_encodings = [x.strip() for x in content_encoding.split(',') if x.strip()]
    if len(multiple_encodings) > 1:
        for e in reversed(multiple_encodings):
            content = decode_content(content, e)
        return content

    # Handle one encoding

    if content_encoding.lower() == 'identity':
        return content

    if content_encoding.lower() == 'gzip':
        return gzip.decompress(content)

    if content_encoding.lower() == 'br':
        return brotli.decompress(content)

    # TODO: deflate
    # In my test 13k cache files, I haven't found any response with deflate.
    # Should be supported by zlib, but couldn't test it because I have no samples

    raise Exception("Unknown encoding: %s" % (content_encoding,))
