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


class FinishSequence(Sequence):

    def __init__(self, np_list):
        super().__init__()
        self.make_finish_seq(np_list)

    def make_finish_seq(self, np_list):
        for _ in range(3):
            para = Parallel(*[BlinkingSequence(np) for np in np_list])
            self.append(para)

        self.append(Func(base.messenger.send, 'gameover'))


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
                        3,
                        self.judge,
                        'judge',
                        extraArgs=[overflow],
                        appendTask=True
                    )
                    self.before = None
                else:
                    self.before = globalClock.get_frame_time()

            self.drops.fall()

            if score := self.drops.merge():
                self.game_board.score_display.add(score)

            self.drops.jump()
            self.game_board.merge_display.show_score(self.drops.complete_score, True)

    def finish_monitoring(self):
        seq = Sequence()
        overflows = [
            np for np in self.drops.get_children() if self.game_board.is_in_gameover_zone(np)
        ]
        seq = FinishSequence(overflows)
        seq.start()

    def judge(self, overflows, task):
        for np in overflows:
            if self.game_board.is_overflow(np):
                self.finish_monitoring()
                self.state = Status.FINISH
                break

        if self.state == Status.MONITORNING:
            self.before = globalClock.get_frame_time()

        return task.done

    def find_overflow(self):
        neighbours = set()

        for nd in self.game_board.sense_contact():
            self.drops.find_all_neighbours(nd, neighbours)

        for nd in neighbours:
            np = NodePath(nd)
            if self.game_board.is_overflow(np):
                yield np