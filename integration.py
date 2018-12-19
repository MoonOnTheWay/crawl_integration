from argparse import ArgumentParser
from datetime import date
from goose import Goose
import collections
import mysql.connector
import hashlib
import arxiv
import requests
import time
import json
from goose import Goose
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from rake_nltk import Rake

mydb = mysql.connector.connect(
	  host="128.111.54.55",
	  user="muxu",
	  passwd="8054552162",
	  database="moon_master_project",
	  charset='utf8mb4'
	)
mycursor = mydb.cursor()

headers = requests.utils.default_headers()
headers.update({
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
})

chrome_options = Options()  
chrome_options.add_argument("--headless")  
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
prefs = {'profile.managed_default_content_settings.images':2}
chrome_options.add_experimental_option("prefs", prefs)


def main():
	parser = ArgumentParser()
	#default is crawl daily blogs
	today = str(date.today()).split('-')
	parser.add_argument('-sy', '--START_YEAR',
		default=today[0], help='start year to crawl from')
	parser.add_argument('-ey', '--END_YEAR',
		default=str(int(today[0])), help='end year to crawl from')
	parser.add_argument('-sm', '--START_MONTH',
		default=today[1], help='start month to crawl from')
	parser.add_argument('-em', '--END_MONTH',
		default=str(int(today[1])), help='end month to crawl from')
	parser.add_argument('-sd', '--START_DAY',
		default=today[2], help='start day to crawl from')
	parser.add_argument('-ed', '--END_DAY',
		default=str(int(today[2])), help='end day to crawl from')

	args = parser.parse_args()
	global START_YEAR, END_YEAR, START_MONTH, END_MONTH, START_DAY, END_DAY

	START_YEAR = int(args.START_YEAR)
	END_YEAR = int(args.END_YEAR)
	START_MONTH = int(args.START_MONTH)
	END_MONTH = int(args.END_MONTH)
	START_DAY = int(args.START_DAY)
	END_DAY = int(args.END_DAY)

	# crawl_medium_templates()
	crawl_medium()
	crawl_others()


def crawl_medium():
	tags = []
	url_root = 'https://medium.com/tag/'
	url_xpath = '//div[@class=\'postArticle-readMore\']/a'

	with open('./top_tags_by_blogs_with_linked_papers.json') as f:
		content = json.load(f)
		# crawl top 100 tags
		top_tags = collections.OrderedDict(sorted(content.items(), key=lambda x: x[1], reverse=True)).keys()[:100]
		
		for tag in top_tags:
			for year in range(START_YEAR, END_YEAR + 1):
				year_str = convert_number_to_str(year)
				path = url_root + tag + '/archive/' + year_str
				if check_redirect(path):
					continue
				
				for month in range(START_MONTH, END_MONTH + 1):
					month_str = convert_number_to_str(month)
					path = url_root + tag + '/archive/' + year_str + '/' + month_str
					if check_redirect(path):
						continue
				
					for day in range(START_DAY, END_DAY + 1):
						day_str = convert_number_to_str(day) 
						# check if the day exists
						path = url_root + tag + '/archive/' + year_str + '/' + month_str + '/' + day_str
						if check_redirect(path):
							continue
						crawl_by_day(url_root + tag + '/archive/', url_xpath, year_str, month_str, day_str)

def crawl_medium_templates():
	URL_LIST = [
		'https://towardsdatascience.com',
		'https://hackernoon.com',
		'https://becominghuman.ai',
		'https://medium.freecodecamp.org',
		'https://medium.com/neuromation-io-blog',
		'https://blog.slavv.com',
		'https://codeburst.io',
		'https://ayearofai.com',
		'https://machinelearnings.co'
	]

	url_xpath = '//div[@class=\'postArticle-readMore\']/a'

	for url_root in URL_LIST:
		for year in range(START_YEAR, END_YEAR + 1):
			year_str = convert_number_to_str(year)
			path = url_root + '/archive/' + year_str
			if check_redirect(path):
				continue

			for month in range(START_MONTH, END_MONTH + 1):
				month_str = convert_number_to_str(month)
				path = url_root + '/archive/' + year_str + '/' + month_str
				if check_redirect(path):
					continue
				
				for day in range(START_DAY, END_DAY + 1):
					day_str = convert_number_to_str(day) 
					# check if the day exists
					path = url_root + '/archive/' + year_str + '/' + month_str + '/' + day_str
					if check_redirect(path):
						continue
					crawl_by_day(url_root + '/archive/', url_xpath, year_str, month_str, day_str)

def crawl_others():
	URL_LIST = [
		'https://www.r-bloggers.com/',
		'https://blog.acolyer.org/',
		'http://www.wildml.com/',
		'https://mattmazur.com/',
		'https://www.kdnuggets.com/',
	]

	URL_XPATH_MAP = {
		'https://www.r-bloggers.com/': '//a[@class=\'more-link\']',
		'https://blog.acolyer.org/': '//li/a',
		'http://www.wildml.com/': '//a[@class=\'more-link\']',
		'https://mattmazur.com/': '//h1[@class=\'entry-title\']/a',
		'https://www.kdnuggets.com/': '//li/a',
	}

	for url_root in URL_LIST:
		url_xpath = URL_XPATH_MAP[url_root]

		for year in range(START_YEAR, END_YEAR + 1):
			year_str = convert_number_to_str(year)
			path = url_root + year_str + '/'
			if check_redirect(path) and check_redirect(path.strip('/')):
				continue

			for month in range(START_MONTH, END_MONTH + 1):
				month_str = convert_number_to_str(month)
				path = url_root + year_str + '/' + month_str + '/'
				if check_redirect(path) and check_redirect(path.strip('/')):
					continue
				
				for day in range(START_DAY, END_DAY + 1):
					day_str = convert_number_to_str(day) 
					# check if the day exists
					path = url_root + year_str + '/' + month_str + '/' + day_str + '/'
					if check_redirect(path) and check_redirect(path.strip('/')):
						continue
					crawl_by_day(url_root, url_xpath, year_str, month_str, day_str)

# crawl all the blogs on a given day
def crawl_by_day(url_root, url_xpath, year, month, day):
	path = url_root + year + '/' + month + '/' + day
	print 'crawl: ' + path

	# extract all urls from each day
	urls = extract_whole_page_urls(path, url_xpath)
	date = year + month + day

	print len(urls)

	for url in urls:
		if '?source=' in url:
			url = url[:url.find('?source=')]
		data = extract_data_from_url(url)
		if 'title' not in data:
			continue
		data['url'] = url
		data['domain'] = url.split('/')[2]
		data['date'] = date

		# import to blogs, arxivs and blogs_arxivs
		import_to_database(data)

def extract_data_from_url(url):
	data = {}
	goose = Goose()
	try:
		article = goose.extract(url=url)
	except:
		return {}
	data['title'] = article.title
	data['text'] = article.cleaned_text
	data['keywords'] = extract_keywords(data['text'].encode('ascii', 'ignore').decode('ascii'))
	data['tags'] = []
	data['papers'] = []

	try:
		page_response = requests.get(url, timeout=5, headers=headers)
		soup = BeautifulSoup(page_response.content, 'html.parser')
	except Exception as e:
		print e
		return data

	# extract tags
	tag_links = soup.find_all('a', class_ = 'link u-baseColor--link')

	for link in tag_links:
		try:
			link = link['href']
		except Exception as e:
			continue
		if not 'tag' in link:
			continue
		try:
			tag = link.split('/')[4]
			tag = tag[:tag.find('?')]
			data['tags'].append(tag)
		except:
			continue

	# extract linked papers
	paper_links = soup.find_all('a')

	for link in paper_links:
		try:
			link = link['href']
		except:
			continue
		if link.startswith('/'):
			baseurl = url.split('/')[0] + url.split('/')[1] + url.split('/')[2] 
			link = baseurl + link

		# check if is arxiv paper link
		if 'arxiv.org' in link:
			data['papers'].append(link)

	return data


def import_to_database(data):
	blog_url = data['url']
	blog_id = hashlib.md5(blog_url.encode()).hexdigest()
	sql = "INSERT INTO blogs (id, url, date, domain, title, text, tags, keywords) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
	val = [blog_id, data['url'], data['date'], data['domain'], data['title'], data['text'], str(data['tags']), str(data['keywords'])]

	try:
		mycursor.execute(sql, tuple(val))
		mydb.commit()
		if mycursor.rowcount > 0:
			print str(mycursor.rowcount) + " blog inserted."
	except Exception as e:
		if not str(e).startswith('1062'):
			print e

	# import to arxivs and blogs_arxivs
	for paper in data['papers']:
		url = paper
		try:
			paper = paper[paper.find('arxiv.org') + 10:]
			if paper.startswith('ftp'):
				arxiv_id = paper.split('/')[4]							
			else:
				arxiv_id = paper.split('/')[1]
			if '.pdf' in arxiv_id:
				arxiv_id = arxiv_id[:arxiv_id.find('.pdf')]

			symbols = ['?', '%', '&', '#']
			for symbol in symbols:
				if symbol in arxiv_id:
					arxiv_id = arxiv_id[:arxiv_id.find(symbol)]
			
			if arxiv_id.endswith('.'):
				arxiv_id = arxiv_id[:len(arxiv_id) - 1]

			try:
				query = arxiv.query(id_list=[arxiv_id])[0]
			except Exception as e:
				print e
				arxiv_id = paper.split('/')[1] + '/' + paper.split('/')[2]
				if '.pdf' in arxiv_id:
					arxiv_id = arxiv_id[:arxiv_id.find('.pdf')]
				# print arxiv_id
				query = arxiv.query(id_list=[arxiv_id])[0]

			published = query.published
			date = published[:4] + published[5:7] + published[8:10]
			title = query.title
			summary = query.summary
			tags = str(query.tags)
			keywords = str(extract_keywords(summary))
	
			val = [arxiv_id, url, date, title, summary, tags, keywords]

			sql = "INSERT INTO arxivs (id, url, date, title, summary, tags, keywords) VALUES (%s, %s, %s, %s, %s, %s, %s)"
			try:
				mycursor.execute(sql, tuple(val))
				mydb.commit()
				print str(mycursor.rowcount) + " arxiv inserted."
			except Exception as e:
				if not str(e).startswith('1062'):
					print e

			match_id = '#'.join([blog_id, arxiv_id])
			val = [match_id, blog_id, arxiv_id]
			sql = "INSERT INTO blogs_arxivs (match_id, blog_id, arxiv_id) VALUES (%s, %s, %s)"
			mycursor.execute(sql, tuple(val))
			mydb.commit()
			print str(mycursor.rowcount) + " blogs_arxivs inserted."
		except Exception as e:
			if not str(e).startswith('1062'):
				print 'error1 '+ str(e)
				print url
			continue

# crawl all the blog links given a page link
def extract_whole_page_urls(url, xpath):
	while True:
		try:
			driver = webdriver.Chrome(chrome_options=chrome_options)
			break
		except Exception as e:
			print e
			print 'restart'
			pass

	try:
		driver.get(url)
	except:
		print 'fail to get page link'
		driver.quit()
		return []

	SCROLL_PAUSE_TIME = 4
	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	while True:
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		# Wait to load page
		time.sleep(SCROLL_PAUSE_TIME)
		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

	divs = driver.find_elements_by_xpath(xpath)

	urls = []
	for div in divs:
		try:
			url = div.get_attribute('href')
		except:
			continue
		if url == None or len(url) == 0:
			continue
		urls.append(url)

	driver.quit()
	return urls


def extract_keywords(text):
	r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
	r.extract_keywords_from_text(text)
	return r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.

# convert interger year/month/day to string
def convert_number_to_str(number):
	if number < 10:
		string = '0' + str(number)
	else:
		string = str(number)
	return string

# check if there is redirect
def check_redirect(url):
	r = requests.get(url)
	if r.status_code == 404:
		return True
	if len(r.history) == 0 or len(r.history) == 2:
		return False
	else:
		print 'redirect: ' + url
		return True
main()



