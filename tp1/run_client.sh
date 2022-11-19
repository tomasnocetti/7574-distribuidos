#!/bin/bash
var=$(docker ps -qf "name=client_0")

docker exec -it $var python3 main.py
