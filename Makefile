build:
	docker build -t wsdookadr/warctools:0.5.0 .
	docker build -t wsdookadr/warctools:latest .

push:
	docker image push --all-tags wsdookadr/femtocrawl

clean_docker:
	docker image prune -f
	docker container prune -f

preview_docs:
	asciidoc readme.adoc && chromium readme.html
