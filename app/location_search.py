from typing import Optional

import numpy as np
from django.db.models import Q
from django.db.models.query import QuerySet

from .models import location, point_name


def near_observatory(ido: float, keido: float) -> location:
    """近接地点の検索
    指定された地点に最も近い，DBに保存された地点情報を返します
    Args:
        - ido (float): 緯度
        - keido (float): 経度
    Returns:
        - target_point: 最寄り地点の DB オブジェクト
    """

    near_points: QuerySet = point_name.objects.filter(
        Q(ido__range=(ido - 0.155, ido + 0.155)),
        Q(keido__range=(keido - 0.277, keido + 0.277)),
    )

    target_distance: int = 100
    target_point: Optional[location] = None

    for near_point in near_points:
        distance = np.sqrt((near_point.ido - ido) ** 2 + (near_point.keido - keido) ** 2)
        if distance <= target_distance:
            target_point = near_point
            target_distance = distance
    return target_point
