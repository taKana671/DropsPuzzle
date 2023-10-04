from enum import Enum, auto

from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath


class Status(Enum):

    MONITORING = auto()
    PLAYING = auto()
    FINISH = auto()

    GAMEOVER = auto()
    PAUSE = auto()

    REBOOT = auto()
    # VFX_MONITORING = auto()


class BlinkingSequence(Sequence):

    def __init__(self, np):
        super().__init__(
            np.colorScaleInterval(0.5, (0.5, 0.5, 0.5, 1.0)),
            np.colorScaleInterval(0.5, (1.0, 1.0, 1.0, 1.0))
        )


class WarningSequence(Sequence):

    def __init__(self, np_list):
        super().__init__()
        self.append_blinks(np_list)
        self.append(Func(base.messenger.send, 'gameover'))

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
        self.before = globalClock.get_frame_time()
        self.state = Status.PLAYING
        self.drops.vfx.pause = False

    def process(self):
        self.drops.fall()
        self.drops.merge()
        self.drops.jump()

        match self.state:
            case Status.FINISH:
                self.warn_gameover()
                return False

            case Status.PLAYING:
                if self.before is not None \
                        and globalClock.get_frame_time() - self.before >= self.timer:
                    if self.game_board.maybe_find_overflow():
                        base.task_mgr.do_method_later(3, self.judge_gameover, 'judge')
                        self.before = None
                    else:
                        self.before = globalClock.get_frame_time()

            case Status.MONITORING:
                if not self.is_vfx_playing():
                    self.judge_continue()

        return True

    # def process(self):
    #     match self.state:
    #         case Status.FINISH:
    #             self.warn_gameover()
    #             return False

    #         case Status.MONITORING:
    #             if self.before is not None \
    #                     and globalClock.get_frame_time() - self.before >= self.timer:
    #                 if self.game_board.maybe_find_overflow():
    #                     base.taskMgr.do_method_later(3, self.judge_gameover, 'judge')
    #                     self.before = None
    #                 else:
    #                     self.before = globalClock.get_frame_time()

    #             self.drops.fall()
    #             if score := self.drops.merge():
    #                 self.game_board.score_display.add(score)

    #             self.drops.jump()
    #             self.game_board.merge_display.show_score(self.drops.complete_score, True)

    #         case Status.VFX_MONITORING:
    #             if not self.drops.disappear_vfx.is_playing():
    #                 self.judge_continue()

    #     # self.drops.fall()
    #     # if score := self.drops.merge():
    #     #     self.game_board.score_display.add(score)

    #     # self.drops.jump()
    #     # self.game_board.merge_display.show_score(self.drops.complete_score, True)
    #     return True

    def is_vfx_playing(self):
        # base.taskMgr.getTasksNamed('vfx_disappear')
        if self.drops.vfx.is_playing():
            return True

    def warn_gameover(self):
        overflow = [
            np for np in self.drops.get_children() if self.game_board.is_in_gameover_zone(np)]
        WarningSequence(overflow).start()
        self.state = Status.GAMEOVER

    def judge_continue(self):
        # if len([np for np in self.find_overflow()]) >= 20:
        if len([np for np in self.find_overflow()]) >= 3:
            self.state = Status.FINISH
        else:
            self.state = Status.PLAYING
            self.before = globalClock.get_frame_time()

    def judge_gameover(self, task):
        if self.drops.vfx.is_playing():
            self.state = Status.MONITORING
        else:
            self.judge_continue()

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

    def stop_gameover_judge(self):
        base.task_mgr.remove('judge')


    def pause_game(self):
        if self.state not in (Status.FINISH, Status.GAMEOVER):
            self.state = Status.PAUSE
            base.task_mgr.remove('judge')
            return True


    def resume_game(self):
        # self.drops.disappear_vfx.pause = False
        self.before = globalClock.get_frame_time()
        self.state = Status.PLAYING

    def reboot_game(self):
        for task in base.taskMgr.getTasksNamed('vfx'):
            args = task.getArgs()
            vfx_li, _ = args

            for vfx in vfx_li:
                vfx.force_stop = True
        self.state = None