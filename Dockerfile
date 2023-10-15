FROM debian:12-slim
LABEL maintainer "Stefan Corneliu Petrea <stefan.petrea@gmail.com>"
RUN apt-get update
RUN apt-get -y install \
    --no-install-recommends \
    firefox-esr chromium curl wget parallel zip unzip \
    python3-pip xmlstarlet jq libmagic-dev poppler-utils sqlite3 vim \
    libnss3-tools gcc g++ make python3-dev libxml2-dev libxslt1-dev patch
RUN apt-get -y clean
RUN rm -f /usr/bin/kiwix-tools.tar.gz && \
    wget -O /usr/bin/kiwix-tools.tar.gz https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-x86_64-3.5.0-2.tar.gz && \
    cd /usr/bin/ && \
    tar xzvf kiwix-tools.tar.gz && \
    mv kiwix-tools_linux-x86_64-3.5.0-2/* . && \
    rm -rf /usr/bin/kiwix-tools*
RUN groupadd -g 1000 user
RUN useradd -rm -d /home/user -s /bin/bash -u 1000 -g 1000 user
COPY bin/conf_root.sh conf_root.sh
RUN ./conf_root.sh
USER user
WORKDIR /home/user
RUN echo export PATH="\"\$HOME/.local/bin/:\$PATH\"" >> ~/.bashrc
RUN pip3 install --break-system-packages virtualenv==20.16.3
RUN bash -c '~/.local/bin/virtualenv v_mitmproxy && chmod +x ./v_mitmproxy/bin/activate && source ./v_mitmproxy/bin/activate && pip3 install mitmproxy==10.0.0 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_har2warc && chmod +x ./v_har2warc/bin/activate && source ./v_har2warc/bin/activate && pip3 install har2warc==1.0.4 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_warcio && chmod +x ./v_warcio/bin/activate && source ./v_warcio/bin/activate && pip3 install warcio==1.7.4 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_warc2zim && chmod +x ./v_warc2zim/bin/activate && source ./v_warc2zim/bin/activate && pip3 install warc2zim==1.5.4 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_warcindex && chmod +x ./v_warcindex/bin/activate && source ./v_warcindex/bin/activate && pip3 install warcio==1.7.4 lxml==4.9.3 && pip3 cache purge && deactivate'
USER root
RUN apt-get -y purge gcc g++ make
RUN apt-get -y autoremove
USER user
COPY --chown=user data/ff.zip data/sample.warc /home/user/
COPY --chown=user data/certs/* /home/user/.mitmproxy/
COPY --chown=user bin/conf_user.sh /home/user/
RUN ./conf_user.sh
RUN unzip ff.zip && rm -f ff.zip
RUN mkdir -p /home/user/.mozilla/firefox/p1 /home/user/.cache/mozilla/firefox/p1
RUN ls ; echo ""
COPY --chown=user bin/* /home/user/
COPY --chown=user warc2zim.patch.txt /home/user/
RUN patch v_warc2zim/lib/python3.11/site-packages/warc2zim/main.py < warc2zim.patch.txt

ENTRYPOINT ["bash","-i","-c"]
