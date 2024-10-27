# pAI-OS API

## Overview

The pAI-OS API allows management interfaces to communicate with the backend services for functionality like enumerating, configuring, and activating plugins ("abilities").

## Editing

The pAI-OS API is specified in OpenAPI format and was created in Stoplight.

## Mocking

APIs can be mocked locally using tools like Stoplight's [Prism](https://github.com/stoplightio/prism), which can be installed as follows:

    npm install -g @stoplight/prism-cli

To start the local prism server:

    prism proxy apis/paios/openapi.yaml

prism can also load the API directly from the repo:

    prism proxy 'https://raw.githubusercontent.com/pAI-OS/Paios/main/apis/paios/openapi.yaml'
