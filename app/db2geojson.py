import json
import pathlib
from typing import Any

from .models import point_name


class wbgt_point:
    def __init__(
        self,
        ido: float,
        keido: float,
        month: int,
        day: int,
        hour: int,
        sevirarity: int,
        type: str = "Feature",
    ) -> None:
        self.type: str = type
        self.geometry: dict[str, Any] = {"type": "Point", "coordinates": (keido, ido)}
        self.properties: dict[str, Any] = {"Month": month, "Day": day, "Hour": hour, "sevirarity": sevirarity}


class com_geojson:
    def __init__(self, type: str = "FeatureCollection"):
        self.type = type
        self.features: list[dict[str, Any]] = []


# jp = json.dumps(p.__dict__)
# print(jp)


def data2geojson(file_name: str = "info.geojson", force: bool = False):
    target = pathlib.Path(__file__).parent / "static" / file_name

    if force or not target.exists():
        g = com_geojson()

        for point in point_name.objects.all():
            print(point.id)
            try:
                for time, wbgt in zip(point.wbgt_time_json["time"], point.wbgt_time_json["wbgt"]):
                    month, day, hour = time.split("/")

                    if wbgt > 35:
                        sevirarity = 5
                    elif 35 > wbgt >= 31:
                        sevirarity = 4
                    elif 31 > wbgt >= 28:
                        sevirarity = 3
                    elif 28 > wbgt >= 24:
                        sevirarity = 2
                    else:  # WBGT < 24:
                        sevirarity = 1

                    g.features.append(
                        wbgt_point(
                            ido=point.ido,
                            keido=point.keido,
                            month=int(month),
                            day=int(day),
                            hour=int(hour.split(":")[0]),
                            sevirarity=sevirarity,
                        ).__dict__
                    )
            except TypeError:
                pass

        with open(target, mode="w+") as f:

            json.dump(g.__dict__, f)
