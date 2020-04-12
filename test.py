#!/usr/bin/env python3


import chromium_cache_simple
import logging
import sys
import os

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)

    files = chromium_cache_simple.list_cache_files(sys.argv[1])
    for fpath in files:
        try:
            res = chromium_cache_simple.parse_and_decode_file(fpath)
            logger.info('OK %s: %s: %s bytes', fpath, res['meta']['header_dict'].get('content-type', '???'), len(res['content']))
            odir = chromium_cache_simple.heuristics.get_folder_name(res)
            ofname = chromium_cache_simple.heuristics.get_file_name(res)
            if odir and ofname:
                os.makedirs(os.path.join(sys.argv[2], odir), exist_ok=True)
                ofpath = os.path.join(sys.argv[2], odir, ofname)
                with open(ofpath, 'wb') as f:
                    f.write(res['content'])
                os.makedirs(os.path.join(sys.argv[2], '_all'), exist_ok=True)
                ofpath = os.path.join(sys.argv[2], '_all', ofname)
                with open(ofpath, 'wb') as f:
                    f.write(res['content'])

        except Exception as ex:
            logger.error("ERR %s: %s", fpath, str(ex))


if __name__ == '__main__':
    main()
