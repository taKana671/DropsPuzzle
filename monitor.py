from collections import deque

from direct.interval.IntervalGlobal import Sequence
from direct.showbase.ShowBaseGlobal import globalClock

from visual_effects import DisappearEffect, VFX, TextureAtlas, VFXSetting


class WarningSequence(Sequence):

    def __init__(self, np):
        super().__init__(
            np.colorScaleInterval(0.5, (0.5, 0.5, 0.5, 1.0)),
            np.colorScaleInterval(0.5, (1.0, 1.0, 1.0, 1.0))
        )


class Monitor:

    def __init__(self, game_board):
        self.game_board = game_board
        self.monitor_q = deque()
        self.tex = TextureAtlas('fire_ball.png')

    def monitoring(self):
        try:
            np = self.monitor_q.popleft()

            if self.game_board.is_in_gameover_zone(np):
                base.messenger.send('gameover')

                settings = VFXSetting(texture=self.tex, scale=4)
                VFX(settings, np).repeat_start(3)

        except IndexError:
            pass

    def start_monitoring(self, np, task):
        self.monitor_q.append(np)
        return task.done