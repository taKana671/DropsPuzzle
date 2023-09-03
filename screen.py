from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from panda3d.core import CardMaker, LColor

import direct.gui.DirectGuiGlobals as DGG


class Screen:

    def __init__(self, parent):
        # super().__init__(
        #     # frameSize=(-0.5, 0.5, -0.5, 0.5),
        #     parnet=base.aspect2d,
        #     # # text_fg=(1, 0, 0, 1),
        #     # # pos=(0, 0)
        # )

        cm = CardMaker("card")
        cm.set_frame_fullscreen_quad()
        card = base.render2d.attach_new_node(cm.generate())

        card.set_transparency(1)
        card.set_color(LColor(0, 0, 0, 0.8))
        # label = DirectLabel(frameSize=(-0.8, 0.8, -1.0, 1.0), frameColor=(0, 0, 0, 0.8), pos=(0, 0, 0))
        # label = DirectLabel(frameSize=(-1.5, 1.5, -1.333, 1.333), frameColor=(0, 0, 0, 0.8), pos=(0, 0, 0))
        
        self.create_gui()

        # label.reparent_to(self)
        
        # label1 = DirectLabel(frameSize=(-0.5, 0.5, -1.0, 1.0), frameColor=(0, 0, 0, 0.5), pos=(-1.1, 0, 0))

        # self.set_frame_color = (1, 0, 0, 1)
        # self.setText('this is frame')
        # self.initialiseoptions(self)
        # self.reparent_to(base.aspect2d)
        # self.set_pos(-0.5, 0, -0.


    def create_gui(self):
        font = base.loader.loadFont('font/Candaral.ttf')
        # font = base.loader.loadFont('font/SegUIVar.ttf')
        self.button = DirectButton(
            parent=base.aspect2d,
            relief=None,
            frameSize=(-0.3, 0.3, -0.1, 0.1),
            text='START',
            pos=(0, 0, 0),
            text_fg=(1, 1, 1, 1),
            text_scale=0.15,
            text_font=font,
            command='',
            # frameColor=(1, 1, 1, 1)
        )
        self.button.guiItem.set_focus(True)

        self.button.bind(DGG.ENTER, self.mouse_over)
        self.button.bind(DGG.EXIT, self.mouse_out)
        # self.button.bind('fin-', self.mouse_over)
        # self.button.bind('fout-', self.mouse_out)

        # self.button = DirectButton(
        #     parent=self,
        #     relief=None,
        #     frameSize=(-1, 1, -0.5, 0.5),
        #     text='QUIT',
        #     pos=(0, 0, -0.2),
        #     text_fg=(1, 1, 1, 1),
        #     text_scale=0.15,
        #     text_font=font,
        #     command=''
        # )
    
    def mouse_over(self, param=None):
        # blendType: see https://docs.panda3d.org/1.10/python/programming/intervals/lerp-intervals
        self.button.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()
        self.button.guiItem.set_state(2)
        print('hello')

    def mouse_out(self, param=None):
        self.button.colorScaleInterval(0.2, (1, 1, 1, 0.5), blendType='easeInOut').start()
        self.button.guiItem.set_state(0)