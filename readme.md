lambda-podcast
==============


Create a serverless podcast service using Amazon S3 for storage of music files and Lambda for generation of the podcast feed. Since the podcast uses serverless components exclusively, you can run this service for very minimal cost and with very high durability.



Technical Description
---------------------


The Lambda function can run periodically to add/remove podcast files from the S3 bucket containing your music. The XML file read by your podcast client can optionally be written to a different S3 bucket with webhosting enabled. Metadata about analyzed MP3's (i.e. filesize, ID3 tags) are cached in a DynamoDB table to speed up podcast generation. 


The diagram below shows the technical components of lambda-podcast;


![alt tag](https://raw.githubusercontent.com/marekq/lambda-podcast/master/docs/1.png)


Besides generating public podcasts, the tool can be used to synchronize music onto an iPhone/iPad using a podcast app such as DownCast instead of needing iTunes. I personally use it as such to have all my music and mixtapes available for streaming and/or downloading across all my mobile devices and laptops. By eliminating the need for a webserver to host the podcast contents, you can run the podcast service for very low cost and with no periodic maintenance requirements (i.e. patching, running services, setting cronjobs etc.). 


A 128 MB Lambda function with a 60 second timeout should be sufficient up to a 1000 MP3's if you rely on the folder structure of your S3 bucket for naming. If you want to use ID3 tags from the MP3 files, the Lambda function will run significantly longer as it does need to download and analyze the first kilobyte of every MP3 file first, but I'll work on a better solution for this. 



Installation
------------


Installing lambda-podcast on your AWS account can be done as follows;


1. Create an S3 bucket which will contain your MP3 files and ensure the files contain a valid ID3 tag. If you do not want to rely on ID3, you can also group MP3 files per S3 folder (i.e. s3://musicbucket/<artist>/<track>.mp3).

2. Create an S3 bucket which will host the podcast XML file - you can also use the same music bucket from step 1 to do this. This bucket should be publically accessible whereas the music bucket does not need to be exposed as it uses S3 signed URL's. 

3. Create a DynamoDB table with a read/write capacity of one to store the MP3 metadata. This way the Lambda function doesnt need to analyze already known MP3's more, leading to a much quicker podcast generation. 

4. Configure the parameters in serverless.yml with details about your S3 buckets and details about the podcast. Your Lambda role must be able to read from the music bucket and write to the bucket where the XML will be posted. It will also need read/write access to DynamoDB. 

5. Use 'serverless deploy' to push the Python code to a Lambda function. Test the Lambda function manually to ensure the S3 buckets can be reached and that a valid XML is created in the destination bucket. Use CloudWatch logs of the Lambda function to debug any issues with permissions or wrong environment variables. 

6. Add a trigger to run the Lambda function whenever a file is uploaded/deleted in the music bucket. This means files will be  available in the podcast whenever a file is added a few seconds later. As an alternative, you can also auto regenerate the podcast every 24 hours or so. 


You can now add the XML's URL to your favourite podcast reader and stream music from your S3 bucket!



Contents of repository
----------------------


- The Lambda function code is in mp3.py, this file also contains the handler which is used to trigger the function whenever a change happens in the S3 music bucket. Set your Lambda handler to "mp3.handler" to trigger the function. 

- The LXML and eyeD3 folders contain Python libraries for generation of XML and identification of ID3 tags. These libraries were built on the Amazon Linux AMI and are precompiled for you to use in the Lambda function directly - simply include them in the ZIP uploaded to the Lambda function. 

- The serverless.yml file contains a template for deployment using the Serverless toolkit - this needs to be further expanded so that all components can be deployed using this template automatically (DynamoDB, create S3 buckets, etc.) as it only takes care of the Lambda function now. 



Pending feature requests
------------------------


- Implement inclusion of podcast links not hosted on personal S3 buckets (i.e. SoundCloud, third party podcasts). This would make the lambda-podcast a onestop shop for podcasts/mixtapes with the flexibility to stream or download music as you wish from one app. 

- Explore if native Python libraries available in Lambda can be used instead of bundling them with the code. This would eliminate any future compatability issues (i.e. switching to Python 3) and reduce the size of the codebase. 

- Make the podcast feed iTunes compatible so that it could be used for official iTunes podcasts - it is currently unknown if there are hard roadblocks to do so. Some requirements include specific iTunes XML tags and ensuring the SSL certificate is recognized by iTunes. 

- Explore if streaming music onto Sonos and Denon wireless music players is possible from S3 directly or through i.e. iHeart. This would allow wireless streaming onto these speaker sets without the need for a local NAS on your network.  

- Figure out if S3 signed URL's can be shortened to less characters, this would make the filesize of the generated XML significantly smaller and more scalable. 



Completed feature requests
--------------------------


- Create a CloudFormation template and ZIP which would preconfigure all components for you, eliminating the need for a manual setup. To do so, Lambda environment variables need to be included as parameters for the podcast instead of having to modify variables by hand in the Python source code.

- Cache the results from ID3 analysis into DynamoDB so files dont need to be analyzed every time the podcast is regenerated. This will drive down cost and makes the tool a lot more scalable.



Contact
-------


For any questions or fixes, please reach out to @marekq! 