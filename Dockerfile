FROM python:3.12-slim-bookworm
LABEL maintainer "Stefan Corneliu Petrea <stefan.petrea@gmail.com>"
RUN apt-get update
RUN apt-get -y install \
    --no-install-recommends \
    curl wget parallel zip unzip \
    python3-pip xmlstarlet jq libmagic-dev poppler-utils sqlite3 vim \
    libnss3-tools gcc g++ make python3-dev libxml2-dev libxslt1-dev patch
RUN apt-get -y clean
RUN rm -f /usr/bin/kiwix-tools.tar.gz && \
    wget -O /usr/bin/kiwix-tools.tar.gz https://download.kiwix.org/release/kiwix-tools/kiwix-tools_linux-x86_64-3.7.0-2.tar.gz && \
    cd /usr/bin/ && \
    tar xzvf kiwix-tools.tar.gz && \
    mv kiwix-tools_linux-x86_64-3.7.0-2/* . && \
    rm -rf /usr/bin/kiwix-tools*
RUN groupadd -g 1000 user
RUN useradd -rm -d /home/user -s /bin/bash -u 1000 -g 1000 user
USER user
WORKDIR /home/user
RUN echo export PATH="\"\$HOME/.local/bin/:\$PATH\"" >> ~/.bashrc
RUN pip3 install --break-system-packages virtualenv==20.26.3
RUN bash -c '~/.local/bin/virtualenv v_warcio && chmod +x ./v_warcio/bin/activate && source ./v_warcio/bin/activate && pip3 install warcio==1.7.4 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_warc2zim && chmod +x ./v_warc2zim/bin/activate && source ./v_warc2zim/bin/activate && pip3 install warc2zim==2.0.3 && pip3 cache purge && deactivate'
RUN bash -c '~/.local/bin/virtualenv v_warcindex && chmod +x ./v_warcindex/bin/activate && source ./v_warcindex/bin/activate && pip3 install warcio==1.7.4 && pip3 install lxml==4.9.3 && pip3 cache purge && deactivate'
# patch warcio (2020 code using pkg_resources module which is probably not even part of Python 3.12)
# reference: https://github.com/mu-editor/mu/issues/2485
RUN perl -p -i -e 's{^}{#} if $. == 16' /home/user/v_warcio/lib/python3.12/site-packages/warcio/cli.py
RUN perl -p -i -e 's{^}{#} if $. == 16' /home/user/v_warcindex/lib/python3.12/site-packages/warcio/cli.py
USER root
RUN apt-get -y purge gcc g++ make
RUN apt-get -y autoremove
USER user
RUN ls ; echo ""
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
RUN ls ;
COPY --chown=user bin/* /home/user/

ENTRYPOINT ["bash","-i","-c"]
