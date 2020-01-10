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


