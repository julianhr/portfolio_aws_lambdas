sam local invoke BeanstalkErrorNotifySlackFunction --event event.json

sam local start-api -p 3001

sam package  --output-template-file packaged.yaml --s3-bucket lambda-eb-error-notify-slack

sam deploy --template-file packaged.yaml --stack-name eb-error-notify-slack --capabilities CAPABILITY_IAM --region us-west-2
