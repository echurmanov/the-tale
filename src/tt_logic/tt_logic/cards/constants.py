
from typing import List

NORMAL_RECEIVE_TIME: int = 12                      # период в часах через который обычному игроку даётся новая карта
RECEIVE_TIME: int = NORMAL_RECEIVE_TIME * 60 * 60  # период в секундах через который обычному игроку даётся новая карта

LEVEL_MULTIPLIERS: List[float] = [1,    # 3.5**0
                                  3.5,  # 3.5**1
                                  12,   # 3.5**2 = 12.25 -> 12; 12/3.5 ~ 3.43
                                  42,   # 3.5**3 = 42.875 -> 42; 42 / 12 = 3.5
                                  150]  # 3.5**4 = 150.0625 -> 150; 150/42 ~ 3.571

NORMAL_PLAYER_SPEED: float = 1.0   # скорость получения карт обычным игроком
PREMIUM_PLAYER_SPEED: float = 1.5  # скорость получения карт подписчиком
