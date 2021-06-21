import bpy
from logging import getLogger
import mathutils
from bpy_extras import view3d_utils
import random

logger = getLogger(__name__)

translation = bpy.app.translations.pgettext


def get_region_and_space(context, area_type, region_type, space_type):
    """https://colorful-pico.net/introduction-to-addon-development-in-blender/2.8/html/chapter_03/08_Use_Coordinate_Transformation.html"""
    region = None
    area = None
    space = None

    # 指定されたエリアの情報を取得する
    for a in context.screen.areas:
        if a.type == area_type:
            area = a
            break
    else:
        return (None, None)
    # 指定されたリージョンの情報を取得する
    for r in area.regions:
        if r.type == region_type:
            region = r
            break
    # 指定されたスペースの情報を取得する
    for s in area.spaces:
        if s.type == space_type:
            space = s
            break

    return (region, space)


def get_location3d(
    context: bpy.types.Context,
    event: bpy.types.Event,
    depth_location: mathutils.Vector = mathutils.Vector([1, 1, 1]),
):
    # マウスカーソルのリージョン座標を取得
    mv = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
    # [3Dビューポート] スペースを表示するエリアの [Window] リージョンの
    # 情報と、[3Dビューポート] スペースのスペース情報を取得する
    region, space = get_region_and_space(context, "VIEW_3D", "WINDOW", "VIEW_3D")
    # グローバル座標
    location = view3d_utils.region_2d_to_location_3d(
        region, space.region_3d, mv, depth_location
    )

    return location


def get_local_coord_from_global_coord(obj: bpy.types.Object, location):
    """グローバル座標からローカル座標を求めたい"""
    matrix = obj.matrix_world
    matrix = mathutils.Matrix(matrix).inverted_safe()
    # 行列何もわからん
    local_location = matrix @ location
    return local_location


def random_vector(factor: float = 1.0):
    return mathutils.Vector([random.uniform(-1, 1) * factor for _ in range(3)])


class ScatterGpencilOps(bpy.types.Operator):
    """散布ブラシオペレータ"""

    bl_idname = "gpencil.scatter_ops"
    bl_label = "scatter gpencil"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}
    bl_space_type = "VIEW_3D"
    bl_context_mode = "PAINT_GPENCIL"

    draw_rate: bpy.props.FloatProperty(
        name="draw rate",
        default=10,
        min=0.1,
        soft_max=60,
        max=240,
        description="draw/sec",
    )
    scatter_rate: bpy.props.FloatProperty(
        name="scatter rate",
        default=0.5,
        soft_max=100,
        soft_min=0,
        description="散乱具合",
    )
    size: bpy.props.IntProperty(
        name="brush size", default=20, min=1, max=1000, description="ブラシサイズ"
    )

    _timer = None
    _stroke: bpy.types.GPencilStroke = None
    _obj: bpy.types.Object = None

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
            location = get_location3d(context, event)
            self.report(
                {"INFO"},
                f"location:{location}"
                f"pressure:{event.pressure},is_tablet:{event.is_tablet}",
            )
            stroke = self._stroke
            stroke.points.add(1)
            point = stroke.points[-1]
            location = get_local_coord_from_global_coord(self._obj, location)
            point.co = location + random_vector(self.scatter_rate)
            if event.is_tablet:
                point.pressure = event.pressure
            else:
                point.pressure = 1
        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.area.type == "VIEW_3D":
            if context.active_object.type == "GPENCIL":
                # いろいろ初期化
                wm = context.window_manager
                # タイマー設定
                rate = 1 / self.draw_rate
                self._timer = wm.event_timer_add(rate, window=context.window)
                wm.modal_handler_add(self)
                # アクティブレイヤーの取得とストローク生成
                self.report({"INFO"}, str(context.active_gpencil_layer.info))
                layer = context.active_gpencil_layer
                strokes = layer.active_frame.strokes
                new_stroke: bpy.types.GPencilStroke = strokes.new()
                # アクティブマテリアルを割り当て
                material_index = bpy.context.object.active_material_index
                new_stroke.material_index = material_index
                # 太さを設定
                new_stroke.line_width = self.size
                self._stroke = new_stroke
                self._obj = context.active_object

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

    def draw_settings(context, layout, tool):
        props = tool.operator_properties("gpencil.scatter_ops")
        layout.prop(props, "draw_rate")
        layout.prop(props, "scatter_rate")
        layout.prop(props, "size")


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
