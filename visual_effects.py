from panda3d.core import NodePath, PandaNode
from panda3d.core import ColorBlendAttrib, TextureStage
from panda3d.core import Vec2

from create_geomnode import TextureAtlasNode


class VFX(NodePath):

    def __init__(self, texture, split_size, scale, target):
        self.div_u, self.div_v = 1 / split_size.x, 1 / split_size.y
        super().__init__(TextureAtlasNode(self.div_u, 1 - self.div_v))
        self.set_attrib(ColorBlendAttrib.make(
            ColorBlendAttrib.M_add,
            ColorBlendAttrib.O_incoming_alpha,
            ColorBlendAttrib.O_one
        ))
        self.set_texture(TextureStage.get_default(), texture, 1)
        self.set_bin('fixed', 40)
        self.set_depth_write(False)
        self.set_depth_test(False)
        self.set_light_off()
        self.set_scale(scale)
        self.flatten_light()

        self.target = target
        self.tex_u = -self.div_u
        self.tex_v = 0


class VisualEffects(NodePath):

    def __init__(self):
        super().__init__('visual_effects')
        self.reparent_to(base.render)
        self.is_playing = False

    def make_effects(self, tex_path, split_size, scale, *targets):
        tex = base.loader.load_texture(tex_path)

        for target in targets:
            target_np = NodePath(target)
            vfx = VFX(tex, split_size, scale, target_np)
            vfx.reparent_to(self)
            yield vfx

    def start_disappear(self, tex_path, scale, *targets, split_size=Vec2(8, 8), delay=0.05):
        effects = [e for e in self.make_effects(tex_path, split_size, scale, *targets)]

        self.is_playing = True
        base.taskMgr.do_method_later(
            delay,
            self.disappear,
            'vfx_disappear',
            extraArgs=[effects],
            appendTask=True
        )

    def texture_offset(self, vfx):
        vfx.set_pos(vfx.target.get_pos(base.render))
        vfx.tex_u += vfx.div_u

        # go to the next row
        if vfx.tex_u >= 1.0:
            vfx.tex_u = 0
            vfx.tex_v -= vfx.div_v
        # comes to the col end
        if vfx.tex_v <= -1:
            return False

        vfx.look_at(base.camera)
        vfx.set_tex_offset(TextureStage.get_default(), vfx.tex_u, vfx.tex_v)

        return True

    def disappear(self, effects, task):
        for i in range(len(effects)):
            vfx = effects[i]

            if vfx.tex_u + vfx.div_u == 1.0 and vfx.tex_v == 0:
                vfx.target.hide()

            if not self.texture_offset(vfx):
                effects[i] = vfx.remove_node()

        if not any(e for e in effects):
            self.is_playing = False
            return task.done

        return task.again

    def run(self, effects, task):
        # for parent, vfx in list(self.vfx_dic.items()):
        # for vfx in effects:
        for i in range(len(effects)):
            vfx = effects[i]
            vfx.set_pos(vfx.target.get_pos(base.render))
            vfx.tex_u += vfx.div_u

            if vfx.tex_u == 1.0 and vfx.tex_v == 0:
                vfx.target.hide()

            # go to the next row
            if vfx.tex_u >= 1.0:
                # NodePath(parent).hide()
                vfx.tex_u = 0
                vfx.tex_v -= vfx.div_v
            # comes to the col end
            if vfx.tex_v <= -1:
                effects[i] = vfx.remove_node()
                # del self.vfx_dic[parent]
                continue

            vfx.look_at(base.camera)
            vfx.set_tex_offset(TextureStage.get_default(), vfx.tex_u, vfx.tex_v)

        # if not len(self.vfx_dic):
        if not any(e for e in effects):
            print('effect finish')
            self.is_playing = False
            return task.done

        return task.again
