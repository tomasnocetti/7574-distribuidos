#!/bin/bash
var=$(docker ps -qf "name=client")

docker exec -it $var bash
