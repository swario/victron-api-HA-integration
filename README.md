# Victron API HA Integration

This repository contains resources and instructions for integrating Victron Cloud API sensors into Home Assistant. It includes various examples, configurations, and guides for fetching and utilizing data from the Victron API.

## Overview

I used the following API request to retrieve various data points from the Victron Energy platform using different `attributeId` values. These `attributeId` values correspond to specific data points related to the installation, such as battery status, power production, and other measurements.

To obtain the complete list of `attributeId` values, I reverse-engineered the API by making individual requests for each ID, which allowed me to compile a full list of sensors and their corresponding IDs. "extracted_data.csv" contains this information here the link https://github.com/swario/victron-api-HA-integration/blob/main/extracted_data.csv

## Example API Request

The following `curl` command retrieves data from the Victron API. You need to replace the placeholders with the actual values specific to your installation:

```bash
curl --request GET \
  --url 'https://vrmapi.victronenergy.com/v2/installations/{installation_id}/widgets/Graph?attributeIds%5B%5D={attribute_id}&instance={instance_id}' \
  --header 'Content-Type: application/json' \
  --header 'x-authorization: Token {your_token_here}'
```

## Home Assistant integration
I’ve shared my anonymized configuration.yaml file. If you want to use it, you’ll need to:
1. Set your site ID and token.
2. Adjust the device number (in my case, it’s mostly set to 291) to match the one shown in the Victron VRM portal → Device List. There, each connected device has a specific instance number.

I used ChatGPT to help generate the configuration. It wasn’t without its challenges and time-consuming tweaks, but in the end it produced a working setup.
You might not be interested in monitoring all the metrics I included, and there’s no guarantee that everything will work out-of-the-box, so I suggest adding one part at a time and testing as you go.
The configuration creates sensors that you can then use in Home Assistant to display data via widgets.

WHERE IT STARDED
https://community.victronenergy.com/t/api-rest-values-mapping/9430

