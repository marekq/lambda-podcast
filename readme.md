lambda-podcast
==============


Create a serverless podcast service using Amazon S3 for storage of music files and Lambda for generating the podcast feed. The Lambda function can be ran periodically to add/remove podcast files from the S3 bucket containing your music. 

The tool can also be used to synchronize music onto an iPhone/iPad using a podcast app such as DownCast instead of doing so using iTunes - I use it as such to have all my music available for streaming and/or downloading across my devices. By eliminating the need for a webserver to host the podcast contents, you can run the podcast service for very low cost and with very low maintenance requirements. 



Description
-----------


The lambda-podcast can be used to generate a podcast feed out of a S3 bucket without the need of running an IaaS server. By using signed URL's to access content from S3, you can optionally grant temporary access to MP3 files on your S3 bucket to avoid hotlinking and therefor potentially high bandwidth costs. 

A 128 MB Lambda function with a 60 second timeout should be sufficient up to a 1000 MP3's if you rely on the folder structure of your S3 bucket for naming. If you want to use ID3 tags from the MP3 files, the Lambda function will run significantly longer as it does need to download and analyze the first kilobyte of every MP3 file first, but I'll work on a better solution for this. 


![alt tag](https://raw.githubusercontent.com/marekq/lambda-podcast/master/docs/1.png)



Installation
------------


Installing lambda-podcast on your AWS account can be done as follows;


1. Create an S3 bucket which will contain your MP3 files and ensure the files contain a valid ID3 tag. If you do not want to rely on ID3, you can also group MP3 files per S3 folder (i.e. s3://musicbucket/<artist>/<track>.mp3).

2. Create an S3 bucket which will host the podcast XML file - you can also use the same music bucket from step 1 to do this. This bucket should be publically accessible whereas the music bucket does not need to be exposed as it uses S3 signed URL's. 

3. Configure the parameters in mp3.py with the correct bucket information and upload the contents of the repository to a Lambda function. Your Lambda role must be able to read from the music bucket and write to the bucket where the XML will be posted. 

4. If you are a user of the serverless framework, you can use the included serverless.yml file to automatically upload your function to Lambda. You can also choose to ZIP the contents of the directory and upload it to Lambda manually. 

5. Test the Lambda function manually to ensure the S3 buckets can be reached and that a valid XML is created in the destination bucket. Use CloudWatch logs of the Lambda function to debug any issues. 

6. Add a trigger to run the Lambda function whenever a file is uploaded/deleted in the music bucket. This means files will be  available in the podcast whenever a file is added a few seconds later. 


You can now add the XML's URL to your favourite podcast reader and stream music from your S3 bucket!



Feature requests
----------------


* Cache the results from ID3 analysis into DynamoDB so files dont need to be analyzed every time the podcast is regenerated. This will drive down cost and makes the tool a lot more scalable.  

* Implement inclusion of podcast links not hosted on personal S3 buckets (i.e. SoundCloud, third party podcasts). This would make the lambda-podcast a onestop shop for podcasts/mixtapes with the flexibility to stream or download music as you wish. 

* Explore if native Python libraries available in Lambda can be used instead of bundling them with the code. This would eliminate any future compatability issues (i.e. switching to Python 3).

* Make the podcast feed iTunes compatible so that it could be used for official iTunes podcasts - it is currently unknown if there are hard roadblocks to do so. Some requirements include specific iTunes XML tags and ensuring the SSL certificate is recognized by iTunes. 

* Explore if streaming music onto Sonos and Denon music players is possible from S3 directly or through i.e. iHeart. This would allow wireless streaming onto these speaker sets without the need for a local NAS on your network.  

* Figure out if S3 signed URL's can be shortened to less characters, this would make the filesize of the generated XML significantly smaller.

* Create a CloudFormation template which would preconfigure all components for you, eliminating the need for a manual setup. 



Contact
-------


For any questions or fixes, please reach out to @marekq! 