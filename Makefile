all: index.html

index.html: CV_header.html CV.list email.js
	python3 CV.py

upload: index.html
	aws s3 cp --acl public-read index.html s3://yourbucket/CV/index.html

