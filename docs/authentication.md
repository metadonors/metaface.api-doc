---
id: authentication
title: Authentication
---

To authenticate requests, Metaface API rely on a [Bearer Authentication](https://swagger.io/docs/specification/authentication/bearer-authentication/). 
It is possibile to obtain tokens form web interface as well from a dedicated api 
endpoint.

## Obtain tokens from API
#### POST /auth/token/

Using this endpoint you will able to obtain a valid token which can be used to 
authenticate all API requests.

##### Parameters

| Field         | Type          |   Required  | Description      |
| ------------- | :-----------: | :---------: | :---------------:|
| username      | String        | True        | A valid username |
| password      | String        | True        | User password    |


Example request body

```json
{
    "username": "john.doe",
    "password": "secretpassword",
}
```

##### Response structure

| Field         | Type          |   Required  | Description      |
| ------------- | :-----------: | :---------: | :---------------:|
| token         | String        | True        | A valid token |

Example response
```json
{
   "token": "<secret_api_key>"
}
```

## API Authentication

Once you obtain your token you are able to make requests to Metaface API. A valid
token should be passed in a dedicated Header in HTTP request with the following format

> Authorization: Token <secret_api_key>

As an example, this is a request that fetchs all user teams with [curl](http://curl.haxx.se/):

```bash
curl --request GET \
--url 'https://<cs>.metaface.it/v3/teams' \
-H 'Authorization: Token <secret_api_key>'
```

Where _cs_ is your customer subdomain