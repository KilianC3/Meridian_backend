#!/usr/bin/env bash
set -e

until nc -z localhost 5432; do echo "waiting for postgres"; sleep 1; done
until nc -z localhost 27017; do echo "waiting for mongo"; sleep 1; done
until nc -z localhost 6379; do echo "waiting for redis"; sleep 1; done
