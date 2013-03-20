from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from crawler.models import *
from datetime import datetime, date
from termcolor import colored
import urllib2
import os
import Queue
import threading
import re
import sys
import time
import json
import traceback
import HTMLParser
from bs4 import BeautifulSoup

def writeToFile(text, filename):
    dir = os.path.dirname(__file__)
    dir = os.path.join(dir, '../../../logs/')
    full = "full"
    text += "\n"
    text = text.encode('ascii', 'replace')
    f = open(dir + filename + ".log", 'a+')
    f.write(text)
    f.close()
    f = open(dir + full + ".log", 'a+')
    f.write(text)
    f.close()

def pLog(text):
    writeToFile(text, "process")

def qLog(text):
    writeToFile(text, "queue")

def uLog(text):
    writeToFile(text, "url")

def eLog(text):
    writeToFile(text, "error")

def processJSON(html):
    html_parser = HTMLParser.HTMLParser()
    try:
        jsonText = re.search(r"window.current_project = \"(.+)\";", html).group(1)
        tempObject = json.loads('{"text":"' + jsonText + '"}')
        jsonText = html_parser.unescape(tempObject["text"])
        #jsonText = re.sub("&quot;", '"', jsonText) #convert the html escaped quotes
        #jsonText = re.sub("&amp;", '&', jsonText) #convert the html escaped ampersand
        #jsonText = re.sub('\\\\"', '\"', jsonText) #do a little unescaping
        #for h in list(set(re.findall(r"&#x(.+);", jsonText))): #convert hex from the json into ascii
        #    jsonText = re.sub(r"&#x" + h + ";", h.decode("hex"), jsonText)

        return json.loads(jsonText)
    except:
        print jsonText + "\n\n"
        raise

def parseSearchResults(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html, 'html5lib')
    projects_added = 0
    urls = []
    for thumb in bs.body.find_all("div", "project-thumbnail"):
        #urls.append(base_url + thumb.a["href"].split('?')[0])
        urls.append(re.sub(r"https://", "http://", thumb.a["href"].split('?')[0]))
    status = str(len(urls)) + " projects found."
    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        urls.append(base_url + next["href"])
        status += " Adding " + urls[-1]
    print status
    qLog(status)
    return urls

def parseProject(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html, 'html5lib')
    fields = {}

    if bs.find(id="hidden_project") or bs.find(id="purged_project"):
        return []

    #Get info from metadata
    propNames = {
        "latitude" : "kickstarter:location:latitude",
        "longitude" : "kickstarter:location:longitude",
        "name" : "og:title",
        "url" : "og:url"
    }

    for propName in propNames:
        propTag = bs.find("meta", {"property": propNames[propName]})
        if(propTag):
            fields[propName] = propTag['content']
        else:
            fields[propName] = 0


    #Get what we can from the JSON that's at the top of the page
    #projectObject = processJSON(html)

    #fields["name"] = projectObject["name"]
    #fields["url"] = projectObject["urls"]["web"]["project"]
    #fields["category"] = projectObject["category"]["name"]
    #fields["goal"] = float(projectObject["goal"])
    #fields["raised"] = float(projectObject["pledged"])    
    #fields["backers"] = int(projectObject["stats"]["backers_count"])
    #fields["date"] = datetime.fromtimestamp(projectObject["launched_at"])
    #fields["date"] = projectObject["launched_at"]
    #duration = projectObject["deadline"] - projectObject["launched_at"]
    #fields["duration"] = duration / 60.0 / 60.0 / 24.0
    fields["date"] = datetime.fromtimestamp(float(re.search(r"&quot;launched_at&quot;:(\d+),&quot;", html).group(1)))


    #Then there's a few things to get from the page itself
    numbers = bs.body.find(id="pledged")
    fields["goal"] = float(numbers["data-goal"])
    fields["pledged"] = float(numbers["data-pledged"])
    fields["duration"] = bs.body.find(id="project_duration_data")["data-duration"]
    fields["faqs"] = len(bs.body.find("ul", "faqs").find_all("li"))
    fields["comments"] = bs.body.find(id="comments_count").find("span", "count").text
    fields["comments"] = re.sub(r"[^\d\.]", "", fields["comments"])
    fields["backers"] = bs.body.find(id="backers_nav").find("span", "count").text
    fields["backers"] = re.sub(r"[^\d\.]", "", fields["backers"])
    cat = bs.body.find(id="project-metadata").find("li", "category")
    fields["parentCat"] = cat["data-project-parent-category"]
    fields["category"] = cat.text
    fields["about"] = bs.body.find("div", {"class": "full-description"}).text

    #Now lets get the rewards
    fields["rewards"] = []
    rewards = bs.find(id="what-you-get").find_all("div", "NS-projects-reward")
    for r in rewards:
        reward = {}
        reward["amount"] = re.sub(r"[^\d]+", "", r.h5.text) #reward amount
        reward["text"] = r.find("div", "desc").p.text.strip()
        backers = r.find("span", "num-backers")
        backers = re.sub(r"[^\d]+", "", backers.text)
        limited = r.find("span", "limited")
        sold_out = r.find("span", "sold-out")
        if limited:
            limited = re.findall(r"[\d]+", limited.text)
            limited = limited[1]
        elif sold_out:
            limited = backers
        reward["limited"] = limited
        reward["backers"] = backers
        fields["rewards"].append(reward)

    saveProject(fields)
    if fields["backers"] > 0:
        return [fields["url"] + "/backers"]
    else:
        return []

