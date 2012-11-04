from django.core.management.base import BaseCommand, CommandError
#from django.db import IntegrityError
from django.db import transaction
from crawler.models import *
#from datetime import datetime, date
import urllib
import Queue
import threading
import time
from termcolor import colored
from bs4 import BeautifulSoup


hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
          "http://ibm.com", "http://apple.com"]




class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.running = True

    def run(self):
        theMax = 10
        theCount = 0
        while self.running:
            #grabs host from queue
            host = self.queue.get()

            #grabs urls of hosts and adds to html ready to process
            if theCount < theMax:
                self.queue.put(host)
                print "added " + host + " back to the queue"
            theCount += 1

            url = urllib.urlopen(host)
            self.out_queue.put(url.read())
            print "added " + host + " to the ready queue"
            
            #signals to queue job is done
            self.queue.task_done()
    def stop(self):
        self.running = False


class Titler(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.running = True

    def run(self):
        while not self.queue.empty() or self.running:
            print "waiting for html"
            html = self.queue.get()
            soup = BeautifulSoup(html)
            print soup.findAll(['title'])
            self.queue.task_done()

    def stop(self):
        self.running = False

class DataminerThread(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    def queueURL(url):
        if not Project.objects.filter(url=url):
            self.out_queue.put(url)

    def run(self):
        while True:
            html = self.queue.get()

            self.queue.task_done()

class Command(BaseCommand):

    HTMLs = Queue.Queue()
    URLs = Queue.Queue() 

    def handle(self, *args, **options):
        print colored("Starting", "blue")
    
        urlThreads = []

        for i in range(10):
            t = ThreadUrl(URLs, HTMLs)
            #t.setDaemon(True)
            t.start()
            urlThreads.append(t)

        for i in range(1):
            URLProcessor = Titler(HTMLs)
            URLProcessor.setDaemon(True)
            URLProcessor.start()

        #populate queue with data   
        for host in hosts:
            URLs.put(host)

        #wait on the queue until everything has been processed     
        running = True
        
        while running:
            time.sleep(1)
            transaction.enter_transaction_management()
            transaction.commit() # Whenever you want to see new data
            if(Cursor.objects.filter(id=2)):
                print colored("FULL STOP", "red")
                running = False
                c = Cursor.objects.get(id=2)
                c.delete()
                for t in urlThreads:
                    t.stop()
                #URLProcessor.stop()
                print colored("Waiting on threads", "red")
                for t in urlThreads:
                    t.join()
                print colored("url threads stopped", "red")
                #URLProcessor.join()
                print colored("all threads stopped. Dumping URLs", "red")
                while not URLs.empty():
                    print URLs.get()
                    URLs.task_done()
                print URLProcessor.running or not URLProcessor.queue.empty()

                #while not ready.empty():
                #    print ready.get()[:25]
                #    ready.task_done()
            else:
                print "Still running"
            

        URLs.join()
        print colored("URLs is empty", "red")
        ready.join()
        print colored("ready is empty", "red")

