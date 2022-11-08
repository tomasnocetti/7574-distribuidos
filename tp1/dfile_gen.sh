#!/bin/bash
set -e

# Vars 
REPLICAS_JOINER="${1:-1}"
REPLICAS_DROPPER="${2:-1}"
REPLICAS_TRENDING="${3:-1}"
REPLICAS_THUMBNAIL="${4:-1}"
REPLICAS_LIKES_FILTER="${5:-1}"
REPLICAS_WATCHERS="${6:-1}"
FILE_NAME="docker-compose.yaml"

FILTER_QTY="5000000"

BASE="
version: '3'
services:
  rabbitmq:
    container_name: rabbitmq
    build: rabbitmq/.
    ports:
      - 5672:5672
      - 15672:15672
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:15672']
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: none
  client:
    container_name: client
    build:
      context: ./
      dockerfile: ./client/Dockerfile
    entrypoint: /bin/sh -c 'while sleep 1000; do :; done'
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
      - FILE_READER_LINES=20
      - THUMBNAIL_PATH=.temp
    volumes:
      - ./raw_data:/workspace/data
      - ./.temp:/workspace/.temp
  tag_unique:
    container_name: tag_unique
    build:
      context: ./
      dockerfile: ./tag_unique/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=tag_unique
      - LOGGING_LEVEL=INFO
  trending_router:
    container_name: trending_router
    build:
      context: ./
      dockerfile: ./trending_router/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=trending_router
      - LOGGING_LEVEL=INFO
      - TRENDING_INSTANCES=${REPLICAS_TRENDING}
  thumbnail_router:
    container_name: thumbnail_router
    build:
      context: ./
      dockerfile: ./thumbnail_router/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=thumbnail_router
      - LOGGING_LEVEL=INFO
      - INSTANCES=${REPLICAS_THUMBNAIL}
  trending_top:
    container_name: trending_top
    build:
      context: ./
      dockerfile: ./trending_top/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=trending_top
      - LOGGING_LEVEL=INFO
      - TRENDING_INSTANCES=${REPLICAS_TRENDING}
  downloader:
    container_name: downloader
    build:
      context: ./
      dockerfile: ./downloader/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=downloader
      - LOGGING_LEVEL=INFO
      - THUMBNAIL_INSTANCES=${REPLICAS_THUMBNAIL}"

for (( i = 0; i < $REPLICAS_JOINER; i++ )) 
do
  
  JOINER_INSTANCE="
  joiner_${i}:
    container_name: joiner_${i}
    build:
      context: ./
      dockerfile: ./joiner/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=joiner_${i}
      - LOGGING_LEVEL=INFO"

  BASE+="${JOINER_INSTANCE}"
done

for (( i = 0; i < $REPLICAS_DROPPER; i++ )) 
do
  
  DROPPER_INSTANCE="
  dropper_${i}:
    container_name: dropper_${i}
    build:
      context: ./
      dockerfile: ./dropper/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=dropper_${i}
      - LOGGING_LEVEL=INFO"

  BASE+="${DROPPER_INSTANCE}"
done

for (( i = 0; i < $REPLICAS_LIKES_FILTER; i++ )) 
do
  
  LIKE_FILTER_INSTANCE="
  like_filter_${i}:
    container_name: like_filter_${i}
    build:
      context: ./
      dockerfile: ./likes_filter/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
      - SERVICE_ID=like_filter_${i}
      - FILTER_QTY=${FILTER_QTY}"

  BASE+="${LIKE_FILTER_INSTANCE}"
done
      
for (( i = 0; i < $REPLICAS_TRENDING; i++ )) 
do
  
  TRENDING_INSTANCE="
  trending_${i}:
    container_name: trending_${i}
    build:
      context: ./
      dockerfile: ./trending_instance/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=trending_${i}
      - LOGGING_LEVEL=INFO
      - INSTANCE_NR=${i}"

  BASE+="${TRENDING_INSTANCE}"
done

for (( i = 0; i < $REPLICAS_THUMBNAIL; i++ )) 
do
  
  THUMBNAIL_INSTANCE="
  thumbnail_${i}:
    container_name: thumbnail_${i}
    build:
      context: ./
      dockerfile: ./thumbnail_instance/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=thumbnail_${i}
      - LOGGING_LEVEL=INFO
      - INSTANCE_NR=${i}"

  BASE+="${THUMBNAIL_INSTANCE}"
done

for (( i = 0; i < $REPLICAS_WATCHERS; i++ )) 
do
  
  WATCHER_INSTANCE="
  watcher_${i}:
    container_name: watcher_${i}
    build:
      context: ./
      dockerfile: ./watcher/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - SERVICE_ID=watcher_${i}
      - LOGGING_LEVEL=INFO
      - INSTANCE_ID=${i}
      - JOINER_INSTANCES=$REPLICAS_JOINER
      - DROPPER_INSTANCES=$REPLICAS_DROPPER
      - TRENDING_INSTANCES=$REPLICAS_TRENDING
      - LIKE_FILTER_INSTANCES=$REPLICAS_LIKES_FILTER
      - WATCHERS_INSTANCES=$REPLICAS_WATCHERS
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock"

  BASE+="${WATCHER_INSTANCE}"
done

echo "${BASE}" > ${FILE_NAME}
