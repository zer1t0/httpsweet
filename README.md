# httpsweet

An HTTP server to easily download and upload files.

It was created with flexibility in mind, allowing be used in many different situations, therefore in allows deploy the very same operation in many different ways. For more information see the [Specification section](#specification).

**Note**: This software is not intended for production enviroment, but for test purposes, therefore be careful with its use, since it don't provide any security mechanism.

## Installation

From python packages:
```shell
pip3 install httpsweet
```

From repository:
```shell
git clone https://gitlab.com/Zer1t0/httpsweet
cd httpsweet/
python3 setup.py install # required only in case of system installation
```

## Examples
This section show some examples of the common operations.

### Download file
Download a file `test`:
```shell
curl 127.0.0.1:8000/test
curl 127.0.0.1:8000/?path=test
curl 127.0.0.1:8000/ -d 'action=download&path=test'
```

Download part of a file `test`:
```shell
curl '127.0.0.1:8000/test?offset=10&size=20'
curl '127.0.0.1:8000/?offset=10&size=20&path=test'
curl 127.0.0.1:8000/ -d 'action=download&offset=10&size=20&path=test'
```

### Upload file

Upload a file named `test_up`:
```shell
curl 127.0.0.1:8000/test_up -H "Content-Type: application/octet-stream" --data 'thedata' 
curl localhost:8000/test_up -H "Content-Type: application/octet-stream" --data-binary "@/etc/hosts"
curl '127.0.0.1:8000/test_up?action=upload_file&data=thedata'
```

Upload a file appending:
```shell
curl 127.0.0.1:8000/test_app?append=t -H "Content-type: application/octet-stream" --data "thedata"
curl '127.0.0.1:8000/test_app?action=upload_file&data=thedata&append=t'
```

Upload base64 encoded:
```shell
curl 127.0.0.1:8000/test_64?encoding=64 -H 'Content-type: application/octet-stream' --data 'dGhlZGF0YQo=' 
curl '127.0.0.1:8000/?action=upload_file&path=test_64&data=dGhlZGF0YQo&encoding=64'
```


## HTTPS

The server also support the HTTPS protocol, for which you should provide a certificate with a private key, by using the parameters `--cert` and `--key`. In case of genereting a cert which also includes the private key, only the `--cert` parameter must be used.

To generate an auto-self certificate you could use the following command:

```shell
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
cat key.pem >> cert.pem # generate cert with the private key
```


## Directory listing

By default, directory listing is disabled, in case you want to enable it, you must provide the flag `--dir-list`.


## Specification
The server perform 2 basic actions: **download** and **upload** file.

### Request Fields
In order to determine the action required in each request, the server examines the following parts of the request:

- **Method**
  + POST | PUT :: Indicate upload
  + Rest of methods :: Indicate download
- **Url**
  + Url path :: Indicates the path of the desired file 
  + Url parameters :: Indicates the action parameters
- **Body**, which could be:
  + Raw data :: Indicates the content of the file
  + Url encoded parameters :: Indicates the action parameters
  + Json data :: Indicates the action parameters
- **Headers** :: Indicates the action parameters
- **Cookies** :: Indicates the action parameters. Since `path` key has a special meaning in cookies, it is not possible to use that parameter in these fields.

The more relevant parts are those in last positions of the list. That means, for instance, if the Url path indicates the path `index.html`, but there is a parameter `path` (in the Url or in the Body) which indicates `other_file.txt`, then `other_file.txt` will be selected as the desired path.

### Key-Value fields (Url, Body, Headers, Cookies)
In all those fields which can specified the action parameters, the following values can be provided:
- **action**: str :: Determines the action
- **path**: str :: Indicates the path of the desired file
- **offset**: int :: (Download) Indicates the starting point for reading a file
- **size**: int :: (Download) Indicates the number of bytes read
- **append**: flag :: (Upload) Indicates if the data should be appended to the desired file
- **encoding**: str :: Indicates the desired encoder use in the actions, actually only base64 is supported (or not encoder)
- **data**: str :: (Upload) The data to write into the desired file

### Matching keywords

The key of the key value fields are case-insensitive, then, for instance, is the same `offset` that `Offset` or `OFFSET`.


In the parameter `action`, any value starting by `d` (such as `d`, `down`, `download`) will match as `download` action and any value starting by `u` (such as `u`, `up`, `upload`) will match as `upload` action.




