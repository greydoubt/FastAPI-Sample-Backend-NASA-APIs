"""


*** Hit RUN to see the immediate result of the REST endpoint `/` for this backend!***

(it will take a few seconds the first time you run it)

This is a Python backend is a proof-of-concept to show how to use FastAPI.
It serves as an API to fetch and process Near-Earth Object (NEO) data from NASA.

It provides three endpoints: `/immediate_threat`, `/top_threats`, and `/` to serve combined data.

It processes NASA data to determine what asteroids are important to watch out for.

Do do that, it normalizes the data and flags the top threats based on speed, diameter and distance from Earth of the object.

More info in the README file!

"""

import os
from datetime import date, timedelta

import requests
import uvicorn
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI()

# Get NASA API key from environment or use 'DEMO_KEY'
nasakey = os.environ.get('NASAKEY', 'DEMO_KEY')


def fetch_neo_data():
  """
  Fetches NEO data from NASA API for a 7-day window,
  the maximum allowed the API.
  """
  start_date = date.today().isoformat()
  end_date = (date.today() + timedelta(days=7)).isoformat()
  url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key={nasakey}"
  response = requests.get(url)

  # Return JSON if successful, None otherwise
  return response.json() if response.status_code == 200 else None


def process_neo_data(data):
  """Processes NEO data to find immediate and top threats."""
  neo_list = [
      item for sublist in data['near_earth_objects'].values()
      for item in sublist
  ]
  immediate_threat = None
  top_threats = []

  # work out the speed, distance and magnitude of the NEO
  # and add them to a list in order to normalize them
  diameters: list[float] = []
  distances: list[float] = []
  speeds: list[float] = []

  for neo in neo_list:
    diameter = (
        neo['estimated_diameter']['kilometers']['estimated_diameter_max'] -
        neo['estimated_diameter']['kilometers']['estimated_diameter_min']) / 2

    distance = float(
        neo['close_approach_data'][0]['miss_distance']['kilometers'])

    speed = float(neo['close_approach_data'][0]['relative_velocity']
                  ['kilometers_per_hour'])

    diameters.append(diameter)
    distances.append(distance)
    speeds.append(speed)

    neo['diameter'] = diameter
    neo['distance'] = distance
    neo['speed'] = speed

  for neo in neo_list:
    # normalize the params
    diameter_norm = (neo['diameter'] - min(diameters)) / (max(diameters) -
                                                          min(diameters))
    distance_norm = (neo['distance'] - min(distances)) / (max(distances) -
                                                          min(distances))
    speed_norm = (neo['speed'] - min(speeds)) / (max(speeds) - min(speeds))

    threat_level = (diameter_norm + distance_norm + speed_norm) / 3

    # ignore NEOs that are not too close to the Earth
    if not neo['is_potentially_hazardous_asteroid']:
      continue

    # Check for most immediate threat
    if immediate_threat is None or threat_level > immediate_threat[
        'threat_level']:
      immediate_threat = {
          'name':
          neo['name'],
          'diameter': {
              'measure': neo['diameter'],
              'unit': 'meters'
          },
          'closest_date':
          neo['close_approach_data'][0]['close_approach_date'],
          'speed':
          neo['speed'],
          'distance':
          neo['distance'],
          'threat_level':
          threat_level,
          'threat_color':
          'red' if threat_level > 0.9 else
          'yellow' if threat_level > 0.8 else 'green'
      }
    else:
      # Append to top threats if not the most immediate one
      top_threats.append(immediate_threat)

  return immediate_threat, top_threats


@app.get("/immediate_threat")
async def get_immediate_threat():
  """Endpoint to fetch and return the most immediate threat."""
  data = fetch_neo_data()
  return process_neo_data(data)[0] if data else {
      "message": "Failed to fetch NASA data"
  }


@app.get("/top_threats")
async def get_top_threats():
  """Endpoint to fetch and return the list of top threats."""
  data = fetch_neo_data()
  return process_neo_data(data)[1] if data else {
      "message": "Failed to fetch NASA data"
  }


@app.get("/")
async def get_merged_data():
  """Endpoint to fetch and return both immediate and top threats."""
  data = fetch_neo_data()
  immediate_threat, top_threats = process_neo_data(data)
  return {"immediate_threat": immediate_threat, "top_threats": top_threats}


# Run FastAPI application
if __name__ == "__main__":
  print(
      "If it's the first time running the server, it may take a few seconds before seeing the response in the webview… hang tight!\n"
  )
  uvicorn.run(app, host="0.0.0.0", port=8080)
