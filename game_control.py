from enum import Enum, auto

from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath


class Status(Enum):

    PROCESSING = auto()
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


class GameControl:

    def __init__(self, game_board, drops):
        self.game_board = game_board
        self.drops = drops
        self.timer = 7
        self.state = None

    def initialize(self):
        self.drops.initialize()
        self.game_board.initialize()

    def start(self):
        self.game_board.show_displays()
        self.before = globalClock.get_frame_time()
        self.state = Status.PROCESSING

    def process(self):
        match self.state:
            case Status.FINISH:
                self.warn_gameover()
                return False

            case Status.PROCESSING:
                self.drops.fall()
                self.drops.merge()
                self.drops.jump()

                if self.before is not None \
                        and globalClock.get_frame_time() - self.before >= self.timer:
                    if self.game_board.maybe_overflow():
                        base.task_mgr.do_method_later(2, self.confirm_overflow, 'confirm')
                        self.before = None
                    else:
                        self.before = globalClock.get_frame_time()
        return True

    def end_process(self):
        self.game_board.hide_displays()
        base.messenger.send('finish')

    def warn_gameover(self):
        self.state = None
        overflow = [np for np in self.drops.get_children() if self.game_board.is_outside(np)]
        WarningSequence(overflow, self.end_process).start()

    def judge(self):
        if len([np for np in self.find_overflow()]) >= 20:
            self.state = Status.FINISH
        else:
            self.state = Status.PROCESSING
            self.before = globalClock.get_frame_time()

    def confirm_overflow(self, task):
        if self.drops.is_merging:
            return task.again

        self.judge()
        return task.done

    def find_overflow(self):
        """Find objects not in the air and not int the gameboard cabinet."""
        neighbours = set()

        for nd in self.game_board.sense_contact():
            self.drops.find_all_neighbours(nd, neighbours)

        for nd in neighbours:
            np = NodePath(nd)
            if self.game_board.is_outside(np):
                yield np

    def pause_game(self):
        if self.state == Status.PROCESSING:
            self.before = None
            self.game_board.hide_displays()
            base.task_mgr.remove('confirm')
            return True