import lib3mf

from lib3mf import get_wrapper, Reader, Wrapper

filename = "data/rack.3mf"

## get wrapper
wrapper = lib3mf.Wrapper()

## create model
model: lib3mf.Model = wrapper.CreateModel()

reader = model.QueryReader("3mf")
reader.ReadFromFile(filename)

obj_iter: lib3mf.ObjectIterator = model.GetObjects()

while obj_iter.MoveNext():
    obj = obj_iter.GetCurrentObject()    
    print(obj)










            while bi.MoveNext():
                mesh_object: lib3mf.BuildItem = bi.GetCurrent()
                mesh = mesh_object.GetObjectResource()

                # self.report({'INFO'}, f"{type(mesh)}")

                if isinstance(mesh, lib3mf.ComponentsObject):
                    for index in range(mesh.GetComponentCount()):
                        me = bpy.data.meshes.new("3MF_Mesh")
                        real_mesh = mesh.GetComponent(index).GetObjectResource()
                        translation = self._3mf2blender_translation(real_mesh)
                        me.from_pydata(*translation)

                    ## link new mesh to scene
                    obj = bpy.data.objects.new(f"3MF_Object", me)
                    if context.collection:
                        context.collection.objects.link(obj)

                    ## select and make active
                    if bpy.context.view_layer:
                        bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    self.report({'INFO'}, f"Successfully imported {mesh.GetComponentCount()} components from {filepath}")
                    return {'FINISHED'}
                elif isinstance(mesh, lib3mf.MeshObject):
                    me = bpy.data.meshes.new("3MF_Mesh")

                    ## get our vertices and triangles

                    translation = self._3mf2blender_translation(mesh)
                    ## create a new blender mesh from the data
                    me.from_pydata(*translation)

                    ## link new mesh to scene
                    obj = bpy.data.objects.new("3mf_object", me)
                    if context.collection:
                        context.collection.objects.link(obj)

                    ## select and make active
                    if bpy.context.view_layer:
                        bpy.context.view_layer.objects.active = obj
                    obj.select_set(True)

                    self.report({'INFO'}, f"Successfully imported {len(translation[0])} verticies from {filepath}")
                    return {'FINISHED'}


                else:
                    self.report({'ERROR'}, f"Unknown mesh type: {type(mesh)}")
                    return {'CANCELLED'}