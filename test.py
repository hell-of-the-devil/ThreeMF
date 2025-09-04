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