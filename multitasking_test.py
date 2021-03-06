"""
from multiprocessing import Process
from multiprocessing import Pool


pool = Pool(processes=10)              # start 4 worker processes
    pool.apply_async(MergeOneWikidataItem , [WikidataItem])    # make one word in //
"""



import multiprocessing
import time
import random
import sys


def worker(item):
    print("test", item)
    sys.stdout.flush()
    time.sleep( random.randint(1, 3) )
    return item


result_list = []
def log_result(result):
    result_list.append(result)


if __name__ == "__main__":
    WORKERS = 10  # N worker processes
    WORDS   = 100

    items_reader = range(WORDS)
    p = multiprocessing.Pool(WORKERS)

    for item in items_reader:
        print("read from reader: ", item)
        p.apply_async(worker, args = (item,), callback = log_result)

    # imap
    # p.imap(worker, items_reader)

    p.close()
    p.join()
    print(result_list)
