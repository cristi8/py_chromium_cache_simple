from .chromium_cache_simple import parse_file
from .content_decoder import decode_content
from . import heuristics


def parse_and_decode_file(fpath):
    parsed = parse_file(fpath)
    decoded_content = decode_content(
        parsed.get('content', None),
        parsed['meta']['header_dict'].get('content-encoding', None)
    )
    parsed['content'] = decoded_content
    return parsed


def list_cache_files(cache_dir):
    import os
    dir_content = [os.path.join(cache_dir, x) for x in os.listdir(cache_dir) if x.endswith('_0')]
    return [x for x in dir_content if os.path.isfile(x)]
