---
id: understanding_signups
title: Understanding Signups
---

Signups have a quite complex structure due to the amount of data they usually carry.

Every Singup is composed by several nested objects which contains data for a specified component.
Main signup components are:

- Signup metadata
- Donor Data
  - Donor Contact Data
    - Donor Address Data
- Donation Data
- Payment Data
- Reject Data

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
| signature        | String  |  False   |      Base64 representation of the donor signature      |
| donor            | Object  |   True   |            Donor data (see Donor structure)            |
| donation         | Object  |   True   |          Donor data (see Donation structure)           |
| payment          | Object  |   True   |           Donor data (see Payment structure)           |

### Donor data

Donor data contains information about the donor who made the signup. In this section you will find
personal and contacts data.

#### Structure

| Field         |  Type  | Required |              Description               |
| ------------- | :----: | :------: | :------------------------------------: |
| business_name | String |  False   |   Business name in case of companies   |
| first_name    | String |  False   |            Donor first name            |
| last_name     | String |  False   |            Donor last name             |
| sex           | String |  False   |              Donor gender              |
| pob           | String |  False   |          Donor place of birth          |
| dob           | String |  False   |          Donor date of birth           |
| job           | String |  False   |               Donor job                |
| ssn           | String |  False   |       Donor Social Serial Number       |
| vat           | String |  False   |               Donor VAT                |
| Contacts      | Object |  False   | Donor Contacts (see contact structure) |

### Donor Contacts data

Metadata represent information about where signup was collected, by who, in which team and in general
about all business related information that can be useful to manage and analyze signups.

#### Structure

| Field               |  Type  | Required |             Description             |
| ------------------- | :----: | :------: | :---------------------------------: |
| phone               | String |  False   |         Donor phone number          |
| mobile              | String |  False   |      Donor mobile phone number      |
| email               | String |  False   |         Donor email address         |
| privacy             | String |  False   |    Donor general privacy consent    |
| sms_privacy         | String |  False   |      Donor SMS privacy consent      |
| phone_privacy       | String |  False   | Donor Telemarketing privacy consent |
| mail_privacy        | String |  False   |     Donor Mail privacy consent      |
| paper_privacy       | String |  False   |    Donor Postal privacy consent     |
| profilation_privacy | String |  False   |  Donor Profilation privacy consent  |
| address             | Object |  False   |  Donor postal address information   |

### Donation data

Donation data represent information about the type and amount of the donation that donor signed up

#### Structure

| Field         |  Type   | Required |          Description          |
| ------------- | :-----: | :------: | :---------------------------: |
| frequency     | Integer |   True   |   Frequency of the donation   |
| amount        |  Float  |   True   |    Amount of the donation     |
| mandate_date  |  Date   |   True   |   Date of signup signature    |
| first_payment |  Date   |   True   |     Date of first payment     |
| destination   | Integer |   True   |  ID of donation destination   |
| topic         | Integer |   True   | ID of donor favorite argument |

### Payment Method data

Signup payment data

#### Structure

| Field       |  Type  | Required |                     Description                     |
| ----------- | :----: | :------: | :-------------------------------------------------: |
| method      | string |   True   |           Type of payment method choosed            |
| creditcard  | Object |  False   |  CreditCard Information (see CreditCard structure)  |
| directdebit | Object |  False   | DirectDebit Information (see DirectDebit structure) |
| bankwire    | Object |  False   |         SDD Information (see SDD structure)         |
