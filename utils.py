import json
import os
import errno
import requests
import time
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

# crawl all the blog links given a page link
def extract_whole_page_urls(url, xpath):
	while True:
		try:
			driver = webdriver.Chrome(chrome_options=chrome_options)
			break
		except Exception as e:
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


# extract the contents of a list of webpages using Goose
def extract_texts(urls):
	output = []
	for url in urls:
		output.append(extract_single_text(url))
		print len(output)
	return output

# extract the content of a single webpage using Goose
def extract_single_text(url):
	output = {}
	goose = Goose()
	try:
		article = goose.extract(url=url)
	except:
		return output
	title = article.title
	text = article.cleaned_text
	output['url'] = url
	output['title'] = title
	output['text'] = text	
	return output

# parse each blog url and crawl all the paper links in the webpage content
def parse_blog(path):
	if is_file_exist(path + '/linked_papers.json'):
		return
	if not is_file_exist(path + '/urls.json'):
		return

	with open(path + '/urls.json') as f:
		urls = json.load(f)

	output = []
	dir_path = path + '/linked_papers.json'

	print path + ' has ' + str(len(urls)) + ' urls.'
	for url in urls:
		output.append(crawl_paper_links(url))
		
	write_to_json_file(dir_path, output)

# def crawl_blog_tags(url):
# 	while True:
# 		try:
# 			driver = webdriver.Chrome(chrome_options=chrome_options)
# 			break
# 		except Exception as e:
# 			print 'restart'
# 			pass

# 	try:
# 		driver.get(url)
# 	except:
# 		print 'continue'
# 		driver.quit()
# 		content = {}
# 		content['url'] = url
# 		content['tags'] = []
# 		return content

# 	try:
# 		soup = BeautifulSoup(driver.page_source, 'html.parser')
# 	except:
# 		return {}
# 		driver.quit()

# 	driver.quit()
# 	links = soup.find_all('a', class_ = 'link u-baseColor--link')
# 	tags = []

# 	for link in links:
# 		try:
# 			link = link['href']
# 		except:
# 			continue
# 		if not 'tag' in link:
# 			continue
# 		tag = link.split('/')[4]
# 		tag = tag[:tag.find('?')]
# 		tags.append(tag)

# 	content = {}
# 	content['url'] = url
# 	content['tags'] = tags

# 	# print content
# 	return content

def crawl_blog_tags(url):
	try:
		page_response = requests.get(url, timeout=5, headers=headers)
	except Exception as e:
		print e
		content = {}
		content['url'] = url
		content['tags'] = []
		return content

	try:
		soup = BeautifulSoup(page_response.content, 'html.parser')
	except:
		return {}

	links = soup.find_all('a', class_ = 'link u-baseColor--link')
	tags = []

	for link in links:
		try:
			link = link['href']
		except:
			continue
		if not 'tag' in link:
			continue
		try:
			tag = link.split('/')[4]
			tag = tag[:tag.find('?')]
			tags.append(tag)
		except:
			continue

	content = {}
	content['url'] = url
	content['tags'] = tags

	# print content
	return content

# crawl all the blog links given a page url
def crawl_paper_links(url): 
	try:
		page_response = requests.get(url, timeout=5, headers=headers)
	except Exception as e:
		print e
		content = {}
		content['url'] = url
		content['papers'] = []
		return content

	soup = BeautifulSoup(page_response.content, 'html.parser')
	links = soup.find_all('a')

	pdfs = []
	for link in links:
		try:
			link = link['href']
		except:
			continue
		if link.startswith('/'):
			baseurl = url.split('/')[0] + url.split('/')[1] + url.split('/')[2] 
			link = baseurl + link

		# check if is paper link
		if is_paper_link(link) == False:
			continue

		pdf = link
		# pdf = get_pdf(link)
		# time.sleep(3)

		if not pdf == 'NULL':
			pdfs.append(pdf)

	content = {}
	content['url'] = url
	content['papers'] = pdfs

	# print content
	return content

# def crawl_paper_links(url): 
# 	while True:
# 		try:
# 			driver = webdriver.Chrome(chrome_options=chrome_options)
# 			print 'success'
# 			break
# 		except Exception as e:
# 			print 'restart'
# 			pass
		
# 	# wait = WebDriverWait(driver, 3)
# 	# driver.set_page_load_timeout(180)

# 	try:
# 		driver.get(url)
# 		soup = BeautifulSoup(driver.page_source, 'html.parser')
# 		driver.quit()
# 	except:
# 		print 'continue'
# 		driver.quit()
# 		content = {}
# 		content['url'] = url
# 		content['papers'] = []
# 		return content

# 	links = soup.find_all('a')

# 	pdfs = []
# 	for link in links:
# 		try:
# 			link = link['href']
# 		except:
# 			continue
# 		if link.startswith('/'):
# 			baseurl = url.split('/')[0] + url.split('/')[1] + url.split('/')[2] 
# 			link = baseurl + link

# 		# check if is paper link
# 		if is_paper_link(link) == False:
# 			continue

# 		pdf = link
# 		# pdf = get_pdf(link)
# 		# time.sleep(3)

# 		if not pdf == 'NULL':
# 			pdfs.append(pdf)

# 	content = {}
# 	content['url'] = url
# 	content['papers'] = pdfs

# 	# print content
# 	return content

def extract_keywords(text):
	r = Rake() # Uses stopwords for english from NLTK, and all puntuation characters.
	r.extract_keywords_from_text(text)
	return r.get_ranked_phrases() # To get keyword phrases ranked highest to lowest.

# check if the url is linked to a paper
def is_paper_link(url):
	if url == None:
		return False
	if url.endswith('pdf') or 'arxiv.org' in url:
		return True
	# collect the filtered paper links
	# with open('filtered_paper_links.txt', 'a') as f:
	# 	f.write(url + '\n')
	return False

# check if file exist
def is_file_exist(filename):
	if os.path.exists(filename):
		# print 'exist: ' + filename
		return True
	else:
		# print 'not exist: ' + filename
		return False

# write to json file
def write_to_json_file(filename, content):
	if not os.path.exists(os.path.dirname(filename)):
		try:
			os.makedirs(os.path.dirname(filename))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise
	with open(filename, "w") as f:
		f.write(json.dumps(content, indent=4))
		print 'write to: ' + filename

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

# def check_redirect2(url):
# 	r = requests.get(url)

# check 404
def check_404(url):
	if requests.get(url).status_code == 404:
		print '404: ' + url
		return True
	else:
		return False