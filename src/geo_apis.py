import json
from typing import Any, Union
from urllib import request

from django.shortcuts import render


def find_near(ido: float, keido: float) -> Union[list[Any], Any]:
    url = f"http://geoapi.heartrails.com/api/json?method=searchByGeoLocation&x={keido}&y={ido}"

    tikaku: list[dict[str, str]] = []
    with request.urlopen(url=url) as r:
        body = json.loads(r.read())
        # print(body["response"]["location"])
        try:
            for item in body["response"]["location"]:
                tikaku.append(
                    {
                        "yuubin": "〒" + item["postal"],
                        "juusyo": item["prefecture"] + item["city"] + item["town"],
                        "lat": "緯度" + item["x"],
                        "lng": "経度" + item["y"],
                    }
                )
            return tikaku
        except KeyError:
            return render(request, "app/basyodetail_error.html")  # type:ignore


if __name__ == "__main__":
    find_near(ido=34.498, keido=135.456)
