# APIs

This document contains an explanation of how to use and consume the apis for this
application.  It uses OAuth 2.0, so keep that in mind whenever you make your requests.
Here is a good site for [OAuth examples](http://oauth.net/2/).  There are 2 APIs right now

[Service](#Service) -- Used to get information about all services or a specific service
[Incident](#Incident) -- Used to update or create an incident that effects a service
[Status](#Status)  -- Used to get the available statuses for an incident

NOTE: unless otherwise stated all fields shown in an example are required to make the API call.
Every response field will be returned.  If it does not actually have a value, it will be set to "None".

NOTE: All dates should be in UTC, including dates sent via POST, or PUT.  This is assumed to be the case.

## Service

A list of APIs that allow you to interact with the services you are monitoring with this application.
Do not get confused, service here refers to the service defined on the front end. For example, if I 
used whiskerboard to inform of downtimes for "People Finder" app, then I'd have a line on the main 
whiskerboard page that has "People Finder" as a line.  See [whiskerboard example](whiskerboard.ex.x25p.com)
if you do not understand.

Gets:

[List all services](#list-all-services)
[List specific service](#list-specific-service)
[List incidents for service](#list-all-active-incidents-for-a-service)

### List all services (GET)

Make a GET request to `website.com/api/v1/services` to get a list of services.

#### Example request -- list services

```sh
GET http://whiskerboard.ex.x25p.com/api/v1/services?access_token=YOUR_TOKEN
HTTP/1.1
```

#### Example response -- list services

services -- a list of dictionaries (service)
service -- a dictionary representing a service

```js
{
  "services": [
                {
                  "id": "ID_1",
                  "name": "First Service",
                  "url": "website.com/whiskerboard/first-service",
                  "status": "Down",
                  "current_incidents": ["INCIDENT_ID_1", "INCIDENT_ID_2"]
                 },
                 {
                  "id": "ID_2",
                  "name": "Second Service",
                  "url": "website.com/whiskerboard/second-service",
                  "status": "OK",
                  "current_incidents": "None"
                 }
               ]
}
```

### List specific service (GET)

Make a GET request to `website.com/api/v1/services/SERVICE_ID` to get a specific service.

#### Example request -- specific service

Optionally add past=true as a query parameter to get historical incidents.  Note: this is not
currently supported well.

```sh
GET http://whiskerboard.ex.x25p.com/api/v1/services/3834758?access_token=YOUR_TOKEN
HTTP/1.1
```

#### Example response -- specific service

post_incidents will only be supplied if the optional query paramter past=true has
been given.

```js
{
  "id": "ID_1",
  "name": "First Service",
  "description": "I am a test service for you viewing pleasure.",
  "category": "A category to help define what my function may accomplish",
  "create_date": "2010-08-18T04:24Z",
  "url": "website.com/whiskerboard/first-service",
  "status": "Warning",
  "current_incidents": ["INCIDENT_ID_1", "INCIDENT_ID_2"],
  "past_incidents": ["OLD_INCIDENT_ID_100", "OLD_INCIDENT_ID_47"]
}
```

## Incidents

This API allows you to create or update an incident.  You will always need either the INCIDENT_ID (for updates)
or the SERVICE_IDs (for creating).

Gets:

[All incidents](#list-all-incidents)
[Specific incident](#list-specific-incident)

Posts:

[Create an incident](#create-an-incident)

### List all incidents (GET)

Make a GET request to `website.com/api/v1/incidents`.

#### Example request -- all incidents

```sh
GET http://whiskerboard.ex.x25p.com/api/v1/incidents?access_token=YOUR_TOKEN
HTTP/1.1
```

#### Example response -- all incidents

```js
{
  "incidents": [
                {
                  "id": "ID_1",
                  "title": "Database Performance is Slow",
                  "effected_service_ids": ["Servie_ID_1", "Service_ID_7"],
                  "status": "Warning",
                  "start_date": "2012-09-18T04:24Z"
                 },
                 {
                  "id": "ID_2",
                  "title": "Our Apps ISZ borked",
                  "effected_service_ids": ["Servie_ID_10", "Service_ID_4"],
                  "status": "Down",
                  "start_date": "2012-10-14T07:21Z"
                 }
               ]
}
```

### List specific incident (GET)

Make a GET request to `website.com/api/v1/incidents/INCIDENT_ID` to get the incident.

#### Example request -- specific incident

```sh
GET http://whiskerboard.ex.x25p.com/api/v1/services/3834758/incidents/38f8asdf8?access_token=YOUR_TOKEN
HTTP/1.1
```

#### Example response -- specific incident

Note: often times created_date and start_date will be the same, however, it is possible an incident is
logged late and the created_date is after the start_date.

```js
{
  "id": "ID_1",
  "title": "Database Performance is Slow",
  "latest_message": {
                      "id": "message_id_2",
                      "status": "Warning",
                      "message": "Our system is experiencing issues with connecting to the database.",
                      "created_date": "2012-09-18T08:24Z"
                    }
  "message_ids": ['message_id_1', 'message_id_2'],
  "effected_service_ids": ["Servie_ID_1", "Service_ID_7"],
  "status": "Warning",
  "created_date": "2012-09-18T04:24Z",
  "start_date": "2012-09-18T04:24Z",
  "end_date": None,
 }
```

### List messages for incident (GET)

Make a GET request to `website.com/api/v1/incidents/INCIDENT_ID/messages` to get the incident.

#### Example request -- messages

```sh
GET http://whiskerboard.ex.x25p.com/api/v1/services/3834758/incidents/38f8asdf8/messages?access_token=YOUR_TOKEN
HTTP/1.1
```

#### Example response -- messages

```js
{
  "id": "ID_1",
  "title": "DB errors abound.",
  "effected_service_ids": ["Servie_ID_6"],
  "messages": [{
                  "id": "message_id_2",
                  "status": "Warning",
                  "message": "Our system is experiencing issues with connecting to the database.",
                  "created_date": "2012-09-18T08:24Z"
                },
                {
                  "id": "message_id_7",
                  "status": "Down",
                  "message": "We have lost all db connectivity.",
                  "created_date": "2012-09-18T09:24Z"
                },
                {
                  "id": "message_id_10",
                  "status": "OK",
                  "message": "DB back up and all is well.",
                  "created_date": "2012-09-18T010:24Z"
                }]
 }

### Create an incident (POST)

Make a POST request to `website.com/api/v1/incidents` .

Must include the following fields:

service_ids = ["id_1", "id_2"]
title = "Incident Title"
message = "A message about what is wrong right now"

























