FROM ubuntu:21.10
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt update && apt dist-upgrade -y &&\
    apt-get --no-install-recommends install -y python3-pip libgl1 libglib2.0-0 python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools  libx11-dev && \
    apt autoremove && \
    apt autoclean && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app
COPY .git /app/.git
RUN pip3 install -r requirements.txt
COPY rewrite/ /app/rewrite


# CMD [ "python", "/app/rewrite/runGui.py" ]