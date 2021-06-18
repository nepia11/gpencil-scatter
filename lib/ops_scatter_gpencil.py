import bpy
from logging import getLogger

logger = getLogger(__name__)

translation = bpy.app.translations.pgettext


class ScatterGpencilOps(bpy.types.Operator):
    """散布ブラシオペレータ"""

    bl_idname = "gpencil.scatter_ops"
    bl_label = "scatter gpencil"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_space_type = "VIEW_3D"
    bl_context_mode = "PAINT_GPENCIL"

    scatter_rate: bpy.props.FloatProperty(
        name="scatter_rate",
        default=0.5,
    )

    _timer = None

    def modal(self, context, event):
        # 非常終了
        if event.type == "ESC":
            self.cancel(context)
            self.report({"INFO"}, "canceld")
            return {"CANCELLED"}

        if event.type == "LEFTMOUSE":
            if event.value == "RELEASE":
                self.cancel(context)
                return {"FINISHED"}

        if event.type == "TIMER":
            self.report(
                {"INFO"},
                f"rate:{self.scatter_rate}type:{event.type},value:{event.value},mouse:{event.mouse_x},{event.mouse_y}",
            )

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.area.type == "VIEW_3D":
            print("exec")
            wm = context.window_manager
            rate = self.scatter_rate
            self._timer = wm.event_timer_add(rate, window=context.window)
            wm.modal_handler_add(self)
            # return {"FINISHED"}
            return {"RUNNING_MODAL"}
        self.cancel(context)
        return {"CANCELLED"}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


class ScatterGpencilTool(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "PAINT_GPENCIL"
    bl_idname = "gpencil.scatter_tool"
    bl_label = "scatter gpencil"
    bl_description = "This is a tooltip\n" "with multiple lines"
    bl_icon = "brush.paint_weight.average"
    bl_widget = None
    bl_keymap = (
        (
            "gpencil.scatter_ops",
            {"type": "LEFTMOUSE", "value": "PRESS"},
            None,
        ),
        (
            "gpencil.scatter_ops",
            {"type": "LEFTMOUSE", "value": "RELEASE"},
            None,
        ),
    )

    # def draw_settings(context, layout, tool):
    # layout.label(icon_value=0)
    #     pass
    #     # props = tool.operator_properties("view3d.select_circle")
    #     # layout.prop(props, "mode")
    #     # layout.prop(props, "radius")


classses = [ScatterGpencilOps]
tools = [ScatterGpencilTool]


def register():
    for c in classses:
        bpy.utils.register_class(c)
    for t in tools:
        bpy.utils.register_tool(t)


def unregister():
    for c in classses:
        bpy.utils.unregister_class(c)
    for t in tools:
        bpy.utils.unregister_tool(t)
