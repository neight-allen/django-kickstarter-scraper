django-kickstarter-scraper
==========================

Scrapes kickstarter and stores to a mySQL database using django. This was a fun project, but I don't have any plans to update this. I'll be watching for pull requests.

As of early july 2013, its functional, but poorly documented, and probably written all wrong. I had used very little django or even python prior to this project. This project was supposed to teach me more about both, and it has.

###Installation
I'm writing all this from memory. If I'm missing steps, please add them. Or just make it smarter ;)

Needs a bunch of libaries to work. This may help:

`easy_install django south django-tastypie BeautifulSoup4 urllib2 termcolor`
  
Like any other django app, you'll need to set up a database. The current settings file is expecting a mySQL database named kickscrape on localhost. Don't forget to sync the database.

`python manage.py syncdb`

There might be a way for python to create files before writing to them, but I don't know it. Run these from root of the django structure. The same folder as the manage.py.

```
mkdir logs
cd logs
touch full.log process.log queue.log url.log error.log
```
  
South might require some additional stuff. I don't remember. You can always disable it in the enabled apps section of settings. Or check it out [here](http://south.readthedocs.org/en/latest/)

####DB dump

Here's a DB dump from my last scrape. It has 87K projects that you won't have to download. You'll still have to seed it with search pages in the URLQueue table.

[Kickscrape DB Dump](https://docs.google.com/file/d/0Bx11M2JmRNl5RlB5Vm1MUUZWbjg/edit?usp=sharing)

###Use
This command starts the scraper

`python manage.py kickthreads`
  
This command stops the scrper

`python manage.py stopscrape`

The scraper runs until the URLQueue table is empty. This also means that you need to fill said table with kickstarter URLs. Search pages or project pages work best.

###Other Notes
* Pretty much everything happens in that one kickthreads file. If I knew more about python, I'd probably break it out into modules.
* Supports the following pages: Projects, Project Backers, Backer Profiles, Search Results
* Doesn't support the home page or curator pages or any others you can find. Yet ;)
* The last time I ran it was in May 2013. Kickstarter periodically changes their HTML, and it's likely some of the parsing will need to be rewritten
