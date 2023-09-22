from enum import Enum, auto

from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath


class Status(Enum):

    MONITORNING = auto()
    FINISH = auto()


class BlinkingSequence(Sequence):

    def __init__(self, np):
        super().__init__(
            np.colorScaleInterval(0.5, (0.5, 0.5, 0.5, 1.0)),
            np.colorScaleInterval(0.5, (1.0, 1.0, 1.0, 1.0))
        )


class WarningSequence(Sequence):

    def __init__(self, np_list, callback, *args, **kwargs):
        super().__init__()
        self.append_blinks(np_list)
        self.append(Func(callback, *args, **kwargs))

    def append_blinks(self, np_list):
        for _ in range(3):
            para = Parallel(*[BlinkingSequence(np) for np in np_list])
            self.append(para)


class Monitor:

    def __init__(self, game_board, drops):
        self.game_board = game_board
        self.drops = drops
        self.timer = 5

    def initialize(self):
        self.before = globalClock.get_frame_time()
        self.state = Status.MONITORNING

    def update(self):
        if self.state == Status.MONITORNING:
            if self.before is not None and globalClock.get_frame_time() - self.before >= self.timer:
                if overflow := [np for np in self.find_overflow()]:
                    base.taskMgr.do_method_later(
                        3, self.judge, 'judge', extraArgs=[overflow], appendTask=True)
                    self.before = None
                else:
                    self.before = globalClock.get_frame_time()

            self.drops.fall()

            if score := self.drops.merge():
                self.game_board.score_display.add(score)

            self.drops.jump()
            self.game_board.merge_display.show_score(self.drops.complete_score, True)

        if self.state == Status.FINISH:
            return False

        return True

    def restart_check(self):
        if not self.drops.disappear_vfx.is_playing():
            self.state = Status.MONITORNING
            return True

    def warn_gameover(self, callback, *args, **kwargs):
        seq = Sequence()
        overflows = [
            np for np in self.drops.get_children() if self.game_board.is_in_gameover_zone(np)
        ]
        seq = WarningSequence(overflows, callback, *args, **kwargs)
        seq.start()

    def judge(self, overflows, task):
        if not self.drops.disappear_vfx.is_playing():
            for np in overflows:
                if self.game_board.is_overflow(np):
                    self.state = Status.FINISH
                    break

        if self.state == Status.MONITORNING:
            self.before = globalClock.get_frame_time()

        return task.done

    def find_overflow(self):
        """Find objects not in the air and not int the gameboard cabinet."""
        neighbours = set()

        for nd in self.game_board.sense_contact():
            self.drops.find_all_neighbours(nd, neighbours)

        for nd in neighbours:
            np = NodePath(nd)
            if self.game_board.is_overflow(np):
                yield np