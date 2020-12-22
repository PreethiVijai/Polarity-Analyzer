#!/bin/sh
#
# Sample queries using Curl rather than rest-client.py
#

#
# Use localhost & port 5000 if not specified by environment variable REST
#
REST=${REST:-"34.120.115.161"}
curl -d '{"url":"https://storage.googleapis.com/cu-csci-5253/lfw/Zico/Zico_0003.jpg"}' -H "Content-Type: application/json" -X POST http://$REST/scan/url
#
# This should match the one above
curl http://$REST/match/215a00cf1bc966348bbd55aa0c8a8b82d1636a68e7d60fdf790329e2
#
# And this shouldn't
curl http://$REST/match/fb82e0120bbf3a26b38f6d939cb510f3ead0aa98b0afdfc972ea277e

#
# Throw in some random samples..
#
for url in $(shuf -n 20 ../all-image-urls.txt)
do
    curl -d "{\"url\":\"$url\"}" -H "Content-Type: application/json" -X POST http://$REST/scan/url
done