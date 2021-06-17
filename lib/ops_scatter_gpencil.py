import bpy
from logging import getLogger

logger = getLogger(__name__)

translation = bpy.app.translations.pgettext


class ScatterGpencilTool(bpy.types.WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "PAINT_GPENCIL"
    bl_idname = "gpencil.scatter"
    bl_label = "scatter gpencil"
    bl_description = "This is a tooltip\n" "with multiple lines"
    bl_icon = "brush.gpencil_draw.draw"
    # bl_icon = "QUESTION"
    bl_widget = None
    bl_keymap = (
        (
            "template.capture_color",
            {"type": "LEFTMOUSE", "value": "PRESS"},
            {"properties": [("wait_for_input", False)]},
        ),
    )

    # def draw_settings(context, layout, tool):
    #     pass
    #     # props = tool.operator_properties("view3d.select_circle")
    #     # layout.prop(props, "mode")
    #     # layout.prop(props, "radius")


classses = []
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
