from django_bootstrap import bootstrap

bootstrap("ks_django")

from crawler.models import *
from datetime import datetime, date
import urllib
import re
from bs4 import BeautifulSoup

base_url = "http://www.kickstarter.com"
url = "http://www.kickstarter.com/projects/doublefine/double-fine-adventure"
url = "http://www.kickstarter.com/projects/blytherenay/damsels-of-dorkington-2012-season/backers"
#url = "http://www.kickstarter.com/projects/blytherenay/damsels-of-dorkington-2012-season/?ref=live"

bs = BeautifulSoup(urllib.urlopen(url))

waiting_urls = []

scraped_urls = []

profiles = []

if(re.search(r"/backers", url)): #backers url. Scan for new profiles
	projurl = re.search(r"^(.+)/backers", url)
	proj = Project.objects.get(url=projurl.group(1))
	backers_added = 0
	for b in bs.body.find(id="leftcol").find_all("div", "NS-backers-backing-row"):
		username = b.a['href'][8:]
		if not Backer.objects.filter(username = username):
			proj.backer_set.create(username = username)
			backers_added += 1
	response = str(backers_added) + " Backers Added"
	#

elif(re.search(r"/profile", url)): #profile url. Scan for new projects
	for anchor in bs.body.find_all("a"):
		if anchor.has_key("href") and re.match(r"^/projects/[^/]+/[^/]+/", anchor["href"]):
			sub_url = re.match(r"/projects/[^/]+/[^/]+/", anchor["href"])
			proj_url = base_url + sub_url.group(0)
			if proj_url not in all_urls:
				all_urls.append(proj_url)

else:
	fields = {}

	propNames = {
		"latitude" : "kickstarter:location:latitude",
		"longitude" : "kickstarter:location:longitude",
	}

	for propName in propNames:
		propTag = bs.find("meta", {"property": propNames[propName]})
		fields[propName] = propTag['content']

	contentDiv = bs.find("div", {"id":"about", "data-project-state":"successful"})
	contentDiv = bs.body.find(id="about")
	about = []
	for p in bs.body.find(id="about").find_all(["p", "h1", "h2"]):
		about.append(p.text)

	#print "Updates count: " + re.findall(r"[\d]+", bs.body.find(id="updates_count").text)[0]
	#print "Backers: " + re.findall(r"[\d]+", bs.body.find(id="backers_count").text)[0]
	fields["url"] = base_url + bs.body.find(id="name").a['href']
	fields["raised"] = bs.body.find(id="pledged")["data-pledged"]
	fields["goal"] = bs.body.find(id="pledged")["data-goal"]
	fields["faqs"] = len(bs.body.find("ul", "faqs").find_all("li"))
	date_data = bs.body.find(id="project_duration_data")
	fields["date_end"] = date_data["data-end_time"]
	fields["duration"] = date_data["data-duration"]
	cat = bs.body.find(id="project_category")
	fields["category"] = cat["data-project-category"]
	fields["parentCat"] = cat["data-project-parent-category"]
	fields["about"] = contentDiv.text
	fields["name"] = bs.body.find(id="name").text.strip()

	proj = Project()
	proj.url = fields["url"]
	proj.name = fields["name"]
	proj.raised = fields["raised"]
	proj.backers = "".join(re.findall(r"[\d]+", bs.body.find(id="backers_count").text))
	proj.goal = fields["goal"]
	proj.faqs = fields["faqs"]
	proj.date_end = datetime.strptime(fields["date_end"], "%a, %d %b %Y %H:%M:%S -0000")
	proj.duration = fields["duration"]
	proj.category = fields["category"]
	proj.parentCat = fields["parentCat"]
	proj.about = fields["about"]
	proj.about = "\n".join(about)
	proj.lat = fields["latitude"]
	proj.lon = fields["longitude"]
	comments = bs.body.find(id="comments_count").find("span", "count").text
	proj.comments = "".join(re.findall(r"[\d]+", comments))
	proj.save()

	rewards = bs.find_all("div", "NS-projects-reward") 

	for r in rewards:
		fields = {}
		fields["amount"] = "".join(re.findall(r"[\d]+", r.h3.span.text)) #reward amount
		fields["text"] = r.find("div", "desc").text.strip()
		limited = r.find("span", "limited")
		sold_out = r.find("span", "sold-out")
		if limited:
			limited = re.findall(r"[\d]+", limited.text)
			limited = limited[1]
		elif sold_out:
			limited = sold_out
			limited = re.findall(r"[\d]+", sold_out.text)
			limited = limited[1]
		backers = r.find("span", "num-backers")
		backers = "".join(re.findall(r"[\d]+", backers.text))
		fields["limited"] = limited
		fields["backers"] = backers
		rew = Reward()
		rew.project = proj
		rew.price = fields["amount"]
		rew.text = fields["text"]
		rew.backers = fields["backers"]
		if(fields["limited"]):
			rew.limited = fields["limited"]
		rew.save()

	mentions = bs.find(id="mentions")

	if(mentions):
		for m in mentions.ul.find_all("li"):
			ment = Mention()
			ment.project = proj
			ment.url = base_url + m.a['href']
			ment.date = datetime.strptime(m.time.text, "%B %d, %Y").date()
			ment.save()
	response = proj.name + " Added"