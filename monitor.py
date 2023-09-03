from collections import deque

from direct.interval.IntervalGlobal import Sequence, Parallel
from direct.showbase.ShowBaseGlobal import globalClock


class WarningSequence(Sequence):

    def __init__(self, np):
        super().__init__(
            np.colorScaleInterval(0.5, (0.5, 0.5, 0.5, 1.0)),
            np.colorScaleInterval(0.5, (1.0, 1.0, 1.0, 1.0))
        )


class Monitor:

    def __init__(self, game_board, drops):
        self.game_board = game_board
        self.drops = drops
        self.is_gameover = False

    def update(self):
        if np := self.drops.fall():
            base.taskMgr.do_method_later(
                5, self.check, 'monitor', extraArgs=[np], appendTask=True)

        if score := self.drops.merge():
            self.game_board.score_display.add(score)

        self.drops.jump()
        self.game_board.merge_display.show(self.drops.complete_score, True)

        if self.is_gameover:
            para = Parallel()
            for np in self.drops.get_children():
                if self.game_board.is_in_gameover_zone(np):
                    para.append(WarningSequence(np))
            para.loop()
            return True

    def check(self, np, task):
        if self.game_board.is_in_gameover_zone(np):
            self.is_gameover = True

        return task.done