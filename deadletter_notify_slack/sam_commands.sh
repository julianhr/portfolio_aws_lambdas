sam local invoke DeadletterNotifySlackFunction --event event.json

sam local start-api -p 3001

sam package  --output-template-file packaged.yaml --s3-bucket lambda-deadletter-notify-slack

sam deploy --template-file packaged.yaml --stack-name deadletter-notify-slack --capabilities CAPABILITY_IAM --region us-west-2
