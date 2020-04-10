# http_server


## Examples

### Download file
Download a file:
```
curl 127.0.0.1:8000/test
curl 127.0.0.1:8000/?path=test
curl 127.0.0.1:8000/ -d 'action=download&path=test'
```

Download part of a file:
```
curl '127.0.0.1:8000/test?offset=10&size=20'
curl '127.0.0.1:8000/?offset=10&size=20&path=test'
curl 127.0.0.1:8000/ -d 'action=download&offset=10&size=20&path=test'
```

### Upload file

Upload a file named `test_up`:
```
curl 127.0.0.1:8000/test_up -X POST --data 'thedata' -H 'Content-type: application/octet-stream'
curl '127.0.0.1:8000/test_up?action=upload_file&data=thedata'
```

Upload a file appending:
```
curl 127.0.0.1:8000/test_app?append=t -X POST --data 'thedata' -H 'Content-type: application/octet-stream'
curl '127.0.0.1:8000/test_app?action=upload_file&data=thedata&append=t'
```

Upload base64 encoded:
```
curl 127.0.0.1:8000/test?encoding=64 -X POST --data 'dGhlZGF0YQo=' -H 'Content-type: application/octet-stream'

curl '127.0.0.1:8000/?action=upload_file&path=test&data=dGhlZGF0YQo&encoding=64'
```


## HTTPS

The server also support the HTTPS protocol, for which you should provide a certificate with a private key, by using the parameters `--cert` and `--key`. In case of genereting a cert which also includes the private key, only the `--cert` parameter must be used.

To generate an auto-self certificate you could use the following command:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
cat key.pem >> cert.pem # generate cert with the private key
```


## Directory listing

By default, directory listing is disabled, in case you want to enable it, you must provide the flag `--dir-list`.
