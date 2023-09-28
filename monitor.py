from enum import Enum, auto

from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath


class Status(Enum):

    MONITORNING = auto()
    FINISH = auto()
    GAMEOVER = auto()


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
        self.timer = 7
        self.state = None

    def initialize(self):
        self.before = globalClock.get_frame_time()
        self.state = Status.MONITORNING

    def update(self):
        match self.state:
            case Status.FINISH:
                self.warn_gameover()

            case Status.MONITORNING:
                if self.before is not None \
                        and globalClock.get_frame_time() - self.before >= self.timer:
                    if self.game_board.maybe_find_overflow():
                        base.taskMgr.do_method_later(3, self.judge, 'judge')
                        self.before = None
                    else:
                        self.before = globalClock.get_frame_time()

                self.drops.fall()

                if score := self.drops.merge():
                    self.game_board.score_display.add(score)

                self.drops.jump()
                self.game_board.merge_display.show_score(self.drops.complete_score, True)

    def restart_check(self):
        if not self.drops.disappear_vfx.is_playing():
            self.state = Status.MONITORNING
            return True

    def finish_monitoring(self):
        base.messenger.send('gameover')
        self.state = Status.GAMEOVER

    def warn_gameover(self):
        overflow = [
            np for np in self.drops.get_children() if self.game_board.is_in_gameover_zone(np)]
        WarningSequence(overflow, self.finish_monitoring).start()
        self.state = Status.MONITORNING

    def judge(self, task):
        if self.find_overflow():
            self.state = Status.FINISH

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
                return True