---
id: signups
title: Signups
---

Read, create and manage all your donor signups

## Read Signups

### GET /sheets

Get list of signups

#### Filter Parameters

You can provide querystring parameters in your GET request to filter results

| Field               |  Type  | Required |            Description             |
| ------------------- | :----: | :------: | :--------------------------------: |
| id_in               |  List  |  False   | Comma separated list of Signup IDs |
| created_gte         |  Date  |  False   |         From creation date         |
| created_lte         |  Date  |  False   |          To creation date          |
| updated_gte         |  Date  |  False   |           From edit date           |
| updated_lte         |  Date  |  False   |            To edit date            |
| mandate_date_gte    |  Date  |  False   |         From mandate date          |
| mandate_date_lte    |  Date  |  False   |          To mandate date           |
| checkpoint_date_gte |  Date  |  False   |        From validation date        |
| checkpoint_date_lte |  Date  |  False   |         To validation date         |
| state               | String |  False   |      Label of searched state       |

#### Response structure

In response body you will find a list of signups, alon with pagination data

| Field    |  Type   | Required |           Description            |
| -------- | :-----: | :------: | :------------------------------: |
| count    | Integer |   True   |     Total number of signups      |
| next     | String  |  False   |   Url for next page of results   |
| previous | String  |  False   | Url for previous page of results |
| results  |  List   |   True   |      List of found signups       |

Example request

```bash
curl --request GET \
  --url 'http://<cs>.metaface.it/api/v3/sheets/?state=Completeted&validation_date_gte=2019-11-01' \
  --header 'Authorization: Token <secret_api_key>' \
```

## Read Single Signup

### GET /sheets/:id

Read a single signup

## Create Signup

### POST /sheets

Create a new signup

## Edit Signup

### PUT /sheets/:id

Edit an existing signup
