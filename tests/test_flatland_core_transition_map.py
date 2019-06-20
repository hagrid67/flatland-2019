from flatland.core.grid.grid4 import Grid4Transitions, Grid4TransitionsEnum
from flatland.core.grid.grid8 import Grid8Transitions, Grid8TransitionsEnum
from flatland.core.transition_map import GridTransitionMap


def test_grid4_set_transitions():
    grid4_map = GridTransitionMap(2, 2, Grid4Transitions([]))
    assert grid4_map.get_transitions((0, 0, Grid4TransitionsEnum.NORTH)) == (0, 0, 0, 0)
    grid4_map.set_transition((0, 0, Grid4TransitionsEnum.NORTH), Grid4TransitionsEnum.NORTH, 1)
    assert grid4_map.get_transitions((0, 0, Grid4TransitionsEnum.NORTH)) == (1, 0, 0, 0)
    grid4_map.set_transition((0, 0, Grid4TransitionsEnum.NORTH), Grid4TransitionsEnum.NORTH, 0)
    assert grid4_map.get_transitions((0, 0, Grid4TransitionsEnum.NORTH)) == (0, 0, 0, 0)


def test_grid8_set_transitions():
    grid8_map = GridTransitionMap(2, 2, Grid8Transitions([]))
    assert grid8_map.get_transitions((0, 0, Grid8TransitionsEnum.NORTH)) == (0, 0, 0, 0, 0, 0, 0, 0)
    grid8_map.set_transition((0, 0, Grid8TransitionsEnum.NORTH), Grid8TransitionsEnum.NORTH, 1)
    assert grid8_map.get_transitions((0, 0, Grid8TransitionsEnum.NORTH)) == (1, 0, 0, 0, 0, 0, 0, 0)
    grid8_map.set_transition((0, 0, Grid8TransitionsEnum.NORTH), Grid8TransitionsEnum.NORTH, 0)
    assert grid8_map.get_transitions((0, 0, Grid8TransitionsEnum.NORTH)) == (0, 0, 0, 0, 0, 0, 0, 0)