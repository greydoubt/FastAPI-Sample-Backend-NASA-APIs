# Asteroid Tracker FastAPI Backend

This is a sample backend that fetches real-time data on near-Earth objects (NEOs) using NASA's API and processes the data to determine potential threats.

## Project Overview

The project's main objective is to provide information about NEOs, including immediate threats and top threats. It uses NASA's NEO Feed API to fetch data and processes it to identify threats. 

## Technology Stack

- Backend technology: FastAPI (Python)
- API: NASA NEO Feed

## API Details

The NASA NEO Feed API endpoint used in this project is as follows:

```
Endpoint: https://api.nasa.gov/neo/rest/v1/feed
```

- The start date is set to today.
- The end date is 7 days from now.

## Endpoints

### `/immediate_threat`

This endpoint returns information about the immediate threat NEO:

- Response Object:

```json
{
   "name": "2007 RF2",
   "diameter": { "measure": "192.5 - 430.5", "unit": "meters" },
   "closest_date": "2023-09-04",
   "speed": "116,835 Km/h",
   "threat_level": 0.91,
   "threat_color": "red"
}
```

The immediate threat NEO is determined as follows:
  - Filter only for objects with `is_potentially_hazardous_asteroid=True`.
  - Calculate the `diameter` as `(estimated_diameter.kilometers.estimated_diameter_max - estimated_diameter.kilometers.estimated_diameter_min) / 2`.
  - Normalize the diameter and the closest distance from Earth (`close_approach_data.miss_distance.kilometers`).
  - Calculate the `threat_level` as the average of the normalized diameter and closest distance.
  - The immediate threat NEO is the one with the highest threat level.
- The `threat_color` field is mapped as follows:
  - `threat_level > 0.9` => red
  - `threat_level > 0.8` => yellow
  - Otherwise, green

### `/top_threats`

This endpoint returns an array of 3 elements, representing the top 2nd, 3rd, and 4th threats from the computed list (since the top 1 threat is returned by the `/immediate_threat` endpoint). The response format is the same as the immediate threat object.

## Additional Notes

- The code is heavily commented to encourage you to modify and customize it according to your needs
- Feel free to explore and tinker with the project code to make adjustments or add additional features as desired