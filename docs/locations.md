---
id: locations
title: Locations
---

Locations where your fundraiser can collect signups

## Read locations list

### GET /locations

Read the list of available locations

#### Response structure

| Field   |  Type   | Required |   Description    |
| ------- | :-----: | :------: | :--------------: |
| id      | Integer |   True   |   Location ID    |
| label   | String  |   True   |  Location Label  |
| code    | String  |   True   |  Location Code   |
| address | String  |  False   | Location Address |
| phone   | String  |  False   |  Location Phone  |
| email   | String  |  False   |  Location Email  |

Example response

```json
[
  {
    "id": 1,
    "label": "Test Position 1",
    "code": "10001",
    "address": "",
    "phone": "",
    "email": ""
  },
  {
    "id": 2,
    "label": "Test Position 2",
    "code": "10002",
    "address": "",
    "phone": "",
    "email": ""
  },
]

```
