import bpy, bmesh, os, importlib, sys, subprocess
from bpy.props import StringProperty, BoolProperty
from bpy.types import Context, Material
from bpy_extras.io_utils import ImportHelper, ExportHelper
import lib3mf

from .utils import lib3mf_color_to_linear, create_principled_material, create_texture_material

class ThreeMFModel:
    def __init__(self, filepath=None):
        self.wrapper = lib3mf.get_wrapper()
        self.model: lib3mf.Model = self.wrapper.CreateModel() ## type: ignore
        if filepath:
            self.model.QueryReader("3mf").ReadFromFile(filepath)

    def _import_populate_materials(self):
        color_groups: lib3mf.ColorGroupIterator = self.model.GetColorGroups()

        materials = {}

        while color_groups.MoveNext():
            group: lib3mf.ColorGroup = color_groups.GetCurrentColorGroup()
            prop_ids = group.GetAllPropertyIDs()

            for pid in prop_ids:
                color = group.GetColor(pid)

                linear_rgba = lib3mf_color_to_linear(color)
                mat_name = f"ColorGroup_{group.GetResourceID()}_{pid}"
                mat = create_principled_material(mat_name, color=linear_rgba, alpha=linear_rgba[3])
                materials[(group.GetResourceID(), pid)] = mat

        return materials

    def _import_mesh_objects(self, context, materials: dict[tuple[int, int], Material]):
        bi: lib3mf.MeshObjectIterator = self.model.GetMeshObjects()

        while bi.MoveNext():
            mesh: lib3mf.MeshObject = bi.GetCurrentMeshObject()
            me = bpy.data.meshes.new(mesh.GetName() or '3mf Mesh')

            verts, _, faces = self._3mf2blender_translation(mesh)

            me.from_pydata(verts, [], faces)
            # meshes.append(me)

            obj = bpy.data.objects.new(mesh.GetName() or '3mf Object', me)

            if context.collection:
                context.collection.objects.link(obj)

            # Assign materials to the mesh
            props = mesh.GetAllTriangleProperties()
            mat_indices = {}
            for t_index, t in enumerate(faces):
                prop = props[t_index]
                key = (prop.ResourceID, prop.PropertyIDs[0])  # ColorGroup + property
                mat = materials.get(key)
                if mat:
                    # Add material to mesh if not added yet
                    if mat.name not in obj.data.materials:
                        obj.data.materials.append(mat)
                    mat_slot_index = obj.data.materials.find(mat.name)
                    # Assign polygon’s material index
                    me.polygons[t_index].material_index = mat_slot_index

            ## select and make active
            if bpy.context.view_layer:
                bpy.context.view_layer.objects.active = obj
            obj.select_set(True)

    def save(self, filepath):
        writer = self.model.QueryWriter("3mf")
        writer.WriteToFile(filepath)

    def _3mf2blender_translation(self, mesh):
        vertices = mesh.GetVertices()
        triangles = mesh.GetTriangleIndices()

        ## convert vertex data to tuple for blender
        verts = [(v.Coordinates[0], v.Coordinates[1], v.Coordinates[2]) for v in vertices]

        ## convert triangle data to a list[tuple] for Blender
        faces = []
        for t in triangles:
            ## lib3mf returns the indices as a C-style array, we convert this to a tuple for blender
            indices = (t.Indices[0], t.Indices[1], t.Indices[2])
            faces.append(indices)

        return (verts, [], faces)

class Import3MF(bpy.types.Operator, ImportHelper):
    """
        Import a 3mf file
    """
    bl_idname = "import_3mf.3mf"
    bl_label = "Import 3MF (3D Manufacturing Format)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".3mf"
    filter_glob: StringProperty(default="*.3mf", options={'HIDDEN'}, maxlen=255) ## type: ignore
    
    def execute(self, context):
        filepath = self.filepath ## type: ignore

        try:
            tmf_model = ThreeMFModel(filepath=filepath)
            materials = tmf_model._import_populate_materials()
            self.report({'INFO'}, f"materials = {materials}")
            tmf_model._import_mesh_objects(context, materials)

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import 3MF file: {e}")
            return {'CANCELLED'}

class Export3MF(bpy.types.Operator, ExportHelper):
    """
        Export a 3mf file
    """
    bl_idname = "export_3mf.3mf"
    bl_label = "Export 3MF (3D Manufacturing Format)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".3mf"
    filter_glob: StringProperty(default="*.3mf", options={'HIDDEN'}, maxlen=255) ## type: ignore
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        return False

    def execute(self, context):
        filepath = self.filepath ## type: ignore

        # try:
        #     tmf_model = ThreeMFModel(filepath=filepath)
        #     materials = tmf_model._import_populate_materials()
        #     self.report({'INFO'}, f"materials = {materials}")
        #     tmf_model._import_mesh_objects(context, materials)

        #     return {'FINISHED'}
        # except Exception as e:
        self.report({'ERROR'}, f"Exporting has not been fully implemented yet!")
        return {'ERROR'}

classes = (Import3MF, Export3MF)

## Blender Registration
def menu_func_import(self, context):
    self.layout.operator(Import3MF.bl_idname, text="3D Manufacturing Format (.3mf)")

def menu_func_export(self, context):
    self.layout.operator(Export3MF.bl_idname, text="3D Manufacturing Format (.3mf)")

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()

