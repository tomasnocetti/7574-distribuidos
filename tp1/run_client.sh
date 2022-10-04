#!/bin/bash
var=$(docker ps -qf "name=client")

docker exec -it $var python3 main.py
