import urllib2, boto3, time, eyed3, os
from lxml import etree

###########

# create dictionaries 
fdict			= dict() 	# store file size of s3 keys
mdict			= dict()	# store modified date of s3 keys
hdict 			= dict() 	# store hashes of s3 keys


# iterate over all files in S3 that are mp3, get filesize and modified date
def get_all_files():
	# create session to s3 music bucket
	s 			= boto3.session.Session()
	c			= s.client('s3', region_name = os.environ['s3_region_name']) 
	a			= c.list_objects(Bucket = os.environ['s3_musicbucket'])

	# create session to s3 webbucket
	e 			= s3_session(os.environ['s3_webbucket'])

	# create session to dynamodb	
	d			= boto3.resource('dynamodb', region_name = os.environ['s3_region_name']).Table(os.environ['dynamo_table'])

	# touch an empty file for S3 file redirection - perhaps there is an easier way? 
	f 	= open('/tmp/s3.txt', 'w')
	f.write('')
	f.close()

	for x in a['Contents']:
		if 'mp3' in x['Key']:
			
			# write the size and modified date of the MP3 to dictionaries
			fdict[x['Key']]	= x['Size']
			mdict[x['Key']] = x['LastModified']
			hdict[x['Key']] = x['ETag'].strip('"')

			get_file(x['Key'], c, d, e)


# check dynamo if a particular ETag was analyzed already
def check_dynamo(mp3hash, fkey, d):
	t 			= d.get_item(TableName = os.environ['dynamo_table'], Key = {'mp3hash': mp3hash})

	if t.has_key('Item'):
		print 'HIT!', t['Item']['artist'], t['Item']['title']
		return t['Item']['artist'], t['Item']['title']
  
	else:
		a, t 	= get_id3(fkey)
		print 'MISS!', a, t
		return a, t


# write the ID3 attributes to DynamoDB so it doesnt need to be recalculated every lambda run 
def write_dynamo(mp3hash, title, artist):
	b 			= boto3.resource('dynamodb', region_name = os.environ['s3_region_name']).Table(os.environ['dynamo_table'])

	b.put_item(Item = {
		'mp3hash' : mp3hash,
		'title' : artist,
		'artist' : title
	})


# !disabled ID3 reading since i use the S3 bucket structure instead of tags! 
# read ID3 tags of the file by downloading the first 1kb from S3
def get_id3(fkey):
	eyed3.log.setLevel("ERROR")

	s 			= boto3.session.Session()
	c			= s.client('s3', region_name = os.environ['s3_region_name']) 
	r 			= c.get_object(Bucket = os.environ['s3_musicbucket'], Key = fkey, Range = 'bytes=0-1024')	
	fn 			= fkey.split('/')[-1]
	mp3hash 	= hdict[fkey]

	print 'added '+fkey+' to dynamodb'

	# write the first kb of the mp3 file to disk
	f			= open('/tmp/'+fn, 'w')
	f.write(r['Body'].read())
	f.close()

	# check the MP3 file for ID3 tags (artist, title)
	a			= eyed3.load('/tmp/'+fn)
	
	try:
		art 	= a.tag.artist
		track 	= a.tag.title
	
	except:
		art, track 	= fkey.split('/')

	write_dynamo(mp3hash, art, track)
	return art, track


# convert datetime input to proper formatted timestamp
def return_times(x):
	return x.strftime("%a, %d %b %Y %H:%M:%S %Z")


# generate a presigned URL and create XML entry for file
def get_file(fkey, c, d, e):

	# get the ETag for the file
	mp3hash		= hdict[fkey]

	# create presigned URL for the MP3
	z 			= c.generate_presigned_url('get_object', Params = {'Bucket': os.environ['s3_musicbucket'], 'Key': fkey}, ExpiresIn = os.environ['link_expiry'])
	
	# create a website redirect object in your public S3 bucket to shorten the presigned URL character length and prettify the MP3 URL
	bkey 		= os.environ['podcast_folder']+'/'+mp3hash[:10]+'.mp3'
	put_s3(e, os.environ['s3_webbucket'], '/tmp/s3.txt', bkey, z, 'audio/mpeg')
	
	# DISABLED - use s3 path and trackname for podcast track properties instead of dynamo 
	#art, track 	= fkey.split('/')
	
	# ask dynamo if the mp3 hash was analyzed already for id3 tags
	art, track 	= check_dynamo(mp3hash, fkey, d)

	item		= etree.SubElement(channel, 'item')
	desc 		= etree.SubElement(item, 'description')
	artist		= etree.SubElement(item, 'artist')
	title		= etree.SubElement(item, 'title')
	pubd		= etree.SubElement(item, 'pubDate')
	size 		= etree.SubElement(item, 'size')
	enc			= etree.SubElement(item, 'enclosure', url = os.environ['podcast_url']+'/'+bkey, length = str(fdict[fkey]), type = 'audio/mpeg')

	desc.text	= fkey
	artist.text	= art
	title.text	= track
	pubd.text	= return_times(mdict[fkey])
	size.text	= str(fdict[fkey])


# create the XML document root
def make_root():
	global rss, channel 
	nam			= {'atom' : 'http://www.w3.org/2005/Atom', 'itunes' : 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
	rss 		= etree.Element('rss', nsmap = nam, version = '2.0')

	channel		= etree.SubElement(rss, 'channel')
	title 		= etree.SubElement(channel, 'title')
	author		= etree.SubElement(channel, 'author')
	desc 		= etree.SubElement(channel, 'description')
	link		= etree.SubElement(channel, 'link')
	lang		= etree.SubElement(channel, 'language')
	build		= etree.SubElement(channel, 'lastBuildDate')
	pubd 		= etree.SubElement(channel, 'pubDate')

	title.text	= os.environ['podcast_name']
	author.text	= os.environ['podcast_author']
	desc.text	= os.environ['podcast_desc']
	link.text 	= os.environ['podcast_url']
	lang.text	= 'en-us'

	pubd.text 	= return_times(time)
	build.text	= return_times(time)

	image		= etree.SubElement(channel, 'image')
	imgurl		= etree.SubElement(image, 'url')
	imgtit		= etree.SubElement(image, 'title')
	imglin		= etree.SubElement(image, 'link')

	imgurl.text	= os.environ['podcast_img']
	imgtit.text = os.environ['podcast_desc']
	imglin.text	= os.environ['podcast_url']


def s3_session(bucketn):
	s 			= boto3.resource('s3')
	return s.Bucket(os.environ['s3_webbucket'])


# store a file on a S3 bucket
def put_s3(session, bucketn, fbody, fkey, redir, contentt):
	if len(redir) != 0:
		session.put_object(Body = open(fbody), Key = fkey, ContentType = contentt, WebsiteRedirectLocation = redir)
	else:
		session.put_object(Body = open(fbody), Key = fkey, ContentType = contentt)

	
# prettify the xml and write to disk
def prettify_xml():
	x 			= etree.tostring(rss, xml_declaration = True, encoding = 'utf-8', pretty_print = True)
	f 			= open('/tmp/rss.xml', 'w')
	f.write(x)
	f.close()


# lambda handler
def handler(event, context):
	# create the root XML structure
	make_root()
	
	# iterate all files in the music S3 bucket, add URL's and ID3 metadata to XML
	get_all_files()
	
	# prettify the XML so its easier to read
	prettify_xml()
	
	# get s3 session
	s 			= s3_session(os.environ['s3_musicbucket'])

	# write the XML file to the public S3 bucket
	put_s3(s, os.environ['s3_webbucket'], '/tmp/rss.xml', os.environ['s3_res_file'], '', 'application/xml')