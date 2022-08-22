build:
	docker build -t wsdookadr/femtocrawl:0.2 .
	docker build -t wsdookadr/femtocrawl:latest .

push:
	docker image push --all-tags wsdookadr/femtocrawl

clean_docker:
	docker image prune -f
	docker container prune -f

run:
	docker run -ti -v `pwd`/warc:/home/user/warc/:Z femtocrawl ./femtocrawl.sh

preview_docs:
	asciidoc readme.adoc && chromium readme.html
