import urllib
import re
from bs4 import BeautifulSoup

class Object(object):
    pass

class Reward(object):
	pass

url="http://www.kickstarter.com/projects/antennasup/antennas-up-radio-promotion-of-the-awkward-phase"
url="http://www.kickstarter.com/projects/1684781151/legends-of-eisenwald"

bs = BeautifulSoup(urllib.urlopen(url))

propNames = {
	"latitude" : "kickstarter:location:latitude",
	"longitude" : "kickstarter:location:longitude",
}

properties = []

for propName in propNames:
	propTag = bs.find("meta", {"property": propNames[propName]})
	print propName + ": " + propTag['content']

contentDiv = bs.find("div", {"id":"about", "data-project-state":"successful"})
#contentDiv = bs.select("#about")

about = Object()
about.charlength = len(contentDiv.text)
about.wordlength = len(contentDiv.text.split(None))
about.numImages =  len(contentDiv.find_all("img"))

#for para in contentDiv[0]("p"):
#	print para.text
#	about.charlength += len(para.text)
#	about.wordlength += len(para.txt)


numRewards = 0

rewards = bs.find_all("div", "NS-projects-reward") 

for r in rewards:

	print "".join(re.findall(r"[\d]+", r.h3.span.text)) #reward amount
	limited = r.find("span", "limited")
	sold_out = r.find("span", "sold_out")
	if limited:
		limited = re.findall(r"[\d]+", limited.text)
		print "Limited: " + limited[0] + " out of " + limited[1]
	elif sold_out:
		limited = sold_out
		limited = re.findall(r"[\d]+", limited.text)
		print "Limited: " + limited[0] + " out of " + limited[1]
	else:
		backers = r.find("span", "num-backers")
		backers = "".join(re.findall(r"[\d]+", backers.text))
		print "backers: " + backers
#	print r.find("div", "desc").text #reward text


print "Updates count: " + re.findall(r"[\d]+", bs.body.find(id="updates_count").text)[0]
print "Backers: " + re.findall(r"[\d]+", bs.body.find(id="backers_count").text)[0]
print "Raised: " + bs.body.find(id="pledged")["data-pledged"]
print "Goal: " + bs.body.find(id="pledged")["data-goal"]
date_data = bs.body.find(id="project_duration_data")
print "Date End: " + date_data["data-end_time"]
print "Days long: " + date_data["data-duration"]
print "Project Category: " + bs.body.find(id="project_category").a.text 
print "Number of Rewards: " + str(len(rewards))
print "Images in About: " + str(about.numImages)
print "Characters in About: " + str(about.charlength)
print "Words in About: " + str(about.wordlength)