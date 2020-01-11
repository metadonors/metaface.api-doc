---
id: trackings
title: Tracking Codes
---

Tracking code use to trace your signup campaigns

## Read tracking codes list

### GET /trackings

Read the list of available tracking codes

#### Response structure

| Field      |  Type   | Required |       Description        |
| ---------- | :-----: | :------: | :----------------------: |
| id         | Integer |   True   |       Tracking ID        |
| code       | String  |   True   |      Tracking Code       |
| is_active  | Boolean |  False   |     Tracking enabled     |
| is_default | Boolean |  False   | Is default Tracking Code |

Example request

```bash
curl --request GET \
  --url https://<cs>.metaface.it/api/v3/trackings \
  --header 'Authorization: Token <secret_api_key>'
```

Example response

```json
[
   {
    "id": 1,
    "code": "19XXXXXX1",
    "is_active": true,
    "is_default": false
  },
  {
    "id": 2,
    "code": "20XXXXX1",
    "is_active": true,
    "is_default": true
  }
]
```
