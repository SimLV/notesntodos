#!/bin/sh

touch tmp
cp src/backend/web/vars.js tmp/web
cp build/release/* tmp/web/
nginx -c `pwd`/local_nginx.conf -p `pwd`
