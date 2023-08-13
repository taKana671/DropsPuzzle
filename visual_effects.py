from collections import deque
from typing import NamedTuple

from panda3d.core import NodePath
from panda3d.core import ColorBlendAttrib, TextureStage

from create_geomnode import TextureAtlasNode


class TextureAtlas:

    def __init__(self, file_name, cols=8, rows=8, tgt_remove_col=8, tgt_remove_row=4):
        self.texture = self.load(file_name)
        self.div_u = 1 / cols
        self.div_v = 1 / rows
        self.tgt_remove_u = self.div_u * tgt_remove_col
        self.tgt_remove_v = -self.div_v * tgt_remove_row

    def load(self, file_name):
        path = f'textures/{file_name}'
        tex = base.loader.load_texture(path)
        return tex


class VFXSetting(NamedTuple):

    texture: TextureAtlas
    scale: float


class VFX(NodePath):

    def __init__(self, vfx_settings, target):
        tex, scale = vfx_settings.texture, vfx_settings.scale
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
        self.set_scale(scale)
        self.flatten_light()

        self.target = target
        self.target_pos = target.get_pos(base.render)
        self.pos_u = -tex.div_u
        self.pos_v = 0
        self.tex = tex

    def texture_offset(self):
        self.set_pos(self.target_pos)
        self.pos_u += self.tex.div_u

        # go to the next row
        if self.pos_u >= 1.0:
            self.pos_u = 0
            self.pos_v -= self.tex.div_v
        # comes to the end
        if self.pos_v <= -1:
            return False

        self.look_at(base.camera)
        self.set_tex_offset(TextureStage.get_default(), self.pos_u, self.pos_v)

        return True


class VFXManager(NodePath):

    def __init__(self):
        super().__init__('visual_effects')
        self.reparent_to(base.render)
        self.drops_q = deque()

    def make_effects(self, vfx_settings, *targets):
        for target_nd in targets:
            target_nd.set_tag('effecting', '')
            target_np = NodePath(target_nd)
            vfx = VFX(vfx_settings, target_np)
            vfx.reparent_to(self)
            yield vfx

    def start_disappear(self, vfx_settings, *targets, delay=0.05):
        effects = [e for e in self.make_effects(vfx_settings, *targets)]

        base.taskMgr.do_method_later(
            delay,
            self.disappear,
            'vfx_disappear',
            extraArgs=[effects],
            appendTask=True
        )

    def disappear(self, effects, task):
        for i, vfx in enumerate(effects):
            if vfx.pos_u + vfx.tex.div_u == vfx.tex.tgt_remove_u \
                    and vfx.pos_v == vfx.tex.tgt_remove_v:
                self.drops_q.append(vfx.target)

            if not vfx.texture_offset():
                effects[i] = vfx.remove_node()

        if not any(e for e in effects):
            return task.done

        return task.again