---
id: workedshifts
title: Worked Shifts
---

Worked Shift are used to track work time of fundraiser

## Read worked shift list

### GET /workedshift

Read the list of workedshift for a fundraiser

#### Fitler Parameters

You can provide querystring parameters in your GET request to filter results

| Field     |  Type   | Required |        Description        |
| --------- | :-----: | :------: | :-----------------------: |
| from_date |  Date   |  False   |  Workedshift start date   |
| to_date   |  Date   |  False   |    Workedshift to date    |
| staff     | Integer |  False   | Workedshift fundraiser ID |

#### Response structure

In response body you will find a list of worked shifts, with the following structure

| Field           |  Type   | Required |       Description        |
| --------------- | :-----: | :------: | :----------------------: |
| id              | Integer |   True   |      Workedshift ID      |
| uuid            | String  |   True   |     Workedshift UUID     |
| uuid            | String  |   True   |     Workedshift UUID     |
| company_label   | String  |   True   |   Workedshift Company    |
| team_label      | String  |   True   |     Workedshift Team     |
| location_label  | String  |   True   |   Workedshift Location   |
| timeround_label | String  |   True   |  Workedshift Timeround   |
| staff_label     | String  |   True   |    Workedshift Staff     |
| company         | Integer |   True   |  Workedshift Company ID  |
| team            | Integer |   True   |   Workedshift Team ID    |
| location        | Integer |   True   | Workedshift Location ID  |
| timeround       | Integer |   True   | Workedshift Timeround ID |
| date            |  Date   |   True   |     Workedshift Date     |
| note            | String  |  False   |     Workedshift Note     |

Example request

```bash
curl --request GET \
  --url 'https://<cs>.metaface.it/api/v3/workedshifts/?from_date=2019-12-01' \
  --header 'Authorization: Token <secret_api_key>' \
```

Example response

```json
[
  {
    "id": 1,
    "uuid": "975fc687-a3e4-42bc-9a15-37f2795b4f05",
    "company_label": "Team Inhouse",
    "team_label": "Tiger Team",
    "location_label": "Rome",
    "staff_label": "John Doe",
    "timeround_label": "1 hour",
    "company": 1,
    "team": 1,
    "location": 1,
    "staff": 1,
    "date": "2019-12-23",
    "timeround": 1,
    "note": ""
  },
  {
    "id": 2,
    "uuid": "975fc687-a3e4-42bc-9a15-37f2795b4123",
    "company_label": "Team Inhouse",
    "team_label": "Tiger Team",
    "location_label": "Rome",
    "staff_label": "John Doe",
    "timeround_label": "2 hours",
    "company": 1,
    "team": 1,
    "location": 1,
    "staff": 1,
    "date": "2019-12-25",
    "timeround": 1,
    "note": ""
  }
]

```

## Create worked shift

### POST /workedshift

Create a workedshift for a fundraiser

#### Body Request structure

| Field |  Type   | Required |  Description   |
| ----- | :-----: | :------: | :------------: |
| id    | Integer |   True   | Workedshift ID |

#### Response structure

| Field |  Type   | Required |  Description   |
| ----- | :-----: | :------: | :------------: |
| id    | Integer |   True   | Workedshift ID |

Example response

```json

```

## Edit worked shift list

### PUT /workedshift/:id

Edit a workedshift for a fundraiser

#### Response structure

| Field |  Type   | Required |  Description   |
| ----- | :-----: | :------: | :------------: |
| id    | Integer |   True   | Workedshift ID |

Example response

```json

```

## Delete worked shift list

### DELETE /workedshift/:id

Delete workedshift for a fundraiser

#### Response structure

| Field |  Type   | Required |  Description   |
| ----- | :-----: | :------: | :------------: |
| id    | Integer |   True   | Workedshift ID |

Example response

```json

```
