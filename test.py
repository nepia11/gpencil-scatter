import bpy

module_name = "gpencil-scatter"

bpy.ops.script.reload()
bpy.ops.preferences.addon_disable(module=module_name)
bpy.ops.preferences.addon_enable(module=module_name)
