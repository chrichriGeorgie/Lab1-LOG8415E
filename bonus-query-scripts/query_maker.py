# LOG8415E - Assignment 1
# query_maker.py
# Python file to make queries in two separate threads

import sys
from threading import Thread
import requests
import logging
import time

# Function to do 1000 HTTP requests
def make_1000_sequentially(cluster, address):
    for x in range(1000):
        requests.get('http://'+address+cluster)

# Function to do 500 HTTP requests
def make_500_sequentially(cluster, address):
    for x in range(500):
        requests.get('http://'+address+cluster)

# Function of the first thread making 1000 requests
def thread_1000(cluster, address):
    logging.info("Thread 1 %s: starting 1000 requests", cluster)
    make_1000_sequentially(cluster, address)
    logging.info("Thread 1 %s: finishing 1000 requests", cluster)

# Function of the second thread making 500 requests, sleeping 1 minute and making 1000 requests
def thread_500_sleep_1000(cluster, address):
    logging.info("Thread 2 %s: starting 500 requests", cluster)
    make_500_sequentially(cluster, address)
    logging.info("Thread 2 %s: sleeping 1 minute", cluster)
    time.sleep(60)
    logging.info("Thread 2 %s: continuing 1000 more requests", cluster)
    make_1000_sequentially(cluster, address)
    logging.info("Thread 2 %s: finishing 500, sleep, 1000 requests", cluster)

# Function that waits for the threads to be finished before continuing
def wait_for_threads(threads):
    for index, thread in enumerate(threads):
        thread.join()
        logging.info("Main : thread %d done", index + 1)

# Function that creates the two threads with the desired usage and starts them
def set_up_cluster_threads(threadList, cluster, address):
    logging.info("Creating %s threads",cluster)
    t1 = Thread(target=thread_1000, args=(cluster, address,))
    t2 = Thread(target=thread_500_sleep_1000, args=(cluster, address,))
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
