# -*- coding: utf-8 -*-
import math
import random

# 武器属性表
WEAPON_TYPES = [
    # ...（从survivor.py复制完整的WEAPON_TYPES列表）...
]

KING_BIBLE_LEVELS = [
    # ...（从survivor.py复制完整的KING_BIBLE_LEVELS列表）...
]

WEAPON_COLORS = {
    # ...（从survivor.py复制完整的WEAPON_COLORS字典）...
}

# 下面迁移所有spawn_xxx武器生成函数，参数第一个为game（或self），其余参数不变
# 例如：
def spawn_straight_shot(game, player, weapon_name, level, angle=None):
    # ...（从survivor.py复制spawn_straight_shot函数体，self改为game）...
    pass

def spawn_homing_missile(game, player, weapon_name, level):
    # ...
    pass

# 其它spawn_xxx函数同理迁移 