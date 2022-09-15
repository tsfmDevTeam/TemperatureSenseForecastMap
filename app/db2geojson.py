import json
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Any

from .models import point_name
from .wbgt_util import wbgt_status


class wbgt_point:
    def __init__(
        self,
        ido: float,
        keido: float,
        month: int,
        day: int,
        hour: int,
        severity: int,
        type: str = "Feature",
    ) -> None:
        self.type: str = type
        self.geometry: dict[str, Any] = {"type": "Point", "coordinates": (keido, ido)}
        self.properties: dict[str, Any] = {"Month": month, "Day": day, "Hour": hour, "severity": severity}


class com_geojson:
    def __init__(self, type: str = "FeatureCollection"):
        self.type = type
        self.features: list[dict[str, Any]] = []


# jp = json.dumps(p.__dict__)
# print(jp)


def data2geojson(file_name: str = "info.geojson", force: bool = False):
    target = pathlib.Path(__file__).parent / "static" / file_name

    date: int = datetime.now(timezone(timedelta(hours=9), "JST")).day

    if force or not target.exists():
        print("Generate GeoJson")

        g = com_geojson()

        for point in point_name.objects.all():
            try:
                for time, wbgt in zip(point.wbgt_time_json["time"], point.wbgt_time_json["wbgt"]):
                    month, day, hour = time.split("/")

                    for v in wbgt_status.values():
                        if v.min <= wbgt < v.max:
                            severity = v.level
                            break
                    else:
                        severity = 0

                    g.features.append(
                        wbgt_point(
                            ido=point.ido,
                            keido=point.keido,
                            month=int(month),
                            day=int(day),
                            hour=int(hour.split(":")[0]) + 24 * (date != int(day)),
                            severity=severity,
                        ).__dict__
                    )
            except TypeError:
                pass

        with open(target, mode="w+") as f:

            json.dump(g.__dict__, f)
