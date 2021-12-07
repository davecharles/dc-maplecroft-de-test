# maplecroft-de-test

Welcome to the Maplecroft data engineering technical test! This project
contains an api only pre-built Flask application.

Maplecroft is a global risk analytics company that aims to standardise risk across a variety of different issues across the globe.
To do this we are often tasked with assigning risk scores to customer provided sites. This inevitably leads to developing 
pipelines to handle the processing, storing and querying of this data. You have been given a typical ETL pipeline task to develop to solve.

## Getting started

To get started all you need is [Docker](https://docs.docker.com/). A makefile has been provided for you for simplicity

Start the dev server and initialise the database:

```bash
make init
```

You should now be able to access the development server at `http://localhost:5000/auth/login` albeit with an authentication error.

### Usage

The most convenient way to interact with the api is to use the Postman configuration provided. First import the following
two files into postman

```bash
de-test.postman_collection.json
de-test.postman_environment.json
```

Once imported send the login request to automatically populate the access_token variable. You should now 
be able to use the `Users` and `Sites` request to list data.

However, if you don't want to use postman or are not familiar with it then the instructions below demonstrate the general process.

The project uses Java Web Tokens to manage authentication, go ahead and obtain a token from the login page

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}' http://localhost:5000/auth/login
```

This will return something like:

```bash
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWRlbnRpdHkiOjEsImlhdCI6MTUxMDAwMDQ0MSwiZnJlc2giOmZhbHNlLCJqdGkiOiI2OTg0MjZiYi00ZjJjLTQ5MWItYjE5YS0zZTEzYjU3MzFhMTYiLCJuYmYiOjE1MTAwMDA0NDEsImV4cCI6MTUxMDAwMTM0MX0.P-USaEIs35CSVKyEow5UeXWzTQTrrPS_YjVsltqi7N4", 
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6MSwiaWF0IjoxNTEwMDAwNDQxLCJ0eXBlIjoicmVmcmVzaCIsImp0aSI6IjRmMjgxOTQxLTlmMWYtNGNiNi05YmI1LWI1ZjZhMjRjMmU0ZSIsIm5iZiI6MTUxMDAwMDQ0MSwiZXhwIjoxNTEyNTkyNDQxfQ.SJPsFPgWpZqZpHTc4L5lG_4aEKXVVpLLSW1LO7g4iU0"
}
```

You can use access_token to access protected endpoints:

```bash
curl -X GET -H "Content-Type: application/json" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzIiwiaWRlbnRpdHkiOjEsImlhdCI6MTUxMDAwMDQ0MSwiZnJlc2giOmZhbHNlLCJqdGkiOiI2OTg0MjZiYi00ZjJjLTQ5MWItYjE5YS0zZTEzYjU3MzFhMTYiLCJuYmYiOjE1MTAwMDA0NDEsImV4cCI6MTUxMDAwMTM0MX0.P-USaEIs35CSVKyEow5UeXWzTQTrrPS_YjVsltqi7N4" http://127.0.0.1:5000/api/v1/users
```


---

## Task

### Overview

Your task is to create a simple ETL pipeline that extracts site data from
the free bike sharing data service CityBikes and allows querying
of these sites by political administrative area (admin area).
The CityBikes service exposes bike sharing locations across the world. You
will need to extract the data from http://api.citybik.es/v2/networks and then
determine the political administrative area (admin area) using the
[GeoBoundaries](https://www.geoboundaries.org/api.html) dataset. Finally, load
the results into the provided SQLite database.

### Load

An entry point for the script to pull from citybikes api and load into SQLite
has been provided for you `api.manage.load_sites`. 
You will also need to create a database model in `api.api.models.site`.
When completed you can run the script with the following command:

```bash
docker-compose exec web flask api load_sites
```

You only have to assign up to admin level 3 (feel free to reduce if required). For example to get the admin level 3 data for Great Britain:

`https://www.geoboundaries.org/gbRequest.html?ISO=GBR&ADM=ADM3`

The admin area code that you have to assign is specified in the geoboundaries response as shapeID. Example:

```json
{ "shapeID": "GBR-ADM3-3_0_0-B1" }
```


### API

Once you have loaded data into the database you need to expose it through the api. An entry point and url has been
created for you. You just need to develop the logic in `api.api.resources.site.SiteList`.

The api should accept a query parameter `?admin_area` which returns all the
sites within this admin area, e.g:

`localhost:5000/api/v1/sites?admin_area=GBR-ADM3-3_0_0-B1`

## Notes

This project was built using the cookiecutter [flask-restful](https://github.com/karec/cookiecutter-flask-restful) project