def parseBackers(html):
    base_url = "http://www.kickstarter.com"
    try:
        bs = BeautifulSoup(html, 'html5lib')
    except LookupError:
        bs = BeautifulSoup(html)
    except:
        bs = BeautifulSoup(html)

    backers = []
    urls = []
    fields = {}
    for b in bs.body.find(id="leftcol").find_all("div", "NS_backers__backing_row"):
        fields = {}
        fields["username"] = b.a['href'][9:]
        if b.div.find("p", "location"):
            fields["location"] = b.div.find("p", "location").text.strip()
        backed = 0
        if b.div.find("p", "backings"):
            backed = re.sub(r"[^\d]", "", b.div.find("p", "backings").text)
        fields["backed"] = int(backed) + 1
        fields["name"] = b.div.h5.text.strip()
        backers.append(fields)
        #Add this profile to the queue to find more projects
        if(fields["backed"] > 99):
            urls.append(base_url + "/profile/" + fields["username"])
            print fields["username"] + " has backed " + str(fields["backed"]) + " projects."
            pLog(fields["username"] + " has backed " + str(fields["backed"]) + " projects.")
    
    newURL = bs.find("meta", {"property": "og:url"})['content']
    proj = getProjByURL(newURL)
    if not proj:
        projectObject = processJSON(html)
        userID = re.search(r"&quot;creator&quot;:{&quot;id&quot;:(\d+),&quot;", html).group(1)
        oldURL = re.sub(r'/projects/(.+)/', '/projects/' + str(userID) + '/', newURL)
        proj = getProjByURL(oldURL)
        proj.url = newURL
        proj.save()

    saveBackers(backers, proj)

    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        urls.append(base_url + next["href"])
    else:
        markAsFinished(newURL)
    
    return urls

def parseProfile(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html, 'html5lib')

    urls = []
    for link in bs.body.find_all("a", "project_item"):
        urls.append(base_url + link["href"].split('?')[0])
    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        urls.append(base_url + next["href"])
    message = str(len(urls)) + " found in a profile page."
    pLog(message)
    return urls

def saveProject(fields):
    proj = Project()
    proj.url = fields["url"]
    proj.name = fields["name"]
    proj.raised = fields["pledged"]
    proj.backers = fields["backers"]
    proj.goal = fields["goal"]
    proj.faqs = fields["faqs"]
    proj.date_end = fields["date"]
    proj.duration = fields["duration"]
    proj.category = fields["category"]
    proj.parentCat = fields["parentCat"]
    proj.about = fields["about"]
    proj.lat = fields["latitude"]
    proj.lon = fields["longitude"]
    proj.comments = fields["comments"]

    if Project.objects.filter(url=proj.url):
        print proj.name + " already Exists, moving on"
        pLog(proj.name + " already Exists, moving on")
        return True
    else:
        try:
            proj.save()
        except IntegrityError:
            print proj.name + " already Exists, moving on because of IntegrityError"
            eLog(proj.name + " already Exists, moving on because of IntegrityError")
            return True
        except:
            eLog("proj.about:")
            eLog(proj.about)
            eLog("about:")
            eLog(about)
            eLog("raw about div:")
            eLog(bs.body.find(id="about"))
            return False
        print proj.name + " Added"
        pLog(proj.name + " Added")

    for r in fields["rewards"]:
        rew = Reward()
        rew.project = proj
        rew.price = r["amount"]
        rew.text = r["text"]
        rew.backers = r["backers"]
        rew.limited = 0
        if(r["limited"]):
            rew.limited = r["limited"]
        try:
            rew.save()
        except:
            eLog("rew.text:")
            eLog(rew.text)
            raise

    return True

def saveBackers(backers, proj):
    backers_added = 0
    for backer in backers:
        #If we can find the backer in the database
        if Backer.objects.filter(username = backer["username"]):
            #Then grab him from the database and add the project to his list of projects
            thisBacker = Backer.objects.get(username = backer["username"])
            try:
                thisBacker.project.add(proj)
            except IntegrityError:
                eLog(backer["username"] + " already backing " + proj.name)
            except:
                eLog("Something went wrong while adding " + backer["username"] + " to " + proj.name)
                raise
        #If we can't find the backer in the database
        else:
            try:
                #try to create the backer as part of the project's set
                b = proj.backer_set.create(
                    username = backer["username"],
                    backed = backer["backed"],
                    name = backer["name"])
                if("location" in backer):
                    b.location = backer["location"]
                    b.save()
                backers_added += 1
            #If the backer is now found in the database, we'll fall to this error
            except IntegrityError:
                #Since we were just told the backer is in the database, it should be there
                thisBacker = Backer.objects.get(username = backer["username"])
                thisBacker.project.add(proj)
                eLog("IntegrityError: Adding project to existing backer")
            except:
                eLog("Something went wrong while adding " + backer["username"])
                raise
    remaining = proj.backers - Backer.objects.filter(project = proj).count()
    message = str(backers_added) + " Backers Added for " + proj.name + ". " + str(remaining) + " remaining."
    print message
    pLog(message)

def markAsFinished(projURL):
    try:
        proj = Project.objects.get(url=projURL)
    except:
        eLog("Couldn't Find " + projURL)
        raise
    proj.finished = True
    proj.save()

def removeFromDBQueue(projURL):
    URLsDone(url=projURL).save()
    URLQueue.objects.filter(url=projURL).delete()

def queueURLs(queue):
    urlSet = URLQueue.objects.all()
    for url in urlSet:
        queue.put(url.url)

def saveURLList(urls):
    uqList = []
    for url in urls:
        uqList.append(URLQueue(url=url))
    from django import db
    db.close_connection()
    URLQueue.objects.bulk_create(uqList)

def threadsRunning(threads):
    allAlive = True
    for thread in threads:
        allAlive = allAlive and thread.isAlive()
    return allAlive

def getProjByURL(projURL):
    try:
        proj = Project.objects.get(url=projURL)        
    except:
        return None
    return proj

class ThreadUrl(threading.Thread):
    """Threaded Url Grab"""
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.running = True

    def run(self):
        #proxy_support = urllib2.ProxyHandler({"http" : "127.0.0.1:8118"})
        #opener = urllib2.build_opener(proxy_support)
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        waitTime = 2
        while self.running:
            host = self.queue.get()
            if URLsDone.objects.filter(url=host):
                removeFromDBQueue(host)
                qLog("Skipping " + host)
                self.queue.task_done()
                continue
            try:
            	url = opener.open(host)
            except urllib2.HTTPError, error:
            	if error.code in [429, 503]:
                    waitTime *= 2
                    message = colored("Code: " + str(error.code), "red") + " Waiting " + str(waitTime) + " sec and retrying " + host
                    print message
                    uLog(message)
                    self.queue.put(host)
                    self.queue.task_done()
                    
                    time.sleep(waitTime)
                    continue
            	else:
            		raise
            waitTime = 2
            item = {}
            item["url"] = host
            item["html"] = url.read()
            self.out_queue.put(item)
            #print colored("Success! ", "green") + host
            uLog(colored("Success! ", "green") + host)
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
            html = self.queue.get()
            self.queue.task_done()

    def stop(self):
        self.running = False

class DataminerThread(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.running = True

    def queueURL(self, urls):
        if urls:
            added = 0
            createList = []
            for url in urls:
                url = re.sub(r"https://", "http://", url)
                if not URLsDone.objects.filter(url=url) and not URLQueue.objects.filter(url=url):
                    self.out_queue.put(url)
                    createList.append(URLQueue(url=url))
                    added += 1
            URLQueue.objects.bulk_create(createList)
            message = str(added) + "/" + str(len(urls)) + " added to the queue"
            print message
            qLog(message)

    def run(self):
        while not self.queue.empty() or self.running:
            item = self.queue.get()
            
            try:
                #search url. Scan for new projects and the next search page
                if(re.search(r"/search", item["url"])):  
                	self.queueURL(parseSearchResults(item["html"]))
                
                #profile url. Scan for new projects
                elif(re.search(r"/profile", item["url"])):
                	self.queueURL(parseProfile(item["html"]))

                #backers url. Scan for new profiles, and add backers to projects
                elif(re.search(r"/backers\?", item["url"]) or re.search(r"/backers$", item["url"])): #edge case, project name starts with "backers"
                	self.queueURL(parseBackers(item["html"]))
                
                #project url. Scan project and add the backers page to the queue
                else:									
                    self.queueURL(parseProject(item["html"]))
            except ObjectDoesNotExist:
                message = colored(str(sys.exc_info()[0]) + ": ", "red") + item["url"]
                for line in traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]):
                    message += line
                print message
                eLog(message)
                self.out_queue.put(item["url"])
                self.queue.task_done()
            except:
                
                message = "\n"
                message += colored(str(sys.exc_info()[0]) + ": ", "red") + item["url"]
                message += "\n"
                for line in traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2]):
                    message += line
                eLog(message)
                raise

            
            removeFromDBQueue(item["url"])
            if not self.queue.empty():
                self.queue.task_done()

    def stop(self):
        self.running = False

class Command(BaseCommand):

    def handle(self, *args, **options):
        print colored("Starting", "blue")
    
        urlThreads = []
        processingThreads = []

        HTMLs = Queue.Queue(maxsize=1000)
        URLs = Queue.Queue()

        for i in range(5):
            t = ThreadUrl(URLs, HTMLs)
            #t.setDaemon(True)
            t.start()
            urlThreads.append(t)

        for i in range(3):
            t = DataminerThread(HTMLs, URLs)
            t.setDaemon(True)
            t.start()
            processingThreads.append(t)
        
        #populate queue with data   
        queueURLs(URLs)

        #wait on the queue until everything has been processed     
        running = True
        
        while running:
            time.sleep(1)
            transaction.enter_transaction_management()
            transaction.commit() # Whenever you want to see new data

            if Cursor.objects.filter(id=2) or not threadsRunning(processingThreads + urlThreads):
                print colored("FULL STOP", "red")
                running = False
                c = Cursor.objects.filter(id=2).delete()
                for t in urlThreads:
                    t.stop()
                #URLProcessor.stop()
                print colored("Waiting on threads", "red")
                for t in urlThreads:
                    t.join()
                print colored("url threads stopped", "red")
                #URLProcessor.join()
                print colored("all threads stopped. Dumping URLs", "red")
                URLList = []
                while not URLs.empty():
                    URLList.append(URLs.get())
                    URLs.task_done()
                #saveURLList(URLList)
                #print URLProcessor.running or not URLProcessor.queue.empty()

                #while not ready.empty():
                #    print ready.get()[:25]
                #    ready.task_done()
            
        print colored("URLs dumped. Joining queue to confirm", "red")
        URLs.join()
        print colored("URLs is empty", "red")
        HTMLs.join()
        print colored("ready is empty", "red")