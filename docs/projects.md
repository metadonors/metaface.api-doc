---
id: projects
title: Signup Projects
---

Use Signup Projects to organize your Signups

## GET /projects

Read the list of available projects

### Response structure

| Field         |  Type   | Required |                       Description                        |
| ------------- | :-----: | :------: | :------------------------------------------------------: |
| id            | Integer |   True   |                        Project ID                        |
| name          | String  |   True   |                       Project Name                       |
| slug          | String  |   True   |                  Project Unique String                   |
| day_deadline  | Integer |  False   | Day of month up until fundraisers can submit new signups |
| options       | Object  |   True   |   Custom Project Options (see dedicated section below)   |
| custom_fields |  List   |   True   |              List of custom defined fields               |
| enums         |  List   |   True   |            List predefined values for fields             |
| contact_state | Integer |  False   |          ID of dedicated state for appointments          |

#### Options field structure

| Field                          |  Type   | Required |                        Description                         |
| ------------------------------ | :-----: | :------: | :--------------------------------------------------------: |
| card_mimimum_expiration_months | Integer |  False   | Number of month to consider valid a credit card expiration |
| min_donor_age                  | Integer |  False   |                   Mimimum age for donors                   |
| max_donor_age                  | Integer |  False   |                   Maximum age for donors                   |
