import sys
import os
import os.path
import requests
import urllib3


DOWNLOAD_TIMEOUT = 10


def get_http_file_size(url):
    r = requests.get(url, stream=True, verify=False, allow_redirects=True, timeout=DOWNLOAD_TIMEOUT)
    size = r.headers['Content-length']
    r.close()
    return int(size)


def get_local_file_size(file_name):
    return os.path.getsize(file_name)


def _download_with_progress(r, f):
    CHUNK_SIZE = 1024*4
    readed = 0
    r.raw.decode_content = False

    for chunk in r.iter_content(CHUNK_SIZE):
        f.write(chunk)
        readed += len(chunk)

        if readed > 1024*1024:
            print('.', end='')
            sys.stdout.flush()
            readed = 0


def continue_downloading(url, local_file, resume_byte_pos=0):
    if resume_byte_pos == 0:
        # new file
        r = requests.get(url, stream=True, verify=False, allow_redirects=True, timeout=DOWNLOAD_TIMEOUT)

        with open(local_file, 'wb') as f:
            _download_with_progress(r, f)

        r.close()

    else:
        # append
        resume_header = {'Range': 'bytes=%d-' % resume_byte_pos}
        r = requests.get(url, stream=True, verify=False, allow_redirects=True, timeout=DOWNLOAD_TIMEOUT,
                         headers=resume_header)

        with open(local_file, 'ab') as f:
            _download_with_progress(r, f)

        r.close()


def _download_with_resume(url, local_file):
    # check already downloaded
    if os.path.isfile(local_file):
        return  True

    # check part file
    part_file = local_file + ".part"

    if os.path.isfile(part_file): # file exists
        # check size
        local = get_local_file_size(part_file)
        remote = get_http_file_size(url)

        if local == remote:
            return True  # OK
        else:
            # continue downloading
            continue_downloading(url, part_file, local)

    else: # no local file
        # downloading
        continue_downloading(url, part_file, 0)
        remote = get_http_file_size(url)

    # rename part_file to local_file
    local = get_local_file_size(part_file)
    if local == remote:
        os.rename(part_file, local_file)


def download_with_resume(url, local_file, attempts=5):
    for i in range(attempts):
        try:
            _download_with_resume(url, local_file)
            return  True

        except requests.exceptions.ConnectionError as e:
            pass

        except urllib3.exceptions.ReadTimeoutError as e:
            pass
