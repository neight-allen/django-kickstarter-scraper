import urllib
from bs4 import BeautifulSoup

# open local/remote url

def get_data(url, local):
   if (local) :
      return open(url)
   else :
      return urllib.urlopen(url)


local = False
base_url = "http://www.apress.com"
deal_url = base_url + '/info/dailydeal'

# local testing
#deal_url = "c:\\mycode\\dailydeal2.htm"   
#data = open(deal_url)

# remote url
data = get_data(deal_url, local)

bs = BeautifulSoup(data)

# screen-scrape the following  HTML fragment
# to get book name, book description
'''<div class="bookdetails">

 <h3><a href="http://www.apress.com/book/view/1590592778">The Definitive Guide to Samba 3</a></h3>

 <div class="cover"><a href="http://www.apress.com/book/view/1590592778"><img src="dailydeal2_files/9781590592779.gif" alt="The Definitive Guide to Samba 3" align="left" border="0" width="125"></a></div>

 <p>Samba
is an efficient file and print server that enables you to get the most
out of your computer hardware. If you're familiar with Unix
administration, TCP/IP networking, and other common Unix servers, and
you want to learn how to deploy the forthcoming revision of Samba, this
book is ideal for you. </p><div class="footer">$49.99 | Published Apr 2004 | Roderick W. Smith</div>

</div>
'''

book = bs.findAll(attrs= {"class" : "bookdetails"})
a = book[0].h3.find('a')

# grab URL to get book details later
rel_url = a.attrs[0][1]
abs_url_book_det = base_url + rel_url

# extract book name
book_name = a.contents[0]   # just 1 name
print "Today's Apress $10 Ebook Deal:"
print book_name.encode('utf-8')

# extract book description
desc = book[0].p
print desc.contents[0] +  '\n'

#extract book details

# local testing
#abs_url_book_det = "c:\\mycode\\bookdetails.htm"
#details  = open(abs_url_book_det)

# remote url
details = get_data(abs_url_book_det, local)
bs      = BeautifulSoup(details)

# screen-scrape the following  HTML fragment
# to get book details
'''<div class="content" style="padding: 10px 0px; font-size: 11px;">

   <a href="http://www.apress.com/book/view/9781590599419"><img src="bookdetails_files/9781590599419.gif" class="centeredImage" alt="Practical DWR 2 Projects book cover" border="0"></a>
   <ul class="bulletoff">

   <li>By Frank  Zammetti </li>
   <li>ISBN13: 978-1-59059-941-9</li>
   <li>ISBN10: 1-59059-941-1</li>
   <li>540 pp.</li>

   <li>Published Jan 2008</li>
      <li>eBook Price: $32.89</li>
   <li>Price: $46.99</li>
'''

det     = bs.find(attrs={"class" : "content"})

ul      = det.find('li')
while (ul.nextSibling <> None):

   if (ul == '\n') :
      ul = ul.nextSibling
      continue
   line = ul.contents[0]
   if line.startswith('eBook') :
      print line + str(ul.contents[2])
   else:
      print line.encode('utf-8')
   ul = ul.nextSibling