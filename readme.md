lambda-podcast
==============


Create a serverless podcast service using Amazon S3 for storage of music files and Lambda for generation of the podcast feed. Since the podcast uses serverless components exclusively, you can run this service for very minimal cost and with very high durability. You can easily deploy the service to your account using the SAM CLI. 


Security
--------


The podcast uses a temporary signed S3 URL's to distribute the content to listeners, which prevents hotlinking by others to your bucket. Please be careful sharing the XML feed link openly on the Internet as it could incur high S3 bandwidth charges. 

By default, the XML file with the podcast feed is uploaded as a private object to S3 which cannot be accessed publicly. You can copy the object to a different location in case you want to protect access to the feed. Keep in mind though that the S3 signed URL's expire after a day by default, meaning that clients do need regular access to the feed. In the future, a more robust mechanism will be added to control feed access.



Technical Description
---------------------


The Lambda function can run periodically to add/remove podcast files from the S3 bucket containing your music. The XML file read by your podcast client is written to a different S3 bucket with webhosting enabled. 


The diagram below shows the technical components of lambda-podcast;


![alt tag](https://raw.githubusercontent.com/marekq/lambda-podcast/master/docs/1.png)


Besides generating public podcasts, the tool can be used to synchronize music onto an iPhone/iPad using a podcast app such as DownCast instead of needing iTunes. I personally use it as such to have all my music and mixtapes available for streaming and/or downloading across all my mobile devices and laptops. 

By eliminating the need for a webserver to host the podcast contents, you can run the podcast service for very low cost and with no periodic maintenance requirements (i.e. patching, running services, setting cronjobs etc.). A 256 MB Lambda function with a 10 second timeout should be sufficient up to a 1000 MP3's if you rely on the folder structure of your S3 bucket for naming.


Installation
------------


Installing lambda-podcast on your AWS account can be done easily through a launch script. Clone the repository and run the *deploy.sh* script. It will retrieve the Python packages, upload the Lambda function and deploy the CloudFormation template. You will be asked to set the S3 bucket with your audio files and a few fields that will be included in your XML feed. 

You can now add the XML's URL to your favourite podcast reader and stream music from your S3 bucket.


Contents of repository
----------------------


- The Lambda function code is stored in *mp3.py*, this file also contains the handler which is used to trigger the function whenever a change happens in the S3 music bucket. 
- The *template.yaml* file contains the SAM template for the application. You can deploy it using *sam deploy -g* or using the  *deploy.sh* script. 


Roadmap
-------


- [ ] Implement inclusion of podcast links not hosted on personal S3 buckets (i.e. SoundCloud, third party podcasts). This would make the lambda-podcast a onestop shop for podcasts/mixtapes with the flexibility to stream or download music as you wish from one app. 

- [ ] Make the podcast feed iTunes compatible so that it could be used for official iTunes podcasts - it is currently unknown if there are hard roadblocks to do so. Some requirements include specific iTunes XML tags and ensuring the SSL certificate is recognized by iTunes. 

- [ ] Explore if streaming music onto Sonos and Denon wireless music players is possible from S3 directly or through i.e. iHeart. This would allow wireless streaming onto these speaker sets without the need for a local NAS on your network.  

- [ ] Figure out if S3 signed URL's can be shortened to less characters, this would make the filesize of the generated XML significantly smaller and a bit more scalable. 

- [ ] Add an authentication or other security mechanism to restrict public access to the feed. Right now, you can only choose between having the feed fully public or only private to a logged in AWS user, there should be a third option in between for more controlled access.


Contact
-------


For any questions or fixes, please reach out to @marekq! 
