---
id: teams
title: Teams
---

Fundraisers team, where your fundraisers are working.


## Read teams list
### GET /teams

Read the list of available teams

#### Response structure

| Field   |  Type   | Required | Description  |
| ------- | :-----: | :------: | :----------: |
| id      | Integer |   True   |   Team ID    |
| name    | String  |   True   |  Team Name   |
| company | Object  |   True   | Team company |

#### Company object structure

| Field   |  Type   | Required | Description  |
| ------- | :-----: | :------: | :----------: |
| id      | Integer |   True   |   Company ID    |
| name    | String  |   True   |  Company Name   |

Example request:

```bash
curl --request GET \
  --url https://<cs>.metaface.it/api/v2/teams \
  --header 'Authorization: Token <secret_api_key>'
```

Example response:

```json
[
  {
    "id": 1,
    "name": "Tiger Team",
    "company": {
      "id": 2,
      "name": "My Awesome Organization"
    }
  },
  {
    "id": 2,
    "name": "Lions Team",
    "company": {
      "id": 2,
      "name": "My Awesome Organization"
    }
  }
]
```