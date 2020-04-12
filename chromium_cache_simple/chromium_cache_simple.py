#!/usr/bin/env python3


# https://github.com/chromium/chromium/blob/master/net/disk_cache/simple/simple_entry_format.h

# If these magic numbers change, probably the format changed and this parser doesn't work
INITIAL_MAGIC_NUMBER = 0xfcfb6d1ba7725c30.to_bytes(8, 'little')
FINAL_MAGIC_NUMBER = 0xf4fa6f45970d41d8.to_bytes(8, 'little')


def _timestamp_microsec_win_to_unix_ts(microseconds_since_win_epoch):
    return microseconds_since_win_epoch / 1000000 - 11644473600


def _parse_http_response_info(raw):
    # Ref: chromium-master/net/http/http_response_info.cc  HttpResponseInfo::InitFromPickle

    if len(raw) - 4 != int.from_bytes(raw[:4], 'little'):
        raise Exception("Unexpected HTTP Response Info length")
    raw = raw[4:]  # Pickle content
    flags = int.from_bytes(raw[0:4], 'little')
    if flags & 0xff != 3:
        raise Exception("Expected version 3 of http_response_info")

    request_time = int.from_bytes(raw[4:12], 'little')
    request_time = _timestamp_microsec_win_to_unix_ts(request_time)
    response_time = int.from_bytes(raw[12:20], 'little')
    response_time = _timestamp_microsec_win_to_unix_ts(response_time)

    headers_str_len = int.from_bytes(raw[20:24], 'little')
    headers_str = raw[24:24 + headers_str_len]
    if headers_str[-2:] != b'\x00\x00':
        raise Exception(r"Unexpected headers. Should end with \x00\x00")
    status_and_headers = headers_str[:-2].split(b'\x00')
    status = status_and_headers[0].decode()
    headers = [x.decode() for x in status_and_headers[1:]]

    header_dict = {}
    for header in headers:
        try:
            hk, hv = header.split(':', maxsplit=1)
            header_dict[hk.strip().lower()] = hv.strip()
        except Exception:
            continue

    has_cert = (flags & 256 == 256)
    if has_cert:
        pass  # ... TODO: implement
    # This http_response_info can contain a lot of other stuff, not parsed here.
    # Full list and parsing details can be found in the referenced chromium source code
    # Other information that can be present:
    # CERT, CERT_STATUS, SSL_CONNECTION_STATUS, SIGNED_CERTIFICATE_TIMESTAMPS, VARY_DATA,
    # socket_address_host, socket_address_port, ALPN_NEGOTIATED_PROTOCOL, CONNECTION_INFO,
    # KEY_EXCHANGE_GROUP, STALENESS, PEER_SIGNATURE_ALGORITHM

    return {
        'ts_request': request_time,
        'ts_response': response_time,
        'status': status,
        'headers': headers,
        'header_dict': header_dict
    }


def parse_file(fpath):
    with open(fpath, 'rb') as f:
        raw = f.read()

    # Check magic numbers
    if raw[:8] != INITIAL_MAGIC_NUMBER:
        raise Exception("Unexpected initial magic number")
    if raw[-24:-16] != FINAL_MAGIC_NUMBER:
        raise Exception("Unexpected final magic number")

    # Parse key (URL)
    key_length = int.from_bytes(raw[12:16], 'little')
    url = raw[24:24+key_length].decode()

    # Parse stream0 from end of file
    stream0_eof = raw[-24:-4]
    has_sha256 = (stream0_eof[8] & 2 == 2)
    stream0_size = int.from_bytes(stream0_eof[-4:], 'little')
    stream0_idx_end = len(raw) - 24
    if has_sha256:
        stream0_idx_end -= 32
    stream0_idx_start = stream0_idx_end - stream0_size
    stream0_body = raw[stream0_idx_start:stream0_idx_end]
    stream0_parsed = _parse_http_response_info(stream0_body)

    # Parse stream1. Note that stream1_eof is useless (doesn't even always have the size)
    stream1_idx_end = stream0_idx_start - 24
    stream1_idx_start = 24 + key_length
    if stream1_idx_start <= stream1_idx_end:
        content = raw[stream1_idx_start:stream1_idx_end]
    else:
        content = None

    return {
        'url': url,
        'meta': stream0_parsed,
        'content': content
    }
