FROM debian:11
RUN apt-get update
RUN apt-get -y install --no-install-recommends curl wget parallel zip unzip python3-pip firefox-esr xmlstarlet jq
RUN apt-get -y clean
RUN groupadd -g 1000 user
RUN useradd -rm -d /home/user -s /bin/bash -u 1000 -g 1000 user
USER user
WORKDIR /home/user
RUN pip3 install mitmproxy==8.1.1
RUN pip3 install har2warc==1.0.4
RUN pip3 install warcio==1.7.4
COPY --chown=user data/ff.zip bin/* /home/user/
COPY --chown=user data/certs/* /home/user/.mitmproxy/
RUN echo export PATH="\"\$HOME/.local/bin/:\$PATH\"" >> ~/.bashrc
RUN mkdir -p /home/user/.mozilla/firefox/p1 /home/user/.cache/mozilla/firefox/p1
RUN unzip ff.zip

ENTRYPOINT ["bash","-i","-c"]
