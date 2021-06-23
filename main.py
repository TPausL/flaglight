import json
import math
import sys

import PIL
import requests
from matplotlib.colors import to_hex
from PIL import Image
from requests.api import head


def getColors(img):
    colorsRaw = img.getcolors(img.size[0]*img.size[1])
    colorsRaw = [c for c in colorsRaw if c[1]
                 [3] != 0]  # remove transparent pixels
    # sort by frequency
    colorsRaw = sorted(colorsRaw, key=lambda t: t[0], reverse=True)

    colors = [to_hex(list(map(lambda x: x / 255, c[1])))
              for c in colorsRaw]  # convert to hex

    colors = colors[: 4]
    return colors


def makeData(length, colors):
    data = list()
    color_length = math.floor(length / len(colors))
    for c in colors:
        data.append({"repeat": color_length, "leds": [c]})
    return data


def downloadImage(country_code, name):
    imageRes = requests.get("https://www.countryflags.io/" +
                            country_code + "/flat/64.png")

    if imageRes.status_code != 200:
        print("Wrong color code!")
        exit()

    with open(name, 'wb') as out_file:
        out_file.write(imageRes.content)  # write image to disk


lights = json.loads(requests.get(
    "http://devlight.local/tags/flag").text)["object"]  # get ligths with 'flags tag'

headers = {"Content-Type": "application/json", "Accept": "application/json"}

if len(sys.argv) == 2:
    downloadImage(sys.argv[1], "flag.png")
    img = Image.open("flag.png")
    colors = getColors(img)
    for l in lights:
        data = makeData(l["count"], colors)
        r = requests.patch("http://devlight.local/lights/" +
                           l["id"] + "/custom", data=json.dumps({"data": data}), headers=headers)
        if r.status_code == 200:
            print(r.json()["object"]["light"]["name"] +
                  ": " + "Succesfully applied flag!")
        else:
            print(l["name"] + ": " +  r.json()["message"])

elif len(sys.argv) == 3:
    downloadImage(sys.argv[1], "first.png")
    downloadImage(sys.argv[2], "second.png")
    first = Image.open("first.png")
    second = Image.open("second.png")
    colorsFirst = getColors(first)
    colorsSecond = getColors(second)
    for l in lights:
        dataFirst = makeData(l["count"] / 2 - 3, colorsFirst)
        dataSecond = makeData(l["count"] / 2 - 3, colorsSecond)

        r = requests.patch("http://devlight.local/lights/" +
                           l["id"] + "/custom", data=json.dumps({"data": dataFirst + [{"repeat": 6, "leds": ["#000"]}] + dataSecond}), headers=headers)
        if r.status_code == 200:
            print(r.json()["object"]["light"]["name"] +
                  ": " + "Succesfully applied flags!")
        else:
            print(l["name"] + ": " +  r.json()["message"])


else:
    print("Please provide one or two country codes!")
