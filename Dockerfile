FROM debian:11
RUN apt-get update
RUN apt-get -y install --no-install-recommends curl wget parallel zip unzip python3-pip firefox-esr xmlstarlet jq libmagic-dev poppler-utils sqlite3 vim
RUN apt-get -y clean
RUN rm -f /usr/bin/kiwix-tools.tar.gz && \
    wget -O /usr/bin/kiwix-tools.tar.gz https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-x86_64-3.3.0.tar.gz && \
    cd /usr/bin/ && \
    tar xzvf kiwix-tools.tar.gz && \
    mv kiwix-tools_linux-x86_64-3.3.0/* . && \
    rm -rf /usr/bin/kiwix-tools*
RUN groupadd -g 1000 user
RUN useradd -rm -d /home/user -s /bin/bash -u 1000 -g 1000 user
USER user
WORKDIR /home/user

RUN echo export PATH="\"\$HOME/.local/bin/:\$PATH\"" >> ~/.bashrc
RUN pip3 install virtualenv==20.16.3
COPY --chown=user data/ff.zip data/sample.warc bin/* /home/user/
RUN bash ./install_py.sh
COPY --chown=user data/certs/* /home/user/.mitmproxy/
RUN mkdir -p /home/user/.mozilla/firefox/p1 /home/user/.cache/mozilla/firefox/p1
RUN unzip ff.zip && rm -f ff.zip

ENTRYPOINT ["bash","-i","-c"]
