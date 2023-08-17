from collections import deque
from typing import NamedTuple

from panda3d.core import NodePath
from panda3d.core import Vec3
from panda3d.core import ColorBlendAttrib, TextureStage

from create_geomnode import TextureAtlasNode


class TextureAtlas:

    def __init__(self, file_name, cols=8, rows=8, vfx_end_row=8, tgt_remove_row=4):
        self.texture = self.load(file_name)
        self.div_u = 1 / cols
        self.div_v = 1 / rows
        self.tgt_remove_v = -self.div_v * tgt_remove_row
        self.vfx_end_v = -self.div_v * vfx_end_row

    def load(self, file_name):
        path = f'textures/{file_name}'
        tex = base.loader.load_texture(path)
        return tex


class VFXSetting(NamedTuple):

    texture: TextureAtlas
    scale: float
    offset: Vec3 = Vec3(0, 0, 0)


class VFX(NodePath):

    def __init__(self, settings, target):
        tex = settings.texture
        super().__init__(TextureAtlasNode(tex.div_u, 1 - tex.div_v))
        self.set_attrib(ColorBlendAttrib.make(
            ColorBlendAttrib.M_add,
            ColorBlendAttrib.O_incoming_alpha,
            ColorBlendAttrib.O_one
        ))
        self.set_texture(TextureStage.get_default(), tex.texture, 1)
        self.set_bin('fixed', 40)
        self.set_depth_write(False)
        self.set_depth_test(False)
        self.set_light_off()
        self.set_scale(settings.scale)
        self.flatten_light()

        self.target = target
        self.pos_u = -tex.div_u
        self.pos_v = 0

        self.offset = settings.offset
        self.tex = tex

    def texture_offset(self):
        if self.target:
            self.set_pos(self.target.get_pos(base.render) + self.offset)

        self.pos_u += self.tex.div_u

        # go to the next row
        if self.pos_u >= 1.0:
            self.pos_u = 0
            self.pos_v -= self.tex.div_v

        # comes to the end
        if self.pos_v <= self.tex.vfx_end_v:
            return False

        self.look_at(base.camera)
        self.set_tex_offset(TextureStage.get_default(), self.pos_u, self.pos_v)

        return True


class VFXRunner:

    def start(self, delay=0.05):
        base.taskMgr.do_method_later(delay, self.run, 'vfx')

    def run(self, *args, **kwargs):
        """Override in sub classes."""
        raise NotImplementedError


class DisappearEffect(VFXRunner):

    def __init__(self, effects, drops_q):
        self.effects = effects
        self.drops_q = drops_q

    # def start(self, delay=0.05):
    #     base.taskMgr.do_method_later(delay, self.run, 'vfx_disappear')

    def run(self, task):
        for i, vfx in enumerate(self.effects):
            if vfx.pos_u + vfx.tex.div_u == 1.0 \
                    and vfx.pos_v == vfx.tex.tgt_remove_v:
                self.drops_q.append(vfx.target)
                vfx.target = None

            if not vfx.texture_offset():
                self.effects[i] = vfx.remove_node()

        if not any(e for e in self.effects):
            return task.done

        return task.again


class ShortEffect(VFXRunner):

    def __init__(self, vfx):
        self.vfx = vfx

    # def start(self, delay=0.05):
    #     base.taskMgr.do_method_later(delay, self.run, 'vfx_short')

    def run(self, task):
        if not self.vfx.texture_offset():
            self.vfx.remove_node()
            return task.done

        return task.again


class VFXManager(NodePath):

    def __init__(self):
        super().__init__('visual_effects')
        self.reparent_to(base.render)
        self.drops_q = deque()

    def make_effect(self, vfx_settings, target_np):
        target_np.set_tag('effecting', '')
        vfx = VFX(vfx_settings, target_np)
        vfx.reparent_to(self)

        return vfx

    def disappear(self, vfx_settings, *targets, delay=0.05):
        effects = [self.make_effect(vfx_settings, NodePath(t)) for t in targets]
        DisappearEffect(effects, self.drops_q).start()

    def short(self, vfx_settings, target, delay=0.05):
        vfx = self.make_effect(vfx_settings, target)
        ShortEffect(vfx).start()
