#!/bin/bash
if [[ "$(docker images -q muonic 2> /dev/null)" == "" ]]; then
  docker build -t muonic .
fi

OS="`uname`"
case $OS in
  'Linux')
    OS='Linux'
    docker run --rm -it \
   --user=$(id -u) \
   --env="DISPLAY" \
   --workdir=/app \
   --volume="$PWD":/app \
   --volume="/etc/group:/etc/group:ro" \
   --volume="/etc/passwd:/etc/passwd:ro" \
   --volume="/etc/shadow:/etc/shadow:ro" \
   --volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
   --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
   -v /dev:/dev \
   -v /var:/var \
   --privileged \
   -it \
muonic python3 /app/rewrite/runGui.py
    ;;
  'FreeBSD')
    OS='FreeBSD'
    alias ls='ls -G'
    ;;
  'WindowsNT')
    OS='Windows'
    echo "Windows not supported"
    ;;
  'Darwin')
    OS='Mac'
    export IP=`ipconfig getifaddr en1`
    export DISPLAY=$IP:0
    export PATH=/usr/X11/bin/xhost:$PATH
    xhost + $IP
    docker run --rm -it \
   --user=$(id -u) \
   --env="DISPLAY" \
   -e DISPLAY=$DISPLAY \
   -v /dev:/dev \
   --workdir=/app \
   --volume="$PWD":/app \
   --volume="/etc/group:/etc/group:ro" \
   --volume="/etc/passwd:/etc/passwd:ro" \
   --volume="/etc/shadow:/etc/shadow:ro" \
   --volume="/etc/sudoers.d:/etc/sudoers.d:ro" \
   --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
   -v /dev:/dev \
   -v /var:/var \
   --privileged \
   -it \
muonic python3 /app/rewrite/runGui.py
    ;;
  'SunOS')
    OS='Solaris'
    ;;
  'AIX') ;;
  *) ;;
esac



#docker run   --privileged -it muonic python3 /app/rewrite/runGui.py
