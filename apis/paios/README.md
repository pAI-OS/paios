# Paios API

## Overview

The Paios API allows management interfaces to communicate with the backend services for functionality like enumerating, configuring, and activiating plugins ("abilities").

## Editing

The Paios API is specified in OpenAPI format and was created in Stoplight.

## Mocking

The API can be mocked locally using Stoplight's [Prism](https://github.com/stoplightio/prism), which can be installed as follows:

    npm install -g @stoplight/prism-cli

To start the local prism server using the current version of the API:

    prism proxy apis/paios/openapi.yaml

prism can also load the API directly from the repo:

    prism proxy 'https://raw.githubusercontent.com/Kwaai-AI-Lab/Paios/main/apis/paios/openapi.yaml'
