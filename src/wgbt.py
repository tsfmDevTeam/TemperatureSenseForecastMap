import json
from urllib import request


def location2wgbt(ido: float, keido: float) -> float:
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={ido}&longitude={keido}"
        "&hourly=temperature_2m,relativehumidity_2m,direct_radiation,diffuse_radiation,"
        "windspeed_10m&current_weather=true&timezone=Asia%2FTokyo"
    )

    with request.urlopen(url) as r:
        body = json.loads(r.read())

        tdate = body["current_weather"]["time"]
        index = body["hourly"]["time"].index(tdate)

        temperature = body["hourly"]["temperature_2m"][index]
        humidity = body["hourly"]["relativehumidity_2m"][index]
        direct_radiation = body["hourly"]["direct_radiation"][index]
        diffuse_radiation = body["hourly"]["diffuse_radiation"][index]
        windspeed_10m = body["hourly"]["windspeed_10m"][index]

    wgbt = (
        0.735 * temperature
        + 0.0374 * humidity
        + 0.00292 * temperature * humidity
        + 7.619 * (direct_radiation * diffuse_radiation)
        - 4.557 * (direct_radiation * diffuse_radiation) ** 2
        - 0.0572 * windspeed_10m
        - 4.064
    )

    return wgbt
