import bpy

def create_principled_material(name, color=(1, 1, 1, 1), roughness=0.5, metallic=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.use_transparent_shadow = True if alpha < 1.0 else False
    mat.blend_method = 'BLEND' if alpha < 1.0 else 'OPAQUE'
    # mat.shadow_method = 'HASHED' if alpha < 1.0 else 'OPAQUE'

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
        bsdf.inputs['Alpha'].default_value = alpha
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic

    return mat

def create_texture_material(name, image_path, uv_layer_name="UVMap"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree

    bsdf = nt.nodes["Principled BSDF"]
    tex_image = nt.nodes.new("ShaderNodeTexImage")
    tex_image.image = bpy.data.images.load(image_path)

    uv_map = nt.nodes.new("ShaderNodeUVMap")
    uv_map.uv_map = uv_layer_name

    nt.links.new(uv_map.outputs["UV"], tex_image.inputs["Vector"])
    nt.links.new(tex_image.outputs["Color"], bsdf.inputs["Base Color"])

    return mat

def show_message(context, message="Something happened"):
    def draw(self, _context):
        self.layout.label(text=message)
    context.window_manager.popup_menu(draw, title="Info", icon='INFO')

def lib3mf_color_to_linear(color):
    def srgb_to_linear(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (
        srgb_to_linear(color.Red / 255.0),
        srgb_to_linear(color.Green / 255.0),
        srgb_to_linear(color.Blue / 255.0),
        color.Alpha / 255.0
    )