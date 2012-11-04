import urllib
import datetime
from termcolor import colored
from bs4 import BeautifulSoup
import re
import sys
import json

def parseSearchResults(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html)
    projects_added = 0
    urls = []
    for thumb in bs.body.find_all("div", "project-thumbnail"):
        urls.append(base_url + thumb.a["href"].split('?')[0])
    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        urls.append(base_url + next["href"])
    return urls


def parseProject(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html)
    fields = {}

    #Get info from metadata
    propNames = {
        "latitude" : "kickstarter:location:latitude",
        "longitude" : "kickstarter:location:longitude",
        #"title" : "og:title",
        #"url" : "og:url",
    }

    for propName in propNames:
        propTag = bs.find("meta", {"property": propNames[propName]})
        if(propTag):
            fields[propName] = propTag['content']
        else:
            fields[propName] = 0


    #Get what we can from the JSON that's at the top of the page
    jsonText = re.search(r"window.current_project = (.+)", html).group(1)
    projectObject = json.loads(jsonText)
    
    fields["name"] = projectObject["name"]
    fields["url"] = projectObject["urls"]["web"]["project"]
    fields["category"] = projectObject["category"]["name"]
    fields["goal"] = float(projectObject["goal"])
    fields["raised"] = float(projectObject["pledged"])    
    fields["backers"] = int(projectObject["stats"]["backers_count"])
    fields["date"] = datetime.datetime.fromtimestamp(projectObject["launched_at"])
    #fields["date"] = projectObject["launched_at"]
    duration = projectObject["deadline"] - projectObject["launched_at"]
    fields["duration"] = duration / 60.0 / 60.0 / 24.0


    #Then there's a few things to get from the page itself
    fields["faqs"] = len(bs.body.find("ul", "faqs").find_all("li"))
    fields["comments"] = bs.body.find(id="comments_count").find("span", "count").text
    fields["comments"] = re.sub(r"[^\d\.]", "", fields["comments"])
    cat = bs.body.find(id="project-metadata").find("li", "category")
    fields["parentCat"] = cat["data-project-parent-category"]
    fields["about"] = bs.body.find("div", {"class": "full-description"}).text

    #Now lets get the rewards
    fields["rewards"] = []
    rewards = bs.find_all("div", "NS-projects-reward")
    for r in rewards:
        reward = {}
        reward["amount"] = re.sub(r"[^\d]+", "", r.h3.text) #reward amount
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

    return fields["url"] + "/backers"


def parseBackers(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html)
    backers = []
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
        fields["name"] = b.div.h3.text.strip()
        backers.append(fields)
    print backers
    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        return base_url + next["href"]
    else:
        return None
   
def parseProfile(html):
    base_url = "http://www.kickstarter.com"
    bs = BeautifulSoup(html)

    urls = []
    for link in bs.body.find_all("a", "project_item"):
        urls.append(base_url + link["href"].split('?')[0])
    if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
        next = bs.body.find("div", "pagination").find("a", "next_page")
        urls.append(base_url + next["href"])
    return urls

src = "profile.html"
f = open(src, "r")
html = f.read()

#print parseProfile(html)

src = "abaSearch.html"
f = open(src, "r")
html = f.read()

print parseSearchResults(html)

src = "project3.html"
f = open(src, "r")
html = f.read()

#print json.dumps(parseProject(html))

src = "backers.html"
f = open(src, "r")
html = f.read()

#print parseBackers(html)