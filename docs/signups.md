---
id: signups
title: Signups
---

Read, create and manage all your donor signups

## Signup data structure

Signups have a quite complex structure due to the amount of data they usually carry.

Every Singup is composed by several nested objects which contains data for a specified component.
Main signup components are:

- Signup metadata
- Donor Data
  - Donor Contact Data
    - Donor Address Data
- Donation Data
- Payment Data

### Signup Metadata

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field            |  Type   | Required |                      Description                       |
| ---------------- | :-----: | :------: | :----------------------------------------------------: |
| id               | Integer |   True   |                       Signup ID                        |
| code             | String  |   True   |                   Signup Unique Code                   |
| uuid             | String  |   True   |                      Signup UUID                       |
| author           | Integer |   True   |     User Id of fundraiser who collected the signup     |
| creator          | Integer |   True   | User Id of fundraiser who added signup in the platform |
| tracking_code    | String  |   True   |                   UTM for the signup                   |
| company          | Integer |  False   |                Signup Metaface Company                 |
| campaign         | Integer |  False   |    ID of mobile campaign which generated the signup    |
| campaign_product | Integer |  False   |   ID of mobile campaign product choosen by the donor   |
| compiled_on      | Integer |  False   |         ID location where signup was collected         |
| created          |  Date   |  False   |                     Creation Date                      |
| updated          |  Date   |  False   |                    Last update Date                    |
| error_log        |  List   |  False   |            List of current errors in singup            |
| checkpoint_date  |  Date   |  False   |               Date of signup validation                |

### Donor data

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field            |  Type   | Required |                      Description                       |
| ---------------- | :-----: | :------: | :----------------------------------------------------: |
| id               | Integer |   True   |                       Signup ID                        |

### Donor Contacts data

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field            |  Type   | Required |                      Description                       |
| ---------------- | :-----: | :------: | :----------------------------------------------------: |
| id               | Integer |   True   |                       Signup ID                        |

### Donation Contacts data

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field            |  Type   | Required |                      Description                       |
| ---------------- | :-----: | :------: | :----------------------------------------------------: |
| id               | Integer |   True   |                       Signup ID                        |

### Payment Contacts data

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field            |  Type   | Required |                      Description                       |
| ---------------- | :-----: | :------: | :----------------------------------------------------: |
| id               | Integer |   True   |                       Signup ID                        |


## Read Signups

### GET /sheets

## Read Single Signup

### GET /sheets/:id

## Create Signup

### POST /sheets

## Edit Signup

### PUT /sheets/:id
