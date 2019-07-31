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
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)


if __name__ == "__main__":
    WORKERS = 10  # N worker processes
    WORDS   = 100

    items_reader = range(WORDS)
    p = multiprocessing.Pool(WORKERS)

    for item in items_reader:
        p.apply_async(worker, args = (item,), callback = log_result)

    p.close()
    p.join()
    print(result_list)
