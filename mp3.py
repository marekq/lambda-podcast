import urllib2, boto3, time, eyed3
from lxml import etree

s3_region_name	= 'eu-west-1'		# region where both the music and publish bucket are located
s3_musicbucket 	= '<musicbucket>'	# bucket name containing all mp3 files

s3_webbucket 	= '<webbucket>' 	# bucket name where the podcast rss xml should be written to
s3_res_file 	= 'rss.xml'			# filename that should be used on the podcast publish bucket
tmp_rss_file 	= '/tmp/rss.xml'  	# temp file to be used by the lambda function

link_expiry 	= '43200'			# s3 signed url's should expiry after x seconds

podcast_name 	= 'my mixtapes and podcasts'
podcast_desc 	= 'my collection of mp3\'s'
podcast_url 	= 'https://marek.rocks'
podcast_img 	= '<url to a logo image>'
podcast_author 	= '@marekq'

###########

# create dictionaries 
fdict			= dict()
mdict			= dict()


# iterate over all files in S3 that are mp3, get filesize and modified date
def get_all_files():
	s 			= boto3.session.Session()
	c			= s.client('s3', region_name = s3_region_name) 
	l			= c.list_objects(Bucket = s3_musicbucket)

	for x in l['Contents']:
		if 'mp3' in x['Key']:
			
			# write the size and modified date of the MP3 to dictionaries
			fdict[x['Key']]	= x['Size']
			mdict[x['Key']] = x['LastModified']
			
			get_file(x['Key'], c)


# !disabled ID3 reading since i use the S3 bucket structure instead of tags! 
# read ID3 tags of the file by downloading the first 1kb from S3
def get_id3(fkey, c):
	eyed3.log.setLevel("ERROR")

	r 			= c.get_object(Bucket=s3__musicbucket, Key=fkey, Range='bytes=0-1024')	
	fn 			= fkey.split('/')[-1]
	d       	= r['LastModified']

	# write the first kb of the MP3 to disk
	f			= open('/tmp/'+fn, 'w')
	f.write(r['Body'].read())
	f.close()

	# check the MP3 file for ID3 tags (artist, title)
	a			= eyed3.load('/tmp/'+fn)
	return a.tag.artist, a.tag.title
	
	# !TODO - extend extraction of more ID3 tags 


# convert datetime input to proper formatted timestamp
def return_times(x):
	return x.strftime("%a, %d %b %Y %H:%M:%S %Z")


# generate a presigned URL and create XML entry for file
def get_file(fkey, c):
	z 			= c.generate_presigned_url('get_object', Params = {'Bucket': s3_musicbucket, 'Key': fkey}, ExpiresIn = link_expiry)
	
	#art, track	= get_id3(fkey, c) - currently unused, uncomment to enable ID3 reading
	art, track 	= fkey.split('/')

	#enc 		= "url='"+str(z)+"' length='"+str(fdict[fkey])+"' type='audio/mpeg'"
	item		= etree.SubElement(channel, 'item')
	desc 		= etree.SubElement(item, 'description')
	artist		= etree.SubElement(item, 'artist')
	title		= etree.SubElement(item, 'title')
	pubd		= etree.SubElement(item, 'pubDate')
	size 		= etree.SubElement(item, 'size')
	enc			= etree.SubElement(item, 'enclosure', url = str(z), length = str(fdict[fkey]), type = 'audio/mpeg')
	guid		= etree.SubElement(item, 'guid')
	link 		= etree.SubElement(item, 'link')

	desc.text	= fkey
	artist.text	= art
	title.text	= track
	pubd.text	= return_times(mdict[fkey])
	size.text	= str(fdict[fkey])
	guid.text	= str(z)
	link 		= str(z)


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

	title.text	= podcast_name
	author.text	= podcast_author
	desc.text	= podcast_desc
	link.text 	= podcast_url
	lang.text	= 'en-us'

	pubd.text 	= return_times(time)
	build.text	= return_times(time)

	image		= etree.SubElement(channel, 'image')
	imgurl		= etree.SubElement(image, 'url')
	imgtit		= etree.SubElement(image, 'title')
	imglin		= etree.SubElement(image, 'link')

	imgurl.text	= podcast_img
	imgtit.text = podcast_desc
	imglin.text	= podcast_url


# store the RSS file on S3
def put_s3(bucketn):
	s 			= boto3.resource('s3')
	c 			= s.Bucket(bucketn)
	c.put_object(Body = open(tmp_rss_file), Key = s3_res_file, ContentType = 'application/xml')


# prettify the xml and write to disk
def prettify_xml():
	x 			= etree.tostring(rss, xml_declaration=True, encoding='utf-8', pretty_print=True)
	f 			= open(tmp_rss_file, 'w')
	f.write(x)
	f.close()


# lambda handler
def handler(event, context):
 	make_root()
	get_all_files()
	prettify_xml()
	put_s3(s3_webbucket)