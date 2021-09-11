import json
import urllib


def get_center() -> str:
    # Opening JSON file
    f = open('./static/data.json', )

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Iterating through the json
    # list

    start_lat = float(data["routes"][0]["legs"][0]["start_location"]["lat"])
    start_lng = float(data["routes"][0]["legs"][0]["start_location"]["lng"])
    end_lat = float(data["routes"][0]["legs"][0]["end_location"]["lat"])
    end_lng = float(data["routes"][0]["legs"][0]["end_location"]["lng"])
    f.close()
    i = 0
    polyline = "1"
    center = str((start_lat + end_lat) / 2) + "," + str((start_lng + end_lng) / 2)
    for step in data["routes"][0]["legs"][0]["steps"]:
        polyline += str(step["polyline"]["points"]) + "|"
        polyline = polyline[: -1]
    return polyline
# Closing file
