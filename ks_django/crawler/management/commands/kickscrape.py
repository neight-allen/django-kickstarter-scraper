from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from crawler.models import *
from datetime import datetime, date
import urllib
import re
import sys
from bs4 import BeautifulSoup

def next_backer_or_project():
	base_url = "http://www.kickstarter.com"
	if Wproject.objects.all():
		nextProject = Wproject.objects.all()[0]
		nextURL = nextProject.url
		nextProject.delete()
		return nextURL
	else:
		if Cursor.objects.filter(id=1):
			c = Cursor.objects.get(id=1)
			new_backer_id = c.backer.id + 1
			if Backer.objects.filter(id__gt=c.backer.id)[0]:
				new_backer = Backer.objects.filter(id__gt=c.backer.id)[0]
				c.backer = new_backer
				c.save()
				return base_url + '/profiles/' + new_backer.username + "/projects/backed"
			else:
				return None
		else:
			c = Cursor()
			c.backer = Backer.objects.get(id=1)
			c.save()
			return base_url + '/profiles/' + c.backer.username + "/projects/backed"

		new_backer_id = Backer.object.get(id = c.backer.id) + 1
		if Backer.object.filter(id = new_backer_id):
			username = Backer.object.get(id = new_backer_id).username
			return base_url + '/profiles/' + username + "/projects/backed"
		else:
			return None

class Command(BaseCommand):

	def handle(self, *args, **options):
		base_url = "http://www.kickstarter.com"
		url = next_backer_or_project()

		while url:
			bs = BeautifulSoup(urllib.urlopen(url))

			if(re.search(r"/backers", url)): #backers url. Scan for new profiles, and add backers to projects
				projurl = re.search(r"^(.+)/backers", url)
				try:
					proj = Project.objects.get(url=projurl.group(1))
				except:
					print url
					raise

				backers_added = 0
				for b in bs.body.find(id="leftcol").find_all("div", "NS-backers-backing-row"):
					username = b.a['href'][8:]
					if Backer.objects.filter(username = username):
						thisBacker = Backer.objects.get(username = username)
						thisBacker.project.add(proj)
					else:
						try:
							proj.backer_set.create(username = username)
							backers_added += 1
						except IntegrityError:
							thisBacker = Backer.objects.get(username = username)
							thisBacker.project.add(proj)
							print "Adding project to existing backer"
						except:
							print "Something went wrong while adding " + username
							raise
				remaining = proj.backers - Backer.objects.filter(project = proj).count()
				response = str(backers_added) + " Backers Added. " + str(remaining) + " remaining." 
				if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
					next = bs.body.find("div", "pagination").find("a", "next_page")
					url = base_url + next["href"]
				else:
					proj.finished = True
					proj.save()
					url = next_backer_or_project()


			elif(re.search(r"/profile", url)): #profile url. Scan for new projects
				projects_added = 0
				for thumb in bs.body.find_all("div", "project-thumbnail"):
					projURL = base_url + thumb.a["href"].split('?')[0]
					if Wproject.objects.filter(url=projURL) or Project.objects.filter(url=projURL):
						pass
					else:
						newProj = Wproject()
						newProj.url = projURL
						newProj.save()
						projects_added += 1
				response = str(projects_added) + " Projects Added"
				if bs.body.find("div", "pagination") and bs.body.find("div", "pagination").find("a", "next_page"):
					next = bs.body.find("div", "pagination").find("a", "next_page")
					url = base_url + next["href"]
				else:
					url = next_backer_or_project()


			else:
				fields = {}

				propNames = {
					"latitude" : "kickstarter:location:latitude",
					"longitude" : "kickstarter:location:longitude",
				}

				for propName in propNames:
					propTag = bs.find("meta", {"property": propNames[propName]})
					if(propTag):
						fields[propName] = propTag['content']
					else:
						fields[propName] = 0

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
				if Wproject.objects.filter(url=proj.url) or Project.objects.filter(url=proj.url):
					url = next_backer_or_project()
					continue
				else:
					try:
						proj.save()
					except IntegrityError:
						print proj.name + " already Exists, moving on"
						url = next_backer_or_project()
						continue
					except:
						print "proj.about:"
						print proj.about
						print "about:"
						print about
						print "raw about div:"
						print bs.body.find(id="about")
						raise



				rewards = bs.find_all("div", "NS-projects-reward") 

				for r in rewards:
					fields = {}
					try:
						fields["amount"] = "".join(re.findall(r"[\d]+", r.h3.span.text)) #reward amount
					except:
						print "Body:"
						print bs.body
						print "Rewards:"
						print rewards
						raise
					fields["text"] = r.find("div", "desc").p.text.strip()
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
					try:
						rew.save()
					except:
						print "rew.text:"
						print rew.text
						print "raw desc div:"
						print r.find("div", "desc").p.text.strip()
						raise


				mentions = bs.find(id="mentions")

				if(mentions):
					for m in mentions.ul.find_all("li"):
						ment = Mention()
						ment.project = proj
						ment.url = base_url + m.a['href']
						ment.date = datetime.strptime(m.time.text, "%B %d, %Y").date()
						ment.save()
				response = proj.name + " Added"

				url = url + "/backers/"
			print response