Cloud DPX
=========

A cloud-hosted DPX multi-instance app, built ontop of the Django REST Framework and Ember.js

## Running the app

Clone the repo into a working directory, and install Docker (and docker-compose).

To run the server, run `docker-compose up` from the repo directory.

To run the client, cd into the _client_ directory and run `ember serve`.

## Features

- Imports episodes from an existing RSS feed
- Generates a DotPodcast JSON feed

## Todo

- Add realtime feedback to the import UI
- Add real data into the dashboard
