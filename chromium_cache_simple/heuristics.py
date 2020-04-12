
import string
from urllib.parse import urlparse
import hashlib


def get_folder_name(parsed_cache_file):
    domain = urlparse(parsed_cache_file['url']).netloc.lower()
    allowed = string.ascii_lowercase + string.digits + '.-'
    return ''.join([c for c in domain if c in allowed])


def get_file_extension(parsed_cache_file):
    ct2ext = {
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/bmp': 'bmp',
        'image/webp': 'webp',
        'image/tiff': 'tif',
        'text/html': 'html',
        'text/css': 'css',
        'text/xml': 'xml',
        'text/javascript': 'js',
        'application/javascript': 'js',
        'application/x-javascript': 'js',
        'application/json': 'json',
        'application/pdf': 'pdf',
        'application/zip': 'zip',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'image/svg': 'svg'
    }

    content_type = parsed_cache_file['meta']['header_dict'].get('content-type', None)

    if not content_type:
        return None
    for ct in ct2ext.keys():
        if content_type.startswith(ct):
            return ct2ext[ct]
    return None


def get_file_name(parsed_cache_file):
    if not parsed_cache_file['content']:
        return None
    ts_str = str(int(parsed_cache_file['meta']['ts_request']))
    content_hash = hashlib.sha1(parsed_cache_file['content']).hexdigest()
    extension = get_file_extension(parsed_cache_file) or 'dat'
    return '%s_%s.%s' % (ts_str, content_hash, extension)
