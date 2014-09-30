#!/bin/bash
set -eu

# from http://ajido.hatenablog.com/entry/2012/03/10/222710

TITLE=${1}
DESC=${2}
TAGS=${3}
PHOTO=${4}
USERNAME=${5}
USER_NSID=${6}
OAUTH_TOKEN=${7}
OAUTH_TOKEN_SECRET=${8}
OAUTH_CONSUMER_KEY=${9}
OAUTH_CONSUMER_SECRET=${10}

LANG=ja_JP.UTF-8
API_URL="https://api.flickr.com/services/upload"
METHOD="POST"
NONCE=`uuidgen | tr -d '-' | shasum | awk '{print $1}'`
TIMESTAMP=`date +%s`

function url_encode() {
    perl -MURI::Escape -lne 'print uri_escape($_, "^0-9A-Za-z\-._~")';
}

BASE="$METHOD&`echo $API_URL | url_encode`&"$(printf "description=%s&oauth_consumer_key=%s&oauth_nonce=%s&oauth_signature_method=HMAC-SHA1&oauth_timestamp=%s&oauth_token=%s&tags=%s&title=%s" "`echo "$DESC" | url_encode`" $OAUTH_CONSUMER_KEY $NONCE $TIMESTAMP $OAUTH_TOKEN "`echo "$TAGS" | url_encode`" "`echo "$TITLE" | url_encode`" | url_encode)

SIGNATURE=`echo -n "$BASE" | openssl sha1 -hmac "$OAUTH_CONSUMER_SECRET&$OAUTH_TOKEN_SECRET" -binary | openssl base64 | url_encode | sed 's/%20/+/g'`

HEADERS=`printf "Authorization: OAuth oauth_consumer_key=\"%s\", \"oauth_nonce=\"%s\", oauth_signature=\"%s\", oauth_signature_method=\"HMAC-SHA1\", oauth_timestamp=\"%s\", oauth_token=\"%s\"" $OAUTH_CONSUMER_KEY $NONCE $SIGNATURE $TIMESTAMP $OAUTH_TOKEN`

curl -s -S --request "$METHOD" "$API_URL" --header "$HEADERS" -F "photo=@$PHOTO" -F "title=$TITLE" -F "description=$DESC" -F "tags=$TAGS"
