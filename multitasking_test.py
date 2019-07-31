"""
from multiprocessing import Process
from multiprocessing import Pool


pool = Pool(processes=10)              # start 4 worker processes
    pool.apply_async(MergeOneWikidataItem , [WikidataItem])    # make one word in //
"""



import multiprocessing
import time
import random


def worker(i):
    print("test", i)
    time.sleep( random.randint(1, 3) )


if __name__ == "__main__":
    N = 10  # N worker processes
    items = range(100)
    p = multiprocessing.Pool(N)
    p.map(worker, items)



