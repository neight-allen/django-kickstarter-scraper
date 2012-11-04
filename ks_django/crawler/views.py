# Create your views here.
from django.http import HttpResponse
from crawler.models import *
from datetime import datetime, date
import urllib
import re
import string
from bs4 import BeautifulSoup

def price(reward):
	return reward.price

def cheapestReward(project, word):
	reward = Reward.objects.filter(project=project, text__icontains=word, price__gt=1).order_by("price")
	try:
		rew = reward[0]
		rew.raised = raised(rew)
		if rew.project.raised > 0:
			rew.percent = rew.raised / rew.project.raised
		else:
			rew.percent = 0
		return rew
	except IndexError:
		return None
def raised(reward):
	return reward.price * reward.backers

def backers(reward):
	return reward.backers

def average(values):
    return sum(values, 0.0) / len(values)

def createWordCloud(objects):
	ignore = [
		'in',
		'as',
		'a',
		'the',
		'and',
		'to',
		'of',
		'for',
		'be',
		'with',
		'this',
		'have',
		'it',
		'on',
		'an',
		'at',
		'is',
		'are',
		'by',
		'-',
	]
	words = {}
	wordCount = 0
	for proj in objects:
		
		for word in proj.about.lower().split():
			wordCount += 1
			if word in ignore:
				continue
			if word in words:
				words[word] += 1
			else:
				words[word] = 1
	printWords = []
	for word in sorted(words, key=words.get, reverse=True):
  		printWords.append(word + ': ' + str(words[word]) + " (" + str((words[word]/wordCount) * 100) + "%)")
  	return printWords

def createReWordCloud(objects):
	ignore = [
		'in','as','a',
		'the','and','to','of',
		'for','be','with',
		'this','have','it',
		'on','an','at','is',
		'are','by','-',
		'you','we','i','will',
		'all','get','or',
		'receive','our','plus',
		'one','from','also','+',
		'plus','add','shipping',
		'international','can','above',
		'if','us','please','reward',
		'not','pledge','only','your',
		'youll','1','2','3',
		'included','above,', '&',
		'own','that','two','three',
		'previous','everything','my',
		'x','any','well','set',
		'out','me','project','well',
		'send'
	]
	words = {}
	wordCount = 0
	for rew in objects:
		
		for word in re.sub('[%s]' % re.escape(string.punctuation), '', rew.text).lower().split():
			wordCount += 1
			if word in ignore or len(word) < 2:
				continue
			if word in words:
				words[word] += 1
			else:
				words[word] = 1
	printWords = []
	for word in sorted(words, key=words.get, reverse=True):
  		printWords.append(word + ': ' + str(words[word]) + " (" + str((words[word]/wordCount) * 100) + "%)")
  	return printWords

def wordcloud(request):
	allProjects = Project.objects.filter(date_end__lt=date(2012,5,25))[:30000]
	successfulProjects = []
	unsuccessfulProjects = []
	videoGameProjects = []
	fashionProjects = []
	for proj in allProjects:
		if proj.goal < proj.raised:
			successfulProjects.append(proj)
		else:
			unsuccessfulProjects.append(proj)
		if proj.category == "Video Games":
			videoGameProjects.append(proj)
		if proj.category == "Fasion":
			fashionProjects.append(proj)

	response = "<table><tr>"
	response += "<td>All Projects:(" + str(len(allProjects)) + ")<br>"
	response += "<br>".join(createWordCloud(allProjects)[:50])

	response += "</td><td>Successful Projects:(" + str(len(successfulProjects)) + ")<br>"
	response += "<br>".join(createWordCloud(successfulProjects)[:50])

	response += "</td><td>Unsuccessful Projects:(" + str(len(unsuccessfulProjects)) + ")<br>"
	response += "<br>".join(createWordCloud(unsuccessfulProjects)[:50])
	
	response += "</td><td>Video Game Projects:(" + str(len(videoGameProjects)) + ")<br>"
	response += "<br>".join(createWordCloud(videoGameProjects)[:50])

	response += "</td><td>Fashion Projects:(" + str(len(fashionProjects)) + ")<br>"
	response += "<br>".join(createWordCloud(fashionProjects)[:50])
	response += "</td></tr></table>"

	return HttpResponse(response)

def rewordcloud(request, category=None):
	allRewards = Reward.objects.filter(project__date_end__lt=date(2012,5,25)).order_by('?')
	allRewards = allRewards.select_related('project')
	if(category):
		allRewards = allRewards.filter(project__parentCat=category).order_by('?')

	allRewards = allRewards[:10000]

	successfulLowRewards = []
	unsuccessfulLowRewards = []
	successfulHighRewards = []
	unsuccessfulHighRewards = []
	for rew in allRewards:
		if rew.project.goal < rew.project.raised:
			if rew.price > 150:
				successfulHighRewards.append(rew)
			else:
				successfulLowRewards.append(rew)
		else:
			if rew.price > 150:
				unsuccessfulHighRewards.append(rew)
			else:
				unsuccessfulLowRewards.append(rew)
		

	response = "<table><tr>"
	response += "<td>All Projects:(" + str(len(allRewards)) + ")<br>"
	response += "<br>".join(createReWordCloud(allRewards)[:50])

	response += "</td><td>Successful $1-$150:(" + str(len(successfulLowRewards)) + ")<br>"
	response += "<br>".join(createReWordCloud(successfulLowRewards)[:50])

	response += "</td><td>Unsuccessful $1-$150:(" + str(len(unsuccessfulLowRewards)) + ")<br>"
	response += "<br>".join(createReWordCloud(unsuccessfulLowRewards)[:50])
	
	response += "</td><td>Successful $151+:(" + str(len(successfulHighRewards)) + ")<br>"
	response += "<br>".join(createReWordCloud(successfulHighRewards)[:50])

	response += "</td><td>Unsuccessful $151+:(" + str(len(unsuccessfulHighRewards)) + ")<br>"
	response += "<br>".join(createReWordCloud(unsuccessfulHighRewards)[:50])
	response += "</td></tr></table>"
	

	return HttpResponse(response)

def priceof(request, word, category=None):

	size = 1000
	#category = None

	if(category):
		allProjects = Project.objects.filter(date_end__lt=date(2012,5,25), reward__text__icontains=word, category=category).order_by('?')[:size]
	else:
		allProjects = Project.objects.filter(date_end__lt=date(2012,5,25), reward__text__icontains=word).order_by('?')[:size]

	successfulRewards = []
	unsuccessfulRewards = []
	successfulPrice = 0
	unsuccessfulPrice = 0
	for proj in allProjects:
		if proj.goal <= proj.raised:
			cheapest = cheapestReward(proj, word)

			if cheapest:
				successfulRewards.append(cheapest)
		else:
			cheapest = cheapestReward(proj, word)
			if cheapest:
				unsuccessfulRewards.append(cheapest)


	
	response = ""
	response += "Avg Successful Price (" + str(len(successfulRewards)) + "): " + str(average(map(price, successfulRewards)))
	response += "<br>Avg Unsuccessful Price (" + str(len(unsuccessfulRewards)) + "): " + str(average(map(price, unsuccessfulRewards)))
	response += "<br>Avg Num of Backers: %f" % average([rew.backers for rew in successfulRewards + unsuccessfulRewards])
	response += "<br>Avg Amount Raised: $" + str(average(map(raised, successfulRewards + unsuccessfulRewards)))
	response += "<br>Avg %% raised: %02.2f%%" % (average([rew.percent for rew in successfulRewards + unsuccessfulRewards]) * 100)

	for rew in successfulRewards:
		proj = rew.project
		response += "<br><a href='%s'>$:%d, B:%d</a>" % (proj.url, rew.price, rew.backers)

	return HttpResponse(response)

def report(request, category, amount):

	top = float(amount) * 1.1
	bot = float(amount) * 0.9
	projects = Project.objects.filter(goal__gte=bot, goal__lte=top, category=category)[:1000]

	successRate = 0.0
	for proj in projects:
		successRate += int(proj.goal <= proj.raised)

	successRate /= len(projects)

	response = ""
	response += "Success Rate of " + str(len(projects)) + " Projects: " + str(round(successRate*100,1)) + "%"
	return HttpResponse(response)

def index(request):
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

	return HttpResponse(response)