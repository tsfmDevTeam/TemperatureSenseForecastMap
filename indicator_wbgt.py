import pandas as pd

def indicator(WBGT):
    num = ["運動は原則中止",
           "厳重警戒（激しい運動は中止）",
           "警戒（積極的に休憩",
           "注意（積極的に水分補給）",
           "ほぼ安全（適宜水分補給）"]

    if WBGT > 35:
        return num[0]
    elif 35 > WBGT >= 31:
        return num[1]
    elif 31 > WBGT >= 28:
        return num[2]
    elif 28 > WBGT >= 24:
        return num[3]
    elif WBGT < 24:
        return num[4]

