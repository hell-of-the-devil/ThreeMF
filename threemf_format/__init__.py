import bpy, bmesh, os, importlib, sys, subprocess
from bpy.props import StringProperty, BoolProperty
from bpy.types import Context
from bpy_extras.io_utils import ImportHelper, ExportHelper
import lib3mf
## Import Operator

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
        wrapper = lib3mf.get_wrapper()
        model: lib3mf.Model = wrapper.CreateModel() ## type: ignore

        try:
            reader: lib3mf.Reader = model.QueryReader("3mf")
            reader.ReadFromFile(filepath)

            ## create new blender mesh object
            bm = bmesh.new()

            ## iterate our model meshes
            # for build_item in model.GetObjects():
            bi: lib3mf.ObjectIterator = model.GetObjects()
            meshes = []

            while bi.MoveNext():
                obj = bi.GetCurrentObject()
                if isinstance(obj, lib3mf.MeshObject):
                    ## we have a mesh object
                    me = bpy.data.meshes.new("3MF_Mesh")

                    translation = self._3mf2blender_translation(obj)

                    me.from_pydata(*translation)
                    meshes.append(me)
            
            for mesh in meshes:
                obj = bpy.data.objects.new("3MF_Object", mesh)

                if context.collection:
                    context.collection.objects.link(obj)

                ## select and make active
                if bpy.context.view_layer:
                    bpy.context.view_layer.objects.active = obj
                obj.select_set(True)

                self.report({'INFO'}, f"obj = {obj}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to import 3MF file: {e}")
            return {'CANCELLED'}
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

classes = (Import3MF,)

class MF_OT_preferences(bpy.types.Operator):
    bl_idname = "import_3mf.preferences"
    bl_label = "Preferences"
    bl_description = ("Define addon specific preferences")
    bl_options = {"REGISTER", "INTERNAL"}


    def execute(self, context):
        return {"FINISHED"}


class MF_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        layout = self.layout
        layout.operator(MF_OT_preferences.bl_idname, icon="CONSOLE")


preference_classes = (MF_OT_preferences, MF_preferences)

## Blender Registration
def menu_func_import(self, context):
    self.layout.operator(Import3MF.bl_idname, text="3D Manufacturing Format (.3mf)")

def register():
    ## load our preference classes
    for cls in preference_classes:
        bpy.utils.register_class(cls)
    
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

def unregister():
    for cls in preference_classes:
        bpy.utils.unregister_class(cls)

    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    register()

