build:
	docker build -t wsdookadr/femtocrawl:0.3 .
	docker build -t wsdookadr/femtocrawl:latest .

push:
	docker image push --all-tags wsdookadr/femtocrawl

clean_docker:
	docker image prune -f
	docker container prune -f

preview_docs:
	asciidoc readme.adoc && chromium readme.html
