import urllib
import re
import MySQLdb as mdb
import sys
from datetime import datetime, date
from bs4 import BeautifulSoup


def insert(table, data):
	query = "INSERT INTO " + table + " SET "
	combined = []
	for field in data:
		if(field):
			print data[field]
			combined.append("%s = '%s'" % (field, data[field]))
	query += ", ".join(combined)
	print query


con = mdb.connect('127.0.0.1', 'root', 'root', 'kickstarter', port=8889);

base_url = "http://www.kickstarter.com"
url = "http://www.kickstarter.com/projects/doublefine/double-fine-adventure/"
url = "http://www.kickstarter.com/projects/blytherenay/damsels-of-dorkington-2012-season?ref=live"
url = "http://www.kickstarter.com/projects/doublefine/double-fine-adventure/backers?page=2"
#url = "http://www.kickstarter.com/profile/117725140"

bs = BeautifulSoup(urllib.urlopen(url))

waiting_urls = []

scraped_urls = []

profiles = []

if(re.search(r"/backers", url)): #backers url. Scan for new profiles
	projurl = re.search(r"^(.+)backers", url)
	print projurl.groups(0)
	for b in bs.body.find(id="leftcol").find_all("div", "NS-backers-backing-row"):
		username = b.a['href'][9:]
		print username

elif(re.search(r"/profile", url)): #profile url. Scan for new projects
	for side in bs.body.find(id="sidebar").find("ul", "menu-sidebar").find_all("li"):
	if side.h3.text == "Websites":
		
		myBacker = Backer.objects.get(username = )
		for item in side.ul.find_all("li"):
			
			site = Sites()
			site.url
			item.a["href"]
	for thumb in bs.body.find_all("div", "project-thumbnail"):
		print base_url + thumb.a["href"].split('?')[0]

# this code scans for just any project on a page. Not super useful for my new tactic.
#	for anchor in bs.body.find_all("a"):
#		if anchor.has_key("href") and re.match(r"^/projects/[^/]+/[^/]+/", anchor["href"]):
#			sub_url = re.match(r"/projects/[^/]+/[^/]+/", anchor["href"])
#			proj_url = base_url + sub_url.group(0)
#			if proj_url not in all_urls:
#				all_urls.append(proj_url)
#				print proj_url

else:
	fields = {
		"url" : url
	}

	propNames = {
		"latitude" : "kickstarter:location:latitude",
		"longitude" : "kickstarter:location:longitude",
	}

	for propName in propNames:
		propTag = bs.find("meta", {"property": propNames[propName]})
		fields[propName] = propTag['content']

	contentDiv = bs.find("div", {"id":"about", "data-project-state":"successful"})
	contentDiv = bs.body.find(id="about")

	#print "Updates count: " + re.findall(r"[\d]+", bs.body.find(id="updates_count").text)[0]
	#print "Backers: " + re.findall(r"[\d]+", bs.body.find(id="backers_count").text)[0]
	fields["raised"] = bs.body.find(id="pledged")["data-pledged"]
	fields["goal"] = bs.body.find(id="pledged")["data-goal"]
	fields["faqs"] = len(bs.body.find("ul", "faqs").find_all("li"))
	date_data = bs.body.find(id="project_duration_data")
	fields["date_end"] = datetime.strptime(date_data["data-end_time"], "%a, %d %b %Y %H:%M:%S -0000")
	fields["duration"] = date_data["data-duration"]
	cat = bs.body.find(id="project_category")
	fields["category"] = cat["data-project-category"]
	fields["parentCat"] = cat["data-project-parent-category"]
	#fields["about"] = contentDiv.text
	#print "Number of Rewards: " + str(len(rewards))
	#print "Images in About: " + str(about.numImages)
	#print "Characters in About: " + str(about.charlength)
	#print "Words in About: " + str(about.wordlength)
	fields["name"] = bs.body.find(id="name").text

	insert('projects', fields)
	
	rewards = bs.find_all("div", "NS-projects-reward") 

	for r in rewards:
		fields = {}
		fields["amount"] = "".join(re.findall(r"[\d]+", r.h3.span.text)) #reward amount
		fields["text"] = r.find("div", "desc").text
		limited = r.find("span", "limited")
		sold_out = r.find("span", "sold_out")
		if limited:
			limited = re.findall(r"[\d]+", limited.text)
			backers = limited[0]
			limited = limited[1]
		elif sold_out:
			limited = sold_out
			limited = re.findall(r"[\d]+", limited.text)
			backers = limited[0]
			limited = limited[1]
		else:
			backers = r.find("span", "num-backers")
			backers = "".join(re.findall(r"[\d]+", backers.text))
		fields["limited"] = limited
		fields["backers"] = backers
		#insert('rewards', fields)

	mentions = bs.find(id="mentions")

	if(mentions):
		for m in mentions.ul.find_all("li"):
			site = base_url + m.a['href']
			date = datetime.strptime(m.time.text, "%B %d, %Y").date()
			print site
			print date
