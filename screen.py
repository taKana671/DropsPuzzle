# from direct.gui.DirectFrame import DirectFrame

from direct.gui.DirectFrame import DirectFrame
import direct.gui.DirectGuiGlobals as DGG
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from panda3d.core import CardMaker, LColor
from direct.interval.IntervalGlobal import Sequence, Func, Wait


class Frame(DirectFrame):

    def __init__(self, parent, hide=False):
        super().__init__(parent=parent)
        self.initialiseoptions(type(self))
        self.group = []

        if hide:
            self.hide()


class Label(DirectLabel):

    def __init__(self, parent, text, pos, font, text_scale=0.2):
        super().__init__(
            parent=parent,
            text=text,
            pos=pos,
            text_fg=(1, 1, 1, 1),
            text_font=font,
            text_scale=text_scale,
            frameColor=(1, 1, 1, 0)
        )

        self.initialiseoptions(type(self))


class Button(DirectButton):

    def __init__(self, parent, text, pos, font, command, focus=False):
        super().__init__(
            parent=parent,
            relief=None,
            frameSize=(-0.3, 0.3, -0.07, 0.07),
            text=text,
            pos=pos,
            text_fg=(1, 1, 1, 1),
            text_scale=0.12,
            text_font=font,
            text_pos=(0, -0.04),
            command=command
        )

        # name, default, function
        # optiondefs = (
        #     ('numStates', 2, None),   
        #     ('state', DGG.NORMAL, None),
        #     ('relief', DGG.RIDGE, None),
        #     ('frameSize',  (-2, 2, -1, 1), None),
        #     ('invertedFrames', (1,), None),
        #     ('pressEffect', 1, DGG.INITOPT),
        # )

        # self.defineoptions(kw, optiondefs)
        # super().__init__(parent=parent)
        self.initialiseoptions(type(self))

        parent.group.append(self)
        self.btn_group = parent.group
        self.is_focus = None

        if focus:
            self.focus()
        else:
            self.blur()

        self.bind(DGG.ENTER, self.focus)
        self.bind(DGG.EXIT, self.blur)

    def focus(self, param=None):
        self.is_focus = True
        self.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()

        for btn in self.btn_group:
            if btn != self and btn.is_focus:
                btn.blur()
                break

    def blur(self, param=None):
        if all(not btn.is_focus for btn in self.btn_group if btn != self):
            return

        self.is_focus = False
        self.colorScaleInterval(0.2, (1, 1, 1, 0.5), blendType='easeInOut').start()


class Screen:

    def __init__(self, gui=None):
        cm = CardMaker("card")
        cm.set_frame_fullscreen_quad()
        self.background = base.render2d.attach_new_node(cm.generate())
        self.background.set_transparency(1)
        self.background.set_color(LColor(0, 0, 0, 1.0))

        self.gui = gui

    
    def switch(self, gui):
        self.gui = gui

    def fade_out(self):
        Sequence(
            Func(self.gui.hide),
            self.background.colorInterval(0.5, LColor(0, 0, 0, 0)),
            # Func(base.messenger.send, 'gamestart')
        ).start()

    def fade_in(self):
        Sequence(
            self.background.colorInterval(0.5, LColor(0, 0, 0, 1.0)),
            Func(self.gui.show)
        ).start()

    def hide(self):
        self.gui.hide()
        self.background.hide()

    def show(self):
        self.gui.show()
        self.background.show()




class Screen1:

    def __init__(self, gui):
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
        # self.button.hide()

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


# class Button1:

#     def __init__(self, parent, text, size, pos, font, command, text_fg=(1, 1, 1, 1), text_scale=0.5):
#         # font = base.loader.loadFont('font/Candaral.ttf')
#         # font = base.loader.loadFont('font/Candaral.ttf')

#         # self.initialiseoptions(Button)
#         self.button = DirectButton(
#             parent=parent.frame,
#             relief=None,
#             frameSize=(-0.3, 0.3, -0.1, 0.1),
#             text='START',
#             pos=(0, 0, 0),
#             text_fg=(1, 1, 1, 1),
#             text_scale=0.15,
#             text_font=font,
#             command='',
#             # frameColor=(1, 1, 1, 1)
#         )

#         self.button.guiItem.set_focus(True)
#         self.button.bind(DGG.ENTER, self.mouse_over)
#         self.button.bind(DGG.EXIT, self.mouse_out)

#     def mouse_over(self, param=None):
#         # blendType: see https://docs.panda3d.org/1.10/python/programming/intervals/lerp-intervals
#         self.button.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()
#         self.button.guiItem.set_state(2)
#         print('hello')

#     def mouse_out(self, param=None):
#         self.button.colorScaleInterval(0.2, (1, 1, 1, 0.5), blendType='easeInOut').start()
#         self.button.guiItem.set_state(0)


# class Button(DirectButton):

#     def __init__(self, parent, text, size, pos, font, command, text_fg=(1, 1, 1, 1), text_scale=0.5):

#         super().__init__(
#             parent=parent,
#             relief=None,
#             frameSize=(-0.3, 0.3, -0.1, 0.1),
#             text=text,
#             pos=pos,
#             text_fg=(1, 1, 1, 1),
#             text_scale=0.15,
#             text_font=font,
#             command='',
#             frameColor=(1, 1, 1, 1)
#         )

#         # name, default, function

#         # optiondefs = (
#         #     # ('numStates', 2, None),
#         #     # ('state', DGG.NORMAL, None),
#         #     ('relief', DGG.RIDGE, None),
#         #     ('frameSize',  (-2, 2, -1, 1), None),
#         #     # ('invertedFrames', (1,), None),
#         #     # ('pressEffect', 1, DGG.INITOPT),
#         # )
#         # self.defineoptions(kw, optiondefs)

#         super().__init__(parent=base.aspect2d)




#         self.initialiseoptions(type(self))

#         self.guiItem.set_focus(True)
#         self.bind(DGG.ENTER, self.mouse_over)
#         self.bind(DGG.EXIT, self.mouse_out)




#         # self.button = DirectButton(
#         #     parent=base.aspect2d,
#         #     relief=None,
#         #     frameSize=(-0.3, 0.3, -0.1, 0.1),
#         #     text='START',
#         #     pos=(0, 0, 0),
#         #     text_fg=(1, 1, 1, 1),
#         #     text_scale=0.15,
#         #     text_font=font,
#         #     command='',
#         #     # frameColor=(1, 1, 1, 1)
#         # )


#         # super().__init__(
#         #     # relief=None,
#         #     text=text,
#         #     frameSize=(-1, 1, -1, 1),  # (-0.3, 0.3, -0.1, 0.1),
#         #     pos=pos,
#         #     text_fg=text_fg,
#         #     text_scale=text_scale,
#         #     text_font=font,
#         #     command=command,
#         #     # parent=parent,

#         # )

#     def mouse_over(self, param=None):
#         # blendType: see https://docs.panda3d.org/1.10/python/programming/intervals/lerp-intervals
#         self.colorScaleInterval(0.2, (1, 1, 1, 1), blendType='easeInOut').start()
#         self.guiItem.set_state(2)

#         print('hello')

#     def mouse_out(self, param=None):
#         self.colorScaleInterval(0.2, (1, 1, 1, 0.5), blendType='easeInOut').start()
#         self.guiItem.set_state(0)