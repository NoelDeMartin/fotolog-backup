import sys
import urllib2
from bs4 import BeautifulSoup

################## UTILS ##################

MONTHS = {
	'enero' : '01',
	'febrero' : '02',
	'marzo' : '03',
	'abril' : '04',
	'mayo' : '05',
	'junio' : '06',
	'julio' : '07',
	'agosto' : '08',
	'septiembre' : '09',
	'octubre' : '10',
	'noviembre' : '11',
	'diciembre' : '12'
}

def get_url_data(url):
	FAKE_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
	return urllib2.urlopen(urllib2.Request(url, headers=FAKE_HEADERS)).read()


def get_post_date_from_description(text):
	start = text.rfind("el ") + 3
	end = text.rfind("<span class=\"flog_block_views float_right\">")
	stripped_text = text[start:end]
	date = stripped_text.split(' ')
	return date[2] + '-' + MONTHS[date[1]] + '-' + date[0]


def store_post(folder, soup):

	# Read Soup
	image_url = soup.find("a", class_="wall_img_container_big").img['src']
	post = soup.find("div", id="description_photo")
	post_title = post.h1
	post_description = post.p
	date = get_post_date_from_description(str(post_description))

	comments_raw = soup.find("div", id="list_all_comments").find_all("div", class_="flog_img_comments")

	comments = []
	for comment in comments_raw:
		comment = comment.p
		if comment is None:
			continue

		comment_user = comment.find("a").text.encode('utf-8')
		comment_text = comment.text.encode('utf-8')
		comments.append((comment_user, comment_text))

	# Write Data
	image_file = open(folder + date + '.jpg','wb')
	image_file.write(get_url_data(image_url))
	image_file.close()

	text_file = open(folder + date, 'wb')
	if post_title is not None:
		text_file.write("[" + post_title.text.encode('utf-8') + "]\n")
	else:
		text_file.write("[Untitled]\n")
	text_file.write(post_description.text.encode('utf-8'))
	text_file.write("\n\n")
	text_file.write("===================== COMMENTS =====================")
	text_file.write("\n\n")
	for comment in comments:
		text_file.write("[" + comment[0] + "] " + comment[1] + "\n\n")
	text_file.close()

################## MAIN ##################

if len(sys.argv) < 2:
	print 'Arguments are not valid, please execute the script using the following format: "python backup-fotolog.py [Fotolog Username] [Destination Path (Optional)]"'
	exit()
elif len(sys.argv) < 3:
	username = sys.argv[1]
	output_dir = './'
else:
	username = sys.argv[1]
	output_dir = sys.argv[2]

if output_dir[-1] != '/':
	output_dir = output_dir + '/'

url = 'http://www.fotolog.com/' + username
retries = 0

while url:
	try:
		print "Checking url", url, "..."
		soup = BeautifulSoup(get_url_data(url))
		store_post(output_dir, soup)
	except:
		retries = retries + 1
		print "Retry..."
		if retries < 5:
			continue
		else:
			print "Something went wrong", sys.exc_info()[0]
			break

	arrow = soup.find("a", class_="arrow_change_photo_right")
	if arrow is not None:
		url = arrow['href']
		retries = 0
	else:
		url = False
