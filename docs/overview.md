---
id: overview
title: Getting started
---

Use the Metaface API to manage your signups, your team and your locations with your database,
manage staff worked shifts and download your signups in batchs.

### Before you start

Here are a few things to know before you start.

* The REST architectural style is an integral part of API. To learn more about REST, check out RESTful Features of the Mailchimp API

## User roles

## Secure requests

We give a valid, signed certificate for all API methods. If you are manually coding submit URLs, change http to https in the URL, and make sure the connection library supports HTTPS.

## JSON

Metaface API only supports JSON. So instead of XML, HTTP POST parameters, or other serialization formats, most POST and PATCH requests require a valid JSON object for the body.

## Pagination


## Throttling

For security reasons, we use some connection limits when we see suspicious activity or overload. Each user account can have up to 10 simultaneous connections. You will receive an error message if you reach the limit. We do not throttle based on volume.

## Code examples

## Errors

