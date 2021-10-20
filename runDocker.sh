#!/bin/bash
if [[ "$(docker images -q muonic 2> /dev/null)" == "" ]]; then
  docker build -t muonic .
fi

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
muonic python3 /app/rewrite/runGui.py
