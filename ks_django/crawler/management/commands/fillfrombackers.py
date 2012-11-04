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

def backer_url(username):
	return "http://www.kickstarter.com/profiles" + username + "/projects/backed"

class Command(BaseCommand):

	def handle(self, *args, **options):
		backer_list = [
			'/1004208496',
			'/1007756037',
			'/1007941078',
			'/1011082370',
			'/1024928080',
			'/1025037299',
			'/1025061590',
			'/1031497676',
			'/1031702113',
			'/1036591063',
			'/1042707970',
			'/1043291769',
			'/1062888664',
			'/1063534031',
			'/1064083090',
			'/1077090731',
			'/1079242157',
			'/107957479',
			'/1084149886',
			'/108629152',
			'/1094168470',
			'/1094974452',
			'/1103894052',
			'/1108044507',
			'/1108322963',
			'/1108616525',
			'/1113188370',
			'/1116575730',
			'/1121896228',
			'/1133270546',
			'/1133945043',
			'/1134919383',
			'/1135300767',
			'/1139276107',
			'/11400078',
			'/1142162776',
			'/1146186734',
			'/1146677432',
			'/1146682330',
			'/1150234493',
			'/1155118169',
			'/1157377930',
			'/1163387690',
			'/1164307822',
			'/1167229170',
			'/1173881877',
			'/1174324007',
			'/1176214633',
			'/1177834213',
			'/1184479237',
			'/1188185710',
			'/1190307198',
			'/119650928',
			'/1197007774',
			'/1200781161',
			'/120114979',
			'/1201314857',
			'/1210088781',
			'/1210629512',
			'/1211463193',
			'/121403279',
			'/121973726',
			'/122316642',
			'/1230931706',
			'/1232802877',
			'/123525026',
			'/1239787122',
			'/1241061775',
			'/1246887277',
			'/124884966',
			'/1249220824',
			'/1253203485',
			'/1254750512',
			'/1255331',
			'/1256868662',
			'/1259145952',
			'/126298461',
			'/1268306454',
			'/1280514659',
			'/1280651859',
			'/1282532532',
			'/1290485468',
			'/1298780195',
			'/1301513886',
			'/1302442300',
			'/1308739287',
			'/1323902523',
			'/1324172866',
			'/1325851543',
			'/132824330',
			'/1333462652',
			'/1355436407',
			'/1355716601',
			'/1357358714',
			'/136594524',
			'/1371654935',
			'/1372587727',
			'/1374269530',
			'/1381237155',
			'/1392959447',
			'/1395358767',
			'/1395592997',
			'/1398391146',
			'/1399582550',
			'/1403520865',
			'/1404133720',
			'/1406687619',
			'/1407662333',
			'/1416169813',
			'/141714957',
			'/1417592187',
			'/1424918531',
			'/1431734304',
			'/143377077',
			'/1434228782',
			'/1442978326',
			'/1447880733',
			'/1448774299',
			'/1450495178',
			'/1451415134',
			'/1457221376',
			'/1457907747',
			'/1460165270',
			'/1462433405',
			'/1467162087',
			'/1467439182',
			'/1472490290',
			'/1477109939',
			'/1479801753',
			'/1484308359',
			'/1486371952',
			'/1491312943',
			'/1495338205',
			'/149667184',
			'/150615619',
			'/1507412675',
			'/1514310712',
			'/1519872970',
			'/1519983660',
			'/1523050323',
			'/1524809338',
			'/1527006350',
			'/1527727539',
			'/1537147755',
			'/1537519525',
			'/1543056132',
			'/1545822764',
			'/1548491474',
			'/1549245392',
			'/1554438351',
			'/1556075252',
			'/1560820757',
			'/1562011924',
			'/1562051344',
			'/15660673',
			'/1566305124',
			'/1569833538',
			'/1575215485',
			'/1578175213',
			'/1581872848',
			'/1583317097',
			'/1585332996',
			'/1585992056',
			'/1593089148',
			'/1594215904',
			'/1595294744',
			'/1598920392',
			'/160304027',
			'/1603561501',
			'/1610752796',
			'/1616742829',
			'/1619687394',
			'/1626697734',
			'/1632570719',
			'/1635114825',
			'/1636150079',
			'/1636188424',
			'/1637746501',
			'/1640482173',
			'/164921645',
			'/1651042205',
			'/1654225676',
			'/1655080005',
			'/1658882280',
			'/1659045115',
			'/1660706255',
			'/1664710572',
			'/1666063850',
			'/1668019696',
			'/1671741598',
			'/1672325197',
			'/167283466',
			'/1676592943',
			'/1677815106',
			'/1682341284',
			'/1685802134',
			'/1695594338',
			'/1697761431',
			'/1702250484',
			'/1703847313',
			'/1709031469',
			'/1709498118',
			'/1716326010',
			'/1718596194',
			'/1720425556',
			'/1724624164',
			'/1729148993',
			'/1730719369',
			'/1738320637',
			'/1744871690',
			'/1751605028',
			'/1751648904',
			'/1753684605',
			'/1758111689',
			'/1760446066',
			'/1761386332',
			'/1765023016',
			'/1765904422',
			'/1767698174',
			'/1771188855',
			'/1781270190',
			'/1794830531',
			'/1799437372',
			'/1801444531',
			'/1804993557',
			'/1807019985',
			'/1807353924',
			'/181365860',
			'/1813772851',
			'/1836456386',
			'/1837066228',
			'/1839879969',
			'/184086151',
			'/1842039760',
			'/1844119445',
			'/1844685721',
			'/1844716191',
			'/1845351721',
			'/1849397482',
			'/1855113134',
			'/185773163',
			'/1862965313',
			'/1867230178',
			'/1881183454',
			'/1881960471',
			'/1888800665',
			'/1890305050',
			'/18908095',
			'/189156593',
			'/189916285',
			'/1900249320',
			'/1902430796',
			'/1913017008',
			'/1914170276',
			'/1914610737',
			'/1917058769',
			'/1918686174',
			'/191951205',
			'/1923130018',
			'/1924036987',
			'/1927045122',
			'/1929795078',
			'/1930472895',
			'/1931941727',
			'/1937991130',
			'/1941943462',
			'/1941955964',
			'/1946217005',
			'/1950031841',
			'/1954366413',
			'/1957830349',
			'/1961184375',
			'/1961961511',
			'/196558591',
			'/197134191',
			'/1973447439',
			'/1973731658',
			'/1978532998',
			'/1984605424',
			'/1984742805',
			'/1993307051',
			'/199366907',
			'/1996870303',
			'/2003896987',
			'/2006182855',
			'/2010830272',
			'/2012328520',
			'/2019080643',
			'/2020133779',
			'/2026780525',
			'/2028238746',
			'/2029379451',
			'/2033480019',
			'/2035234108',
			'/2037946385',
			'/2038885098',
			'/2039461278',
			'/2042155052',
			'/2048393942',
			'/205204938',
			'/2052656801',
			'/2052995090',
			'/205708506',
			'/2058990948',
			'/2062707256',
			'/2066077255',
			'/206615392',
			'/2068026266',
			'/2068638719',
			'/2070249666',
			'/2073219127',
			'/2073232695',
			'/2076723463',
			'/2083686541',
			'/2085868048',
			'/208965156',
			'/2089717097',
			'/209296035',
			'/2095320665',
			'/2098207945',
			'/2098242263',
			'/2098329762',
			'/2098872598',
			'/209904713',
			'/2100973237',
			'/2121208252',
			'/2122451331',
			'/2123116592',
			'/2124402016',
			'/2126285425',
			'/2132118857',
			'/2133537347',
			'/2133716708',
			'/2135277579',
			'/2137182295',
			'/2137261389',
			'/2137586230',
			'/2142747647',
			'/2143084258',
			'/216976262',
			'/217744267',
			'/22213900',
			'/229340548',
			'/235504521',
			'/240823425',
			'/244194624',
			'/245696375',
			'/247661276',
			'/248162944',
			'/249198508',
			'/255086237',
			'/256200161',
			'/257964139',
			'/258350017',
			'/260483802',
			'/261404198',
			'/263551599',
			'/264573595',
			'/264767489',
			'/266486170',
			'/267449562',
			'/269314320',
			'/273297809',
			'/279140237',
			'/281933632',
			'/288998067',
			'/29402869',
			'/296634835',
			'/304376579',
			'/307573276',
			'/309441405',
			'/313593224',
			'/314118605',
			'/318414018',
			'/322613074',
			'/325112552',
			'/326368500',
			'/33277513',
			'/333104691',
			'/335178166',
			'/341366973',
			'/341839352',
			'/341984809',
			'/343711182',
			'/345267495',
			'/345971450',
			'/346215787',
			'/349632140',
			'/3511332',
			'/35132645',
			'/355107218',
			'/357102651',
			'/363502227',
			'/364124026',
			'/367677288',
			'/367990778',
			'/368090025',
			'/371326895',
			'/371798438',
			'/372652651',
			'/37275098',
			'/378774366',
			'/385003071',
			'/390318391',
			'/391075868',
			'/396414543',
			'/400044046',
			'/401880215',
			'/420122543',
			'/426926503',
			'/429894982',
			'/43087991',
			'/431236220',
			'/437561931',
			'/445104399',
			'/448265184',
			'/450872620',
			'/450916418',
			'/45378584',
			'/458217901',
			'/460019832',
			'/466409009',
			'/466686584',
			'/472481402',
			'/472825514',
			'/478898899',
			'/480285735',
			'/485150195',
			'/489105615',
			'/490718624',
			'/502573223',
			'/503461731',
			'/504746139',
			'/506170609',
			'/509139134',
			'/510403516',
			'/512114450',
			'/519149853',
			'/520192805',
			'/52068849',
			'/524063108',
			'/52501465',
			'/531773988',
			'/535417422',
			'/537354043',
			'/551427224',
			'/551454666',
			'/554666478',
			'/555695439',
			'/556628777',
			'/558286155',
			'/562260252',
			'/566824200',
			'/578014700',
			'/589868626',
			'/5920763',
			'/594261704',
			'/599275051',
			'/600367789',
			'/604147666',
			'/605719333',
			'/606571395',
			'/610894019',
			'/614071520',
			'/615930224',
			'/617880293',
			'/618690249',
			'/624112695',
			'/643297192',
			'/647818722',
			'/657340954',
			'/657899059',
			'/661324603',
			'/663727372',
			'/666418257',
			'/666511809',
			'/672216542',
			'/673180757',
			'/679643240',
			'/685277882',
			'/685515515',
			'/687180231',
			'/700292136',
			'/700649122',
			'/701822901',
			'/706451770',
			'/708114748',
			'/714422620',
			'/71466571',
			'/721433325',
			'/721528322',
			'/724922710',
			'/726414539',
			'/7280135',
			'/729171262',
			'/729516305',
			'/730939783',
			'/731938587',
			'/737771419',
			'/738039519',
			'/739918532',
			'/741585929',
			'/744175843',
			'/744503674',
			'/748399949',
			'/759310116',
			'/761410869',
			'/765557157',
			'/766090572',
			'/767053832',
			'/769268217',
			'/77142331',
			'/77170858',
			'/780781193',
			'/783861385',
			'/786920276',
			'/795050980',
			'/799701494',
			'/799715502',
			'/799764355',
			'/801870568',
			'/806492178',
			'/807080474',
			'/809310759',
			'/814717131',
			'/822089078',
			'/830202652',
			'/835761524',
			'/837261686',
			'/840535252',
			'/841442646',
			'/847145696',
			'/849809668',
			'/852944246',
			'/85366152',
			'/856792009',
			'/85763696',
			'/860179029',
			'/860562524',
			'/867907736',
			'/878565859',
			'/878775693',
			'/879824901',
			'/880371065',
			'/884230359',
			'/900523365',
			'/901258627',
			'/902977912',
			'/905139298',
			'/905567919',
			'/92342836',
			'/927829618',
			'/928731338',
			'/931943446',
			'/93600237',
			'/936371788',
			'/938059198',
			'/943905344',
			'/948058249',
			'/952540461',
			'/953467510',
			'/957536571',
			'/962405061',
			'/964403266',
			'/968265467',
			'/969750783',
			'/970078748',
			'/983312432',
			'/983931103',
			'/986639431',
			'/98813937',
			'/994122008',
			'/994449179',
			'/9956287',
			'/999379575',
			'/airsports',
			'/aldie',
			'/alexkoti',
			'/alexlucard',
			'/alexstrang',
			'/alika',
			'/alow',
			'/alwayslookaround',
			'/amaquieria',
			'/amotion',
			'/angiekh',
			'/araven',
			'/arkie',
			'/arturs',
			'/ashtarasilunar',
			'/asubhani',
			'/atannir',
			'/atarun',
			'/aweissman',
			'/baudot',
			'/beaugunderson',
			'/becoming',
			'/bellawonder',
			'/bigtony',
			'/blink',
			'/bma',
			'/bmeaker',
			'/boonerang',
			'/bqk',
			'/brandy',
			'/brennerbeer',
			'/brett',
			'/brett24',
			'/buddah',
			'/cadler',
			'/cainlevy',
			'/cameo',
			'/camrncrazy',
			'/canvas',
			'/carlcollins',
			'/cassiem',
			'/catone',
			'/chapman',
			'/chowe',
			'/chrisbutler',
			'/chrischarlton',
			'/cinchel',
			'/cindy',
			'/cinejoe',
			'/clevermojogames',
			'/cmagnuson',
			'/compelledorphan',
			'/conordempsey',
			'/cooper',
			'/corriedavidson',
			'/court',
			'/dagmarwm',
			'/dallasartssalon',
			'/daneen',
			'/daniellajaeger',
			'/danlazar',
			'/dariengee',
			'/darkwind187',
			'/daryn',
			'/davelecompte',
			'/davli',
			'/dcell59',
			'/demarko',
			'/derik',
			'/deviousgoldfish',
			'/devonsputant',
			'/devotee',
			'/dinosaur',
			'/disquietnight',
			'/divnull',
			'/djcrazycraig',
			'/dmcgauley',
			'/dominik',
			'/dpamlin',
			'/Dragyn',
			'/draper',
			'/drenieves',
			'/drewish',
			'/duaiwe',
			'/duncan',
			'/dustinsharpless',
			'/dustywhite',
			'/dylankurtz',
			'/elenamurphy',
			'/elisabeth',
			'/era',
			'/eri',
			'/eric73',
			'/ericalvarado',
			'/EricDamonWalters',
			'/ericg',
			'/ericjohnson',
			'/ericsmithrocks',
			'/EricStriffler',
			'/evilhat',
			'/farmisen',
			'/featherwise',
			'/felyn',
			'/forbeck',
			'/fred',
			'/frosty',
			'/garyploski',
			'/georgechiesa',
			'/ggarb',
			'/ghostcode',
			'/gleneivey',
			'/gmf',
			'/goodness',
			'/goodyerin',
			'/gorbash',
			'/granddevil',
			'/gregd',
			'/grel',
			'/grid',
			'/grking',
			'/grue',
			'/guttermonkey',
			'/gwen',
			'/halcyon',
			'/hdellamanna',
			'/herostyle',
			'/hershberg',
			'/hezz',
			'/hoekstra',
			'/hoodablah',
			'/horizonfactory',
			'/hybridvigor',
			'/iankragh',
			'/ingrid',
			'/inkyphoenix',
			'/intemperiae',
			'/Jagash',
			'/jakemckee',
			'/jamesriggall',
			'/jared',
			'/javajoe96',
			'/jazcat',
			'/jcolag',
			'/jdaysy',
			'/jdherg',
			'/jeffdinkins',
			'/jeremydouglass',
			'/jgoethals',
			'/jhliu',
			'/jjtiziou',
			'/jlariviere',
			'/jnjitkoff',
			'/joanm',
			'/joedp',
			'/johneternal',
			'/johnweidner',
			'/jonathanwash',
			'/jstylman',
			'/juliaz',
			'/justinchung',
			'/jzimbabwe',
			'/kajita',
			'/karolgajda',
			'/kartar',
			'/kaysindre',
			'/kccr',
			'/kcunning',
			'/kelb',
			'/kenn',
			'/kentkb',
			'/kgagne',
			'/kidincredible',
			'/kingkeith',
			'/kishimoto',
			'/kitt',
			'/kpjackson',
			'/krishaamer',
			'/lastandroid',
			'/launderground',
			'/leonardr',
			'/leos',
			'/lewiswinter',
			'/lindyandkris',
			'/listato',
			'/litmanlive',
			'/llin',
			'/luxdewakari',
			'/majcher',
			'/mamojo',
			'/mana',
			'/mariac',
			'/markderail',
			'/mathowie',
			'/mattpatt',
			'/mbbatz',
			'/mbrandonw',
			'/mcgill',
			'/mchwinder',
			'/meagancignoli',
			'/meaghano',
			'/mervae',
			'/mikaelo',
			'/mikehedge',
			'/mikejt',
			'/mikekn',
			'/mikelietz',
			'/mikeprasad',
			'/mikolajl',
			'/miles-matton',
			'/milkweed',
			'/minhittowinit',
			'/moiraclunie',
			'/mollems',
			'/movieactor',
			'/mrudat',
			'/mscala',
			'/mstum',
			'/muneeramak',
			'/myllyluoma',
			'/natasqi',
			'/netboy',
			'/netsabes',
			'/neverevergiverupper',
			'/nicholascroft',
			'/nickd',
			'/nickgagalis',
			'/nicole',
			'/nicoles',
			'/nikolaibroxz',
			'/nmontgom',
			'/ohbalto',
			'/olorin',
			'/omahdon',
			'/omfa',
			'/overflowcafe',
			'/padawer',
			'/panacirema',
			'/patmanta',
			'/patrickstrange',
			'/paynie',
			'/perry',
			'/petrilli',
			'/phacin8ing',
			'/philomath',
			'/polar',
			'/proboliving',
			'/pyrowolf',
			'/rabt',
			'/raines',
			'/raistlyne',
			'/ralfh',
			'/rambo',
			'/redwood',
			'/rejectedmuse',
			'/restorationmedia',
			'/richmccomas',
			'/rifter',
			'/ringmaster',
			'/robinsloan',
			'/rocknrollgeek',
			'/rockshainkjr',
			'/ronfink',
			'/rosalieinc',
			'/rusdude',
			'/rwdederick',
			'/ryanbkoo',
			'/samuelcole',
			'/sarahjoan78',
			'/schun',
			'/scotthughes',
			'/seanmeagher',
			'/sembiance',
			'/shackett',
			'/shashinbeauty',
			'/shervyn',
			'/sitgo',
			'/sitouh',
			'/sjoerdadding',
			'/skajawills',
			'/smudge',
			'/snailbird',
			'/snowything',
			'/st3phani3',
			'/stadam',
			'/stephancom',
			'/stepheneckman',
			'/strutter',
			'/supremedef',
			'/suzieqsailaway',
			'/swelsh20',
			'/tabacco',
			'/tamok',
			'/terencebowlby',
			'/textfiles',
			'/thatguy',
			'/thechosenone',
			'/themockturtle',
			'/TheQwerty',
			'/theremina',
			'/thereport',
			'/thi3d-com',
			'/tiegz',
			'/tikilovegod',
			'/torusJKL',
			'/trekspert1',
			'/trents',
			'/triwizard',
			'/tromblee',
			'/tshow',
			'/tysonyoung',
			'/userclone',
			'/verkisto',
			'/vob',
			'/waxpancake',
			'/wccrawford',
			'/wcoburn',
			'/webwidejosh',
			'/whitneymcn',
			'/wileywiggins',
			'/xorlor',
			'/yaffa',
			'/yancey',
			'/yetiworks',
			'/yumeji',
			'/zabezapf',
			'/zacksears',
			'/zael',
			'/zucky',
		]
		bi = 0;
		base_url = "http://www.kickstarter.com"
		url = backer_url(backer_list[bi])

		while url:
			bs = BeautifulSoup(urllib.urlopen(url))

			if(re.search(r"/backers", url)): #backers url. Scan for new profiles, and add backers to projects
				projurl = re.search(r"^(.+)/backers", url)
				proj = Project.objects.get(url=projurl.group(1))
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
					bi+=1
					url = backer_url(backer_list[bi])


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