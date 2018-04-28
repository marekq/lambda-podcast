#!/usr/bin/python
# marek kuczynski
# @marekq
# www.marek.rocks
# coding: utf-8

from xml.etree.ElementTree import Element, SubElement, Comment, tostring 
import urllib2, boto3, time, os

# create the XML document root
def make_root():
	rss 		= Element('rss', version = '2.0')
	rss.set('atom', 'http://www.w3.org/2005/Atom')
	rss.set('itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')

	channel 	= SubElement(rss, 'channel')
	SubElement(channel, 'title').text	= os.environ['podcast_name']
	SubElement(channel, 'author').text = os.environ['podcast_author']
	SubElement(channel, 'description').text = os.environ['podcast_desc']
	SubElement(channel, 'link').text = os.environ['podcast_url']
	SubElement(channel, 'language').text = 'en-us'
	SubElement(channel, 'lastBuildDate').text = time.strftime("%a, %d %b %Y %H:%M:%S %Z")
	SubElement(channel, 'pubDate').text = time.strftime("%a, %d %b %Y %H:%M:%S %Z")

	image		= SubElement(channel, 'image')
	SubElement(image, 'url').text = os.environ['podcast_img']
	SubElement(image, 'title').text = os.environ['podcast_desc']
	SubElement(image, 'link').text = os.environ['podcast_url']

	# create session to s3 music bucket
	s 	= boto3.session.Session()
	c	= s.client('s3', region_name = os.environ['s3_region_name']) 
	a	= c.list_objects(Bucket = os.environ['s3_musicbucket'])

	# check all mp3 files in the bucket
	for x in a['Contents']:
		if 'mp3' in x['Key']:
		
			# create presigned URL for the MP3
			z 			= c.generate_presigned_url('get_object', Params = {'Bucket': os.environ['s3_musicbucket'], 'Key': x['Key']}, ExpiresIn = os.environ['link_expiry'])
			art, track 	= x['Key'].split('/')
			
			item		=SubElement(channel, 'item')
			SubElement(item, 'description').text = str(art)+' - '+str(track)
			SubElement(item, 'artist').text = art
			SubElement(item, 'title').text = track
			SubElement(item, 'pubDate').text = x['LastModified'].strftime("%a, %d %b %Y %H:%M:%S %Z")
			SubElement(item, 'size').text = str(x['Size'])
			SubElement(item, 'enclosure', url = z, length = str(x['Size']), type = 'audio/mpeg')

	# write the output rss.xml file to /tmp
	f 	= open('/tmp/rss.xml', 'wb')
	f.write(tostring(rss))
	f.close()

	# upload the rss.xml file to 3
	s = boto3.resource('s3').Bucket(os.environ['s3_webbucket'])
	s.put_object(Body = open('/tmp/rss.xml'), Key = 'podcast.xml', ContentType = 'application/xml', ACL = 'public-read')

# lambda handler
def handler(event, context):
	make_root()
