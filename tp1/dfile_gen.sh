#!/bin/bash
set -e

# Vars 
REPLICAS="${1:-1}"
FILE_NAME="${2:-"docker-compose.yaml"}"

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
    volumes:
      - ./data:/workspace/data
  joiner:
    container_name: joiner
    build:
      context: ./
      dockerfile: ./joiner/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
  dropper:
    deploy:
      replicas: 3
    build:
      context: ./
      dockerfile: ./dropper/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
  likes_filter:
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
  tag_unique:
    build:
      context: ./
      dockerfile: ./tag_unique/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
  trending_router:
    build:
      context: ./
      dockerfile: ./trending_router/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
      - TRENDING_INSTANCES=${REPLICAS}
  trending_top:
    build:
      context: ./
      dockerfile: ./trending_top/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
      - TRENDING_INSTANCES=${REPLICAS}"
  
  
for (( i = 0; i < $REPLICAS; i++ )) 
do
  
  TRENDING_INSTANCE="
  trending_instance${i}:
    build:
      context: ./
      dockerfile: ./trending_instance/Dockerfile
    entrypoint: python3 main.py
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      - RABBIT_SERVER_ADDRESS=rabbitmq
      - LOGGING_LEVEL=INFO
      - INSTANCE_NR=${i}"

  BASE+="${TRENDING_INSTANCE}"
done

echo "${BASE}" > ${FILE_NAME}
