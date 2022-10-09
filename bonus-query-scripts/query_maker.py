import sys
from threading import Thread
import requests
import logging
import time

def make_1000_sequentially(cluster, address):
    for x in range(1000):
        requests.get('http://'+address+cluster)

def make_500_sequentially(cluster, address):
    for x in range(500):
        requests.get('http://'+address+cluster)

def thread_1000(cluster, address):
    logging.info("Thread %s: starting 1000 requests", cluster)
    make_1000_sequentially(cluster, address)
    logging.info("Thread %s: finishing 1000 requests", cluster)

def thread_500_sleep_500(cluster, address):
    logging.info("Thread %s: starting 500 requests", cluster)
    make_500_sequentially(cluster, address)
    logging.info("Thread %s: sleeping 1 minute", cluster)
    time.sleep(60)
    logging.info("Thread %s: continuing 500 more requests", cluster)
    make_500_sequentially(cluster, address)
    logging.info("Thread %s: finishing 500, sleep, 500 requests", cluster)
        
def wait_for_threads(threads):
    for index, thread in enumerate(threads):
        thread.join()
        logging.info("Main : thread %d done", index + 1)

def set_up_cluster_threads(threadList, cluster, address):
    logging.info("Creating %s threads",cluster)
    t1 = Thread(target=thread_1000, args=(cluster, address,))
    t2 = Thread(target =thread_500_sleep_500, args=(cluster, address,))
    threadList.append(t1)
    threadList.append(t2)

    logging.info("Starting %s threads", cluster)
    t1.start()
    t2.start()

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    address = sys.argv[1]
    logging.info("Loadbalancer url: {}".format(address))

    threads = list()
    set_up_cluster_threads(threads, '/cluster1', address)
    wait_for_threads(threads)
    logging.info("Cluster 1 Threads done")
    threads.clear()

    set_up_cluster_threads(threads, '/cluster2', address)
    wait_for_threads(threads)
    logging.info("Cluster 2 Threads done")
