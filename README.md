# http_server


## Examples

### Download file
Download a file:
```
curl 127.0.0.1:8000/test
curl 127.0.0.1:8000/?path=test
curl 127.0.0.1:8000/ -X POST -d 'action=download_file&path=test'
```

Download part of a file:
```
curl '127.0.0.1:8000/test?offset=10&size=20'
curl '127.0.0.1:8000/?offset=10&size=20&path=test'
curl 127.0.0.1:8000/ -X POST -d 'action=download_file&offset=10&size=20&path=test'
```

### Upload file

Upload a file named `test_up`:
```
curl 127.0.0.1:8000/test_up -X POST --data 'thedata' -H 'Content-type: application/octet-stream'
curl '127.0.0.1:8000/test_up?action=upload_file&data=thedata'
```

Upload base64 encoded:
```
curl 127.0.0.1:8000/test?encoding=64 -X POST --data 'dGhlZGF0YQo=' -H 'Content-type: application/octet-stream'

curl 127.0.0.1:8000/?action=upload_file&path=test&data=dGhlZGF0YQo&encoding=64
```

Upload a file appending:
```
curl 127.0.0.1:8000/test?append=t -X POST --data 'thedata' -H 'Content-type: application/octet-stream'
curl 127.0.0.1:8000/test?action=upload_file&data=thedata&append=t
```
