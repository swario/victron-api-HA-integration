# Victron API HA Integration

This repository contains resources and instructions for integrating Victron Cloud API sensors into Home Assistant. It includes various examples, configurations, and guides for fetching and utilizing data from the Victron API.

## Overview

I used the following API request to retrieve various data points from the Victron Energy platform using different `attributeId` values. These `attributeId` values correspond to specific data points related to the installation, such as battery status, power production, and other measurements.

To obtain the complete list of `attributeId` values, I reverse-engineered the API by making individual requests for each ID, which allowed me to compile a full list of sensors and their corresponding IDs.

## Example API Request

The following `curl` command retrieves data from the Victron API. You need to replace the placeholders with the actual values specific to your installation:

```bash
curl --request GET \
  --url 'https://vrmapi.victronenergy.com/v2/installations/{installation_id}/widgets/Graph?attributeIds%5B%5D={attribute_id}&instance={instance_id}' \
  --header 'Content-Type: application/json' \
  --header 'x-authorization: Token {your_token_here}'

