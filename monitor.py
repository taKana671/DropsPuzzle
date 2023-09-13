from collections import deque

from direct.interval.IntervalGlobal import Sequence, Parallel, Func
from direct.showbase.ShowBaseGlobal import globalClock
from panda3d.core import NodePath


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
        self.timer = 5

    def initialize(self):
        self.before_frame_time = globalClock.get_frame_time()
        self.is_gameover = False

    def update(self):
        if self.is_gameover:
            return False

        if self.before_frame_time is not None \
                and globalClock.get_frame_time() - self.before_frame_time >= self.timer:
            print('check!')
            if overflow := [np for np in self.find_overflow()]:
                base.taskMgr.do_method_later(3, self.judge, 'judge', extraArgs=[overflow], appendTask=True)
                self.before_frame_time = None
            else:
                self.before_frame_time = globalClock.get_frame_time()

        if np := self.drops.fall():
            pass
            # print('before_check', np)
        #     base.taskMgr.do_method_later(
        #         5, self.check, 'monitor', extraArgs=[np], appendTask=True)

        if score := self.drops.merge():
            self.game_board.score_display.add(score)

        self.drops.jump()
        self.game_board.merge_display.show_score(self.drops.complete_score, True)

        return True

    def gameover(self):
        seq = Sequence()
        overflow_np = [np for np in self.drops.get_children() if self.game_board.is_in_gameover_zone(np)]

        for _ in range(3):
            para = Parallel()
            for np in overflow_np:
                para.append(WarningSequence(np))
            seq.append(para)

        seq.append(Func(base.messenger.send, 'gameover'))
        seq.start()

    def judge(self, overflow, task):
        for np in overflow:
            if self.game_board.is_overflow(np):
                self.gameover()
                self.is_gameover = True

        if not self.is_gameover:
            self.before_frame_time = globalClock.get_frame_time()

        return task.done

    def find_overflow(self):
        neighbours = set()

        # print([nd for nd in self.game_board.find_contact_obj()])
        for nd in self.game_board.sense_contact():
            self.drops.find_all_neighbours(nd, neighbours)

        for nd in neighbours:
            np = NodePath(nd)
            if self.game_board.is_overflow(np):
                yield np

    def check(self, np, task):
        if self.game_board.is_in_gameover_zone(np):
            self.is_gameover = True

        return task.done