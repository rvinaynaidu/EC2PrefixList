zip -r ../ec2-prefixlist.zip .


cd package

zip -g ec2-prefixlist.zip ec2_prefix_list.py 

 aws lambda create-function --function-name barath-ec2-list-lambda  --zip-file fileb://ec2-prefix-list-lambda.zip --handler ec2_prefix_list.handler --runtime python3.8 --role arn:aws:iam::932250589015:role/service-role/demo-lambda-role
