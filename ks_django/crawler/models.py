from django.db import models

# Create your models here.
class Project(models.Model):
	url = models.URLField(unique=True)
	name = models.CharField(max_length=255, default='')
	backers = models.IntegerField(default = 0)
	parentCat = models.CharField(max_length=255)
	category = models.CharField(max_length=255)
	duration = models.FloatField(default = 0)
	date_end = models.DateTimeField()
	goal = models.FloatField()
	raised = models.FloatField()
	lat = models.FloatField()
	lon = models.FloatField()
	about = models.TextField()
	faqs = models.IntegerField()
	comments = models.IntegerField()
	date_scanned = models.DateTimeField(auto_now=True, blank=True)
	finished = models.BooleanField(default=False)

	def __unicode__(self):
		return self.name

class Reward(models.Model):
	project = models.ForeignKey(Project, related_name='rewards')
	price = models.IntegerField()
	backers = models.IntegerField()
	limited = models.IntegerField(blank=True)
	text = models.TextField()

	def __unicode__(self):
		return "$" + self.price

class Mention(models.Model):
	project = models.ForeignKey(Project)
	url = models.URLField()
	date = models.DateField()

	def __unicode__(self):
		return self.url	

class Backer(models.Model):
	username = models.CharField(max_length=255, unique=True)
	project = models.ManyToManyField(Project)
	backed = models.IntegerField(default = 0)
	location = models.CharField(max_length=255, default="")
	name = models.CharField(max_length=255, default="")

	def __unicode__(self):
		return self.username

class Sites(models.Model):
	backer = models.ForeignKey(Backer)
	url = models.URLField()

class Cursor(models.Model):
	backer = models.ForeignKey(Backer)

class Wproject(models.Model):
	url = models.URLField()

	def __unicode__(self):
		return self.url

class URLQueue(models.Model):
	url = models.URLField()

	def __unicode__(self):
		return self.url		

class URLsDone(models.Model):
	url = models.URLField()

	def __unicode__(self):
		return self.url