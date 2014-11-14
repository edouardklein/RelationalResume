all:
	python3 CV.py

upload:
	aws s3 cp --acl public-read index.html s3://rdklein.fr/CV/index.html

