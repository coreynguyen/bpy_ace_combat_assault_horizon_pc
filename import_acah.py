""" ======================================================================

    PythonScript:   [PC] Ace Combat Assault Horizon
    Author:         mariokart64n
    Date:           March 22, 2021
    Version:        0.1

    ======================================================================

    ChangeLog:

    2021-03-22
        Script Wrote

    2021-03-23
        Adapted to work with PS3 Memory dump from Ace Combat Infinity

    ====================================================================== """

import bpy  # Needed to interface with blender
import struct  # Needed for Binary Reader
import math
from pathlib import Path  # Needed for os stuff


useOpenDialog = True


signed, unsigned = 0, 1  # Enums for read function
seek_set, seek_cur, seek_end = 0, 1, 2  # Enums for seek function
SEEK_ABS, SEEK_REL, SEEK_END = 0, 1, 2  # Enums for seek function


def messageBox(message="", title="Message Box", icon='INFO'):
    def draw(self, context): self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
    return None


def clearListener(len=64):
    for i in range(0, len): print('')


def getFilenameFile(file):  # returns: "myImage"
    return Path(file).stem


def getFilenameType(file):  # returns: ".jpg"
    return Path(file).suffix


def toUpper(string):
    return string.upper()


def findItem(array, value):
    index = -1
    try:
        index = array.index(value)
    except:
        pass
    return index


def append(array, value):
    array.append(value)
    return None


def appendIfUnique(array, value):
    try:
        array.index(value)
    except:
        array.append(value)
    return None


class StandardMaterial:
    data = None
    bsdf = None

    def __init__(self, name="Material"):
        # make material
        self.data = bpy.data.materials.new(name=name)
        self.data.use_nodes = True
        self.data.use_backface_culling = True
        self.bsdf = self.data.node_tree.nodes["Principled BSDF"]
        self.bsdf.label = "Standard"
        return None

    def diffuse(self, colour=(0.0, 0.0, 0.0, 0.0), name="Diffuse"):
        rgbaColor = self.data.node_tree.nodes.new('ShaderNodeRGB')
        rgbaColor.label = name
        rgbaColor.outputs[0].default_value = (colour[0], colour[1], colour[2], colour[3])
        if self.bsdf != None:
            self.data.node_tree.links.new(self.bsdf.inputs['Base Color'], rgbaColor.outputs['Color'])
        return None

    def diffuseMap(self, imageTex=None):
        if imageTex != None and self.bsdf != None:
            self.data.node_tree.links.new(self.bsdf.inputs['Base Color'], imageTex.outputs['Color'])
        return None

    def opacityMap(self, imageTex=None):
        if imageTex != None and self.bsdf != None:
            self.data.blend_method = 'BLEND'
            self.data.shadow_method = 'HASHED'
            self.data.show_transparent_back = False
            self.data.node_tree.links.new(self.bsdf.inputs['Alpha'], imageTex.outputs['Alpha'])
        return None

    def normalMap(self, imageNode=None):
        if imageTex != None and self.bsdf != None:
            imageTex.image.colorspace_settings.name = 'Linear'
            normMap = self.data.node_tree.nodes.new('ShaderNodeNormalMap')
            normMap.label = 'ShaderNodeNormalMap'
            self.data.node_tree.links.new(normMap.inputs['Color'], imageTex.outputs['Color'])
            self.data.node_tree.links.new(self.bsdf.inputs['Normal'], normMap.outputs['Normal'])
        return None

    def specularMap(self, imageNode=None, invert=True):
        if imageTex != None and self.bsdf != None:
            if invert:
                invertRGB = self.data.node_tree.nodes.new('ShaderNodeInvert')
                invertRGB.label = 'ShaderNodeInvert'
                self.data.node_tree.links.new(invertRGB.inputs['Color'], imageTex.outputs['Color'])
                self.data.node_tree.links.new(self.bsdf.inputs['Roughness'], invertRGB.outputs['Color'])
            else:
                self.data.node_tree.links.new(self.bsdf.inputs['Roughness'], imageTex.outputs['Color'])
        return None


class fopen:
    little_endian = True
    file = ""
    mode = 'rb'
    data = bytearray()
    size = 0
    pos = 0
    isGood = False

    def __init__(self, filename=None, mode='rb', isLittleEndian=True):
        if mode == 'rb':
            if filename != None and Path(filename).is_file():
                self.data = open(filename, mode).read()
                self.size = len(self.data)
                self.pos = 0
                self.mode = mode
                self.file = filename
                self.little_endian = isLittleEndian
                self.isGood = True
        else:
            self.file = filename
            self.mode = mode
            self.data = bytearray()
            self.pos = 0
            self.size = 0
            self.little_endian = isLittleEndian
            self.isGood = False

        return None

    # def __del__(self):
    #    self.flush()

    def resize(self, dataSize=0):
        if dataSize > 0:
            self.data = bytearray(dataSize)
        else:
            self.data = bytearray()
        self.pos = 0
        self.size = dataSize
        self.isGood = False
        return None

    def flush(self):
        print("flush")
        print("file:\t%s" % self.file)
        print("isGood:\t%s" % self.isGood)
        print("size:\t%s" % len(self.data))
        if self.file != "" and not self.isGood and len(self.data) > 0:
            self.isGood = True

            s = open(self.file, 'w+b')
            s.write(self.data)
            s.close()

    def read_and_unpack(self, unpack, size):
        '''
          Charactor, Byte-order
          @,         native, native
          =,         native, standard
          <,         little endian
          >,         big endian
          !,         network

          Format, C-type,         Python-type, Size[byte]
          c,      char,           byte,        1
          b,      signed char,    integer,     1
          B,      unsigned char,  integer,     1
          h,      short,          integer,     2
          H,      unsigned short, integer,     2
          i,      int,            integer,     4
          I,      unsigned int,   integer,     4
          f,      float,          float,       4
          d,      double,         float,       8
        '''
        value = 0
        if self.size > 0 and self.pos + size < self.size:
            value = struct.unpack_from(unpack, self.data, self.pos)[0]
            self.pos += size
        return value

    def pack_and_write(self, pack, size, value):
        if self.pos + size > self.size:
            self.data.extend(b'\x00' * ((self.pos + size) - self.size))
            self.size = self.pos + size
        try:
            struct.pack_into(pack, self.data, self.pos, value)
        except:
            print('Pos:\t%i / %i (buf:%i) [val:%i:%i:%s]' % (self.pos, self.size, len(self.data), value, size, pack))
            pass
        self.pos += size
        return None

    def set_pointer(self, offset):
        self.pos = offset
        return None

    def set_endian(self, isLittle = True):
        self.little_endian = isLittle
        return isLittle

def fclose(bitStream):
    bitStream.flush()
    bitStream.isGood = False


def fseek(bitStream, offset, dir):
    if dir == 0:
        bitStream.set_pointer(offset)
    elif dir == 1:
        bitStream.set_pointer(bitStream.pos + offset)
    elif dir == 2:
        bitStream.set_pointer(bitStream.pos - offset)
    return None


def ftell(bitStream):
    return bitStream.pos


def readByte(bitStream, isSigned=0):
    fmt = 'b' if isSigned == 0 else 'B'
    return (bitStream.read_and_unpack(fmt, 1))


def readShort(bitStream, isSigned=0):
    fmt = '>' if not bitStream.little_endian else '<'
    fmt += 'h' if isSigned == 0 else 'H'
    return (bitStream.read_and_unpack(fmt, 2))


def readLong(bitStream, isSigned=0):
    fmt = '>' if not bitStream.little_endian else '<'
    fmt += 'i' if isSigned == 0 else 'I'
    return (bitStream.read_and_unpack(fmt, 4))

def readFloat(bitStream):
    fmt = '>f' if not bitStream.little_endian else '<f'
    return (bitStream.read_and_unpack(fmt, 4))


def readHalf(bitStream):
    uint16 = bitStream.read_and_unpack('>H' if not bitStream.little_endian else '<H', 2)
    uint32 = (
            (((uint16 & 0x03FF) << 0x0D) | ((((uint16 & 0x7C00) >> 0x0A) + 0x70) << 0x17)) |
            (((uint16 >> 0x0F) & 0x00000001) << 0x1F)
    )
    return struct.unpack('f', struct.pack('I', uint32))[0]


def readString(bitStream, length=0):
    string = ''
    pos = bitStream.pos
    lim = length if length != 0 else bitStream.size - bitStream.pos
    for i in range(0, lim):
        b = bitStream.read_and_unpack('B', 1)
        if b != 0:
            string += chr(b)
        else:
            if length > 0:
                bitStream.set_pointer(pos + length)
            break
    return string


def mesh_validate (vertices=[], faces=[]):
    #
    # Returns True if mesh is BAD
    #
    # check face index bound
    face_min = 0
    face_max = len(vertices) - 1
    
    for face in faces:
        for side in face:
            if side < face_min or side > face_max:
                print("Face Index Out of Range:\t[%i / %i]" % (side, face_max))
                return True
    return False

def mesh(
    vertices=[],
    faces=[],
    materialIDs=[],
    tverts=[],
    normals=[],
    colours=[],
    materials=[],
    mscale=1.0,
    flipAxis=False,
    obj_name="Object",
    lay_name='',
    position = (0.0, 0.0, 0.0)
    ):
    #
    # This function is pretty, ugly
    # imports the mesh into blender
    #
    # Clear Any Object Selections
    # for o in bpy.context.selected_objects: o.select = False
    bpy.context.view_layer.objects.active = None
    
    # Get Collection (Layers)
    if lay_name != '':
        # make collection
        layer = bpy.data.collections.get(lay_name)
        if layer == None:
            layer = bpy.data.collections.new(lay_name)
            bpy.context.scene.collection.children.link(layer)
    else:
        if len(bpy.data.collections) == 0:
            layer = bpy.data.collections.new("Collection")
            bpy.context.scene.collection.children.link(layer)
        else:
            try:
                layer = bpy.data.collections[bpy.context.view_layer.active_layer_collection.name]
            except:
                layer = bpy.data.collections[0]
    

    # make mesh
    msh = bpy.data.meshes.new('Mesh')

    # msh.name = msh.name.replace(".", "_")

    # Apply vertex scaling
    # mscale *= bpy.context.scene.unit_settings.scale_length
    if len(vertices) > 0:
        vertArray = [[float] * 3] * len(vertices)
        if flipAxis:
            for v in range(0, len(vertices)):
                vertArray[v] = (
                    vertices[v][0] * mscale,
                    -vertices[v][2] * mscale,
                    vertices[v][1] * mscale
                )
        else:
            for v in range(0, len(vertices)):
                vertArray[v] = (
                    vertices[v][0] * mscale,
                    vertices[v][1] * mscale,
                    vertices[v][2] * mscale
                )

    # assign data from arrays
    if mesh_validate(vertArray, faces):
        # Erase Mesh
        msh.user_clear()
        bpy.data.meshes.remove(msh)
        print("Mesh Deleted!")
        return None
    
    msh.from_pydata(vertArray, [], faces)

    # set surface to smooth
    msh.polygons.foreach_set("use_smooth", [True] * len(msh.polygons))

    # Set Normals
    if len(faces) > 0:
        if len(normals) > 0:
            msh.use_auto_smooth = True
            if len(normals) == (len(faces) * 3):
                msh.normals_split_custom_set(normals)
            else:
                normArray = [[float] * 3] * (len(faces) * 3)
                if flipAxis:
                    for i in range(0, len(faces)):
                        for v in range(0, 3):
                            normArray[(i * 3) + v] = (
                                [normals[faces[i][v]][0],
                                 -normals[faces[i][v]][2],
                                 normals[faces[i][v]][1]]
                            )
                else:
                    for i in range(0, len(faces)):
                        for v in range(0, 3):
                            normArray[(i * 3) + v] = (
                                [normals[faces[i][v]][0],
                                 normals[faces[i][v]][1],
                                 normals[faces[i][v]][2]]
                            )
                msh.normals_split_custom_set(normArray)

        # create texture corrdinates
        #print("tverts ", len(tverts))
        # this is just a hack, i just add all the UVs into the same space <<<
        if len(tverts) > 0:
            uvw = msh.uv_layers.new()
            # if len(tverts) == (len(faces) * 3):
            #    for v in range(0, len(faces) * 3):
            #        msh.uv_layers[uvw.name].data[v].uv = tverts[v]
            # else:
            uvwArray = [[float] * 2] * len(tverts[0])
            for i in range(0, len(tverts[0])):
                uvwArray[i] = [0.0, 0.0]

            for v in range(0, len(tverts[0])):
                for i in range(0, len(tverts)):
                    uvwArray[v][0] += tverts[i][v][0]
                    uvwArray[v][1] += 1.0 - tverts[i][v][1]

            for i in range(0, len(faces)):
                for v in range(0, 3):
                    msh.uv_layers[uvw.name].data[(i * 3) + v].uv = (
                        uvwArray[faces[i][v]][0],
                        uvwArray[faces[i][v]][1]
                    )


    # Create Face Maps?
    # msh.face_maps.new()

    # Update Mesh
    msh.update()

    # Check mesh is Valid
    # Without this blender may crash!!! lulz
    # However the check will throw false positives so
    # and additional or a replacement valatiation function
    # would be required
    
    if msh.validate():
        print("Mesh Failed Validation")

        

    # Assign Mesh to Object
    obj = bpy.data.objects.new(obj_name, msh)
    obj.location = position
    # obj.name = obj.name.replace(".", "_")

    for i in range(0, len(materials)):

        if len(obj.material_slots) < (i + 1):
            # if there is no slot then we append to create the slot and assign
            obj.data.materials.append(materials[i])
        else:
            # we always want the material in slot[0]
            obj.material_slots[0].material = materials[i]
        # obj.active_material = obj.material_slots[i].material

    if len(materialIDs) == len(obj.data.polygons):
        for i in range(0, len(materialIDs)):
            obj.data.polygons[i].material_index = materialIDs[i] % len(materials)
    elif len(materialIDs) > 0:
        print("Error:\tMaterial Index Out of Range")

    # obj.data.materials.append(material)
    layer.objects.link(obj)

    # Generate a Material
    # img_name = "Test.jpg"  # dummy texture
    # mat_count = len(texmaps)

    # if mat_count == 0 and len(materialIDs) > 0:
    #    for i in range(0, len(materialIDs)):
    #        if (materialIDs[i] + 1) > mat_count: mat_count = materialIDs[i] + 1

    # Assign Material ID's
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.context.tool_settings.mesh_select_mode = [False, False, True]

    bpy.ops.object.mode_set(mode='OBJECT')
    # materialIDs

    # Redraw Entire Scene
    # bpy.context.scene.update()

    return obj


def deleteScene(include=[]):
    if len(include) > 0:
        # Exit and Interactions
        if bpy.context.view_layer.objects.active != None:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Select All
        bpy.ops.object.select_all(action='SELECT')

        # Loop Through Each Selection
        for o in bpy.context.view_layer.objects.selected:
            for t in include:
                if o.type == t:
                    bpy.data.objects.remove(o, do_unlink=True)
                    break

        # De-Select All
        bpy.ops.object.select_all(action='DESELECT')
    return None

class ndxr_entry_info_cmd_table2:
    unk081 = 0
    name_addr = 0
    name = ""
    unk083 = 0
    unk084 = 0
    unk085 = 0.0
    unk086 = 0.0
    unk087 = 0.0
    unk088 = 0.0

    def read_info_cmd_table2(self, strings_addr=0, f=fopen()):
        self.unk081 = readLong(f, unsigned)
        self.name_addr = readLong(f, unsigned)
        self.unk083 = readLong(f, unsigned)
        self.unk084 = readLong(f, unsigned)
        self.unk085 = readFloat(f)
        self.unk086 = readFloat(f)
        self.unk087 = readFloat(f)
        self.unk088 = readFloat(f)
        pos = ftell(f)
        fseek(f, (strings_addr + self.name_addr), seek_set)
        self.name = readString(f)
        fseek(f, pos, seek_set)


class ndxr_entry_info_cmd_table1:  # 24 bytes
    unk061 = 0
    unk062 = 0
    unk063 = 0
    unk064 = 0
    unk065 = 0
    unk066 = 0
    unk067 = 0
    unk068 = 0
    unk069 = 0
    unk070 = 0
    unk071 = 0
    unk072 = 0
    unk073 = 0
    unk074 = 0
    unk075 = 0
    unk076 = 0

    def read_info_cmd_table1(self, f=fopen()):
        self.unk061 = readByte(f, unsigned)
        self.unk062 = readShort(f, unsigned)
        self.unk063 = readLong(f, unsigned)
        self.unk064 = readByte(f, unsigned)
        self.unk065 = readShort(f, unsigned)
        self.unk066 = readLong(f, unsigned)
        self.unk067 = readByte(f, unsigned)
        self.unk068 = readByte(f, unsigned)
        self.unk069 = readByte(f, unsigned)
        self.unk070 = readByte(f, unsigned)
        self.unk071 = readByte(f, unsigned)
        self.unk072 = readByte(f, unsigned)
        self.unk073 = readByte(f, unsigned)
        self.unk074 = readByte(f, unsigned)
        self.unk075 = readByte(f, unsigned)
        self.unk076 = readByte(f, unsigned)


class ndxr_entry_info_cmd:
    unk041 = 0
    unk042 = 0
    unk043 = 0
    unk044 = 0
    unk045 = 0
    table1_count = 0  # count
    unk046 = 0
    unk047 = 0
    unk048 = 0
    unk049 = 0
    unk050 = 0
    table1 = []
    unk051 = 0
    unk052 = 0
    unk053 = 0
    table2 = []

    def read_info_cmd(self, strings_addr=0, f=fopen()):
        self.unk041 = readByte(f, unsigned)
        self.unk042 = readShort(f, unsigned)
        self.unk043 = readByte(f, unsigned)
        self.unk044 = readShort(f, unsigned)
        self.unk045 = readLong(f, unsigned)
        self.table1_count = readShort(f, unsigned)
        self.unk046 = readShort(f, unsigned)
        self.unk047 = readLong(f, unsigned)
        self.unk048 = readLong(f, unsigned)
        self.unk049 = readByte(f, unsigned)
        self.unk050 = readShort(f, unsigned)
        if self.table1_count > 0:
            self.table1 = [ndxr_entry_info_cmd_table1] * self.table1_count
            for i in range(0, self.table1_count):
                self.table1[i] = ndxr_entry_info_cmd_table1()
                self.table1[i].read_info_cmd_table1(f)
                self.unk051 = readByte(f, unsigned)
                self.unk052 = readShort(f, unsigned)
                self.unk053 = readLong(f, unsigned)
                i = -1
                while True:
                    i += 1
                    append(self.table2, (ndxr_entry_info_cmd_table2()))
                    self.table2[i].read_info_cmd_table2(strings_addr, f)
                    if self.table2[i].unk081 != 0x20: break


class ndxr_entry_info:
    face_addr = 0  # face buffer addr?
    vert_addr = 0  # vert buffer addr?
    unk033 = 0  # 0
    vert_count = 0  # vertex count?
    unk036 = 0  # 6
    unk037 = 0  # ? vertex format? 17=28bytes, 16=20bytes
    cmd_addr = 0
    cmd = ndxr_entry_info_cmd()
    unk038 = 0  # 0
    unk039 = 0  # 0
    unk040 = 0  # 0
    face_count = 0  # face count?
    unk042 = 0  # 0
    unk043 = 0  # 0
    unk044 = 0  # 0
    unk045 = 0  # 0

    def read_info(self, pos=0, strings_addr=0, f=fopen(), addr_off = 0):
        self.face_addr = readLong(f, unsigned)
        self.vert_addr = readLong(f, unsigned)
        self.unk033 = readLong(f, unsigned)
        self.vert_count = readShort(f, unsigned)
        self.unk036 = readByte(f, unsigned)
        self.unk037 = readByte(f, unsigned)
        self.cmd_addr = readLong(f, unsigned) - addr_off
        self.unk038 = readLong(f, unsigned)
        self.unk039 = readLong(f, unsigned)
        self.unk040 = readLong(f, unsigned)
        self.face_count = readShort(f, unsigned)
        self.unk042 = readShort(f, unsigned)
        self.unk043 = readLong(f, unsigned)
        self.unk044 = readLong(f, unsigned)
        self.unk045 = readLong(f, unsigned)
        if self.cmd_addr > 0:
            fseek(f, pos + self.cmd_addr, seek_set)
            self.cmd.read_info_cmd(strings_addr, f)


class ndxr_entry:
    unk011 = 0.0
    unk012 = 0.0
    unk013 = 0.0
    unk014 = 0.0
    unk015 = 0.0
    unk016 = 0.0
    unk017 = 0.0
    unk018 = 0
    name_addr = 0
    name = ""
    unk019 = 0
    unk020 = 0
    unk021 = 0
    unk022 = 0  # info count
    info_addr = 0
    info = []

    def read_entry(self, pos=0, strings_addr=0, f=fopen(), addr_off = 0):
        self.unk011 = readFloat(f)
        self.unk012 = readFloat(f)
        self.unk013 = readFloat(f)
        self.unk014 = readFloat(f)
        self.unk015 = readFloat(f)
        self.unk016 = readFloat(f)
        self.unk017 = readFloat(f)
        self.unk018 = readLong(f, unsigned)
        self.name_addr = readLong(f, unsigned)
        self.unk019 = readShort(f, unsigned)
        self.unk020 = readShort(f, unsigned)
        self.unk021 = readShort(f, unsigned)
        self.unk022 = readShort(f, unsigned)
        self.info_addr = readLong(f, unsigned) - addr_off
        fseek(f, (strings_addr + self.name_addr), seek_set)
        self.name = readString(f)
        if self.unk022 > 0 and self.info_addr > 0:
            self.info = [ndxr_entry_info] * self.unk022
            for i in range(0, self.unk022):
                fseek(f, (pos + self.info_addr + (i * 48)), seek_set)
                self.info[i] = ndxr_entry_info()
                self.info[i].read_info(pos, strings_addr, f, addr_off)


class ndxr_file:
    fileid = 0
    unk001 = 0
    unk002 = 0
    count = 0
    unk007 = 0
    unk003 = 0
    face_addr = 0
    face_size = 0
    vert_size = 0
    unk004 = 0
    unk005 = 0
    unk006 = [0.0, 0.0, 0.0]
    entries = []

    def read(self, f=fopen(), mscale = 1.0, col_name = "", addr_off = 0):
        pos = ftell(f)
        header_size = 48
        self.fileid = readLong(f, unsigned)
        self.unk001 = readLong(f, unsigned)
        self.unk002 = readShort(f, unsigned)
        self.count = readShort(f, unsigned)
        self.unk007 = readShort(f, unsigned)
        self.unk003 = readShort(f, unsigned)
        self.face_addr = readLong(f, unsigned)
        self.face_size = readLong(f, unsigned)
        self.vert_size = readLong(f, unsigned)
        self.unk004 = readLong(f, unsigned)
        self.unk005 = readLong(f, unsigned)
        self.unk006 = [readFloat(f), readFloat(f), readFloat(f)]

        self.face_addr += pos + header_size
        vert_addr = self.face_addr + self.face_size
        strings_addr = vert_addr + self.vert_size
        entry_size = 48
        vertArray = []
        normArray = []
        faceArray = []
        matidArray = []
        tvertArray = []
        msh = None
        tmp = []
        vertex_stride = 0
        face = [0, 0, 0]
        facePosition = 0
        faceCW = True
        maxIndex = 0

        if self.count > 0:
            self.entries = [ndxr_entry] * self.count
            for i in range(0, self.count):
                fseek(f, (pos + header_size + (i * entry_size)), seek_set)
                self.entries[i] = ndxr_entry()
                self.entries[i].read_entry(pos, strings_addr, f, addr_off)
        
        
            
        
        # Generate Size List to Estimate the Vertex Stride
        for i in range(0, self.count):
            for ii in range(0, self.entries[i].unk022):
                appendIfUnique(tmp, (self.entries[i].info[ii].vert_addr + vert_addr))

        append(tmp, strings_addr)
        tmp.sort()
        
        for i in range(0, self.count):  # mesh entry
            vertArray = []
            tvertArray = []
            faceArray = []
            normArray = []
            matidArray = []
            facePosition = 0
            for ii in range(0, self.entries[i].unk022):  # level of detail meshes?

                # Read Faces
                fseek(f, (self.face_addr + self.entries[i].info[ii].face_addr), seek_set)
                v = 0
                
                while v < self.entries[i].info[ii].face_count:
                    faceCW = True
                    face[0] = readShort(f, unsigned)
                    face[1] = readShort(f, unsigned)
                    v += 2
                    while v < self.entries[i].info[ii].face_count:
                        face[2] = readShort(f, unsigned)
                        v += 1
                        if face[0] == 0xFFFF or face[1] == 0xFFFF or face[2] == 0xFFFF: break
                        if face[0] != face[1] and face[1] != face[2] and face[0] != face[2]:
                            if faceCW:
                                append(faceArray, [face[0] + facePosition, face[1] + facePosition, face[2] + facePosition])
                            else:
                                append(faceArray, [face[0] + facePosition, face[2] + facePosition, face[1] + facePosition])
                            append(matidArray, ii)
                        faceCW = not faceCW
                        face = [face[1], face[2], face[0]]
                        
                facePosition += self.entries[i].info[ii].vert_count
                vertex_stride = 20
                # Reading Vertices
                if self.entries[i].info[ii].vert_count != 0:
                    vertex_stride = int(
                        (tmp[(findItem(tmp, self.entries[i].info[ii].vert_addr + vert_addr)) + 1] -
                        (self.entries[i].info[ii].vert_addr + vert_addr)) / self.entries[i].info[ii].vert_count
                        )
                    vertex_stride = int(vertex_stride - (vertex_stride % 4))

                # format "Vertex Addr:\t%\n" (entries[i].info[ii].vert_addr + vert_addr)
                # format "Vertex Count:\t%\n" entries[i].info[ii].vert_count

                # format "Vertex Format:\t%\n" entries[i].info[ii].unk037
                if self.entries[i].info[ii].unk036 == 0:
                    vertex_stride = 20
                elif self.entries[i].info[ii].unk036 == 6:
                    vertex_stride = 28
                elif self.entries[i].info[ii].unk036 == 7:
                    vertex_stride = 44
                else:
                    print("Error:\tUnsupported Vertex Stride [%i]" % self.entries[i].info[ii].unk036)

                # format "Vertex Stride:\t%\n" vertex_stride
                # vertArray[entries[i].info[ii].vert_count] = [0.0, 0.0, 0.0]
                for v in range(0, self.entries[i].info[ii].vert_count):
                    fseek(f, (vert_addr + self.entries[i].info[ii].vert_addr + (v * vertex_stride)),
                          seek_set)
                    append(vertArray, [readFloat(f), readFloat(f), readFloat(f)])
                    if vertex_stride >= 28:
                        fseek(f, 8, seek_cur)  # append normArray ([readHalf f, readHalf f, readHalf f] * (readHalf f))
                        append(tvertArray, [readFloat(f), readFloat(f), 0.0])
                    else:
                        fseek(f, 4, seek_cur)  # readLong(f) # normal
                        append(tvertArray, [readHalf(f), readHalf(f), 0.0])
            
            mats = []
            mat = None
            for ii in range(0, self.entries[i].unk022):
                mat = StandardMaterial()
                mats.append(mat.data)
            
            msh = mesh(
                vertices=vertArray,
                faces=faceArray,
                tverts=[tvertArray],
                materialIDs=matidArray,
                materials=mats,
                obj_name=self.entries[i].name,
                flipAxis=True,
                lay_name=col_name,
                mscale=mscale
                )
        return None

class fhm_table_addr_entry:
    unk021 = 0
    addr = 0
    def read_addr_entry(self, f=fopen()):
        self.unk021 = readLong(f, unsigned)
        self.addr = readLong(f, unsigned)


class fhm_table_entry:
    unk031=0
    unk032 = 0
    unk033 = 0
    addr = 0
    size = 0
    def read_entry(self, f=fopen()):
        self.unk031 = readShort(f)
        self.unk032 = readShort(f)
        self.unk033 = readLong(f, unsigned)
        self.addr = readLong(f, unsigned)
        self.size = readLong(f, unsigned)


class fhm_file:
    fileid=0
    unk001 = 0
    unk002 = 0
    unk003 = 0
    unk004 = 0
    unk005 = 0
    unk006 = 0
    unk007 = 0
    unk008 = 0
    unk009 = 0
    unk010 = 0
    unk011 = 0
    file_count = 0
    file_addr_table =[]
    file_table =[]
    def read(self, f=fopen()):
        self.fileid = readLong(f, unsigned)
        if self.fileid != 0x004D4846:
            print("Error:\tInvalid File Type\n")
            return False
        
        self.unk001 = readLong(f, unsigned)
        self.unk002 = readLong(f, unsigned)
        self.unk003 = readLong(f, unsigned)
        self.unk004 = readLong(f, unsigned)
        self.unk005 = readLong(f, unsigned)
        self.unk006 = readLong(f, unsigned)
        self.unk007 = readLong(f, unsigned)
        self.unk008 = readLong(f, unsigned)
        self.unk009 = readLong(f, unsigned)
        self.unk010 = readLong(f, unsigned)
        self.unk011 = readLong(f, unsigned)
        self.file_count = readLong(f, unsigned)
        if self.file_count > 0:
            self.file_addr_table = [fhm_table_addr_entry] * self.file_count
            self.file_table = [fhm_table_entry] * self.file_count
            for i in range(0, self.file_count):
                self.file_addr_table[i] = fhm_table_addr_entry()
                self.file_addr_table[i].read_addr_entry(f)
    
            for i in range(0, self.file_count):
                fseek(f, (0x30 + self.file_addr_table[i].addr), seek_set)
                self.file_table[i] = fhm_table_entry()
                self.file_table[i].read_entry(f)
        return True

def dump_fhm(file=""):
    f = fopen(file, "rb")
    s = None

    fseek(f, 0x30, seek_set)
    count = readLong(f)

    fseek(f, (count * 8), seek_cur)

    pos = ftell(f)
    addr = 0
    size = 0
    type = ""
    for i in range(0, count):
        fseek(f, (pos + (i * 16)), seek_set)

    readLong(f)
    readLong(f)
    addr = readLong(f)
    size = readLong(f)

    fseek(f, (addr + 0x30), seek_set)
    type = "."
    for x in range(0, 4):
        type += chr(readByte(f))

    s = fopen((file + "_" + str(i) + type), "wb")

    fseek(f, (addr + 0x30), seek_set)
    for x in range(0, size):
        writeByte(s, (readByte(f)))

    fclose(s)
    fclose(f)

def read(file="", mscale = 1.0):
    fhm = fhm_file()
    type = 0
    ndxr = ndxr_file()
    fileID = 0
    
    f = fopen(file, "rb")
    if f.isGood:
        fname = getFilenameFile(file)
        fileID = readLong(f, unsigned)
        fseek(f, 0, seek_set)

        if fileID == 0x004D4846:  # FHM
            fhm.read(f)

            for i in range(0, len(fhm.file_table)):
                fseek(f, (fhm.file_table[i].addr + 0x30), seek_set)
                type = readLong(f, unsigned)
                fseek(f, (fhm.file_table[i].addr + 0x30), seek_set)
                if type == 0x5258444E:
                    ndxr = ndxr_file()
                    ndxr.read(f, mscale, fname + "_" + str(i + 1))
                else:
                    print("#%i\tUnknown Block:\t%i\t@ 0x%s\n" % (i, type, hex(fhm.file_table[i].addr + 0x30)))


        elif fileID == 0x5258444E:  # NDXR
            ndxr = ndxr_file()
            ndxr.read(f, mscale)
            
        elif fileID == 0x3350444E:  # NDP3 (Memory Dump)
            
            # a sample was provided from a memory dump
            # in which the addresses are assigned to memory
            # and are out of bounds of the supplied file sample
            # For this we need to try and derive the address
            # relative to the file and not the PS3 Memory block
            
            f.set_endian(False)
            fseek(f, 0x0A, seek_set)
            count = readShort(f)
            fseek(f, 0x5C, seek_set)
            addr_off = readLong(f) - (48 + (count * 0x30))
            print("addr_off:\t%i" % addr_off)
            fseek(f, 0, seek_set)
            
            
            ndxr = ndxr_file()
            ndxr.read(f, mscale, "", addr_off)
        else:
            print("Error:\tUnsupported File Type\n")

        fclose(f)

    else:
        print("Error:\tFailed to Read File\n")


# Callback when file(s) are selected
def acecombat_ah_imp_callback(fpath="", files=[], clearScene=True, mscale = 1.0):
    if len(files) > 0 and clearScene: deleteScene(['MESH', 'ARMATURE'])
    for file in files:
        read(fpath + file.name, mscale)
    if len(files) > 0:
        messageBox("Done!")
        return True
    else:
        return False


# Wrapper that Invokes FileSelector to open files from blender
def acecombat_ah_imp(reload=False):
    # Un-Register Operator
    if reload and hasattr(bpy.types, "IMPORTHELPER_OT_acecombat_ah_imp"):  # print(bpy.ops.importhelper.acecombat_ah_imp.idname())

        try:
            bpy.types.TOPBAR_MT_file_import.remove(
                bpy.types.Operator.bl_rna_get_subclass_py('IMPORTHELPER_OT_acecombat_ah_imp').menu_func_import)
        except:
            print("Failed to Unregister2")

        try:
            bpy.utils.unregister_class(bpy.types.Operator.bl_rna_get_subclass_py('IMPORTHELPER_OT_acecombat_ah_imp'))
        except:
            print("Failed to Unregister1")

    # Define Operator
    class ImportHelper_acecombat_ah_imp(bpy.types.Operator):

        # Operator Path
        bl_idname = "importhelper.acecombat_ah_imp"
        bl_label = "Select File"

        # Operator Properties
        # filter_glob: bpy.props.StringProperty(default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp', options={'HIDDEN'})
        filter_glob: bpy.props.StringProperty(default='*.fhm;*.ndxr;*.ndp3', options={'HIDDEN'}, subtype='FILE_PATH')

        # Variables
        filepath: bpy.props.StringProperty(subtype="FILE_PATH")  # full path of selected item (path+filename)
        filename: bpy.props.StringProperty(subtype="FILE_NAME")  # name of selected item
        directory: bpy.props.StringProperty(subtype="FILE_PATH")  # directory of the selected item
        files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)  # a collection containing all the selected items as filenames

        # Controls
        my_float1: bpy.props.FloatProperty(name="Scale", default=1.0, description="Changes Scale of the imported Mesh")
        my_bool1: bpy.props.BoolProperty(name="Clear Scene", default=True, description="Deletes everything in the scene prior to importing")

        # Runs when this class OPENS
        def invoke(self, context, event):

            # Retrieve Settings
            try: self.filepath = bpy.types.Scene.acecombat_ah_imp_filepath
            except: bpy.types.Scene.acecombat_ah_imp_filepath = bpy.props.StringProperty(subtype="FILE_PATH")

            try: self.directory = bpy.types.Scene.acecombat_ah_imp_directory
            except: bpy.types.Scene.acecombat_ah_imp_directory = bpy.props.StringProperty(subtype="FILE_PATH")

            try: self.my_float1 = bpy.types.Scene.acecombat_ah_imp_my_float1
            except: bpy.types.Scene.acecombat_ah_imp_my_float1 = bpy.props.FloatProperty(default=1.0)

            try: self.my_bool1 = bpy.types.Scene.acecombat_ah_imp_my_bool1
            except: bpy.types.Scene.acecombat_ah_imp_my_bool1 = bpy.props.BoolProperty(default=False)


            # Open File Browser
            # Set Properties of the File Browser
            context.window_manager.fileselect_add(self)
            context.area.tag_redraw()

            return {'RUNNING_MODAL'}

        # Runs when this Window is CANCELLED
        def cancel(self, context): print("run *SPAM*")

        # Runs when the class EXITS
        def execute(self, context):

            # Save Settings
            bpy.types.Scene.acecombat_ah_imp_filepath = self.filepath
            bpy.types.Scene.acecombat_ah_imp_directory = self.directory
            bpy.types.Scene.acecombat_ah_imp_my_float1 = self.my_float1
            bpy.types.Scene.acecombat_ah_imp_my_bool1 = self.my_bool1

            # Run Callback
            acecombat_ah_imp_callback(self.directory + "\\", self.files, self.my_bool1, self.my_float1)

            return {"FINISHED"}

            # Window Settings

        def draw(self, context):

            self.layout.row().label(text="Import Settings")

            self.layout.separator()
            self.layout.row().prop(self, "my_bool1")
            self.layout.row().prop(self, "my_float1")

            self.layout.separator()

            col = self.layout.row()
            col.alignment = 'RIGHT'
            col.label(text="  Author:", icon='QUESTION')
            col.alignment = 'LEFT'
            col.label(text="mariokart64n")

            col = self.layout.row()
            col.alignment = 'RIGHT'
            col.label(text="Release:", icon='GRIP')
            col.alignment = 'LEFT'
            col.label(text="March 23, 2021")

        def menu_func_import(self, context):
            self.layout.operator("importhelper.acecombat_ah_imp", text="Ace Combat Assault Horizon (*.fhm)")

    # Register Operator
    bpy.utils.register_class(ImportHelper_acecombat_ah_imp)
    bpy.types.TOPBAR_MT_file_import.append(ImportHelper_acecombat_ah_imp.menu_func_import)

    # Call ImportHelper
    bpy.ops.importhelper.acecombat_ah_imp('INVOKE_DEFAULT')



if not useOpenDialog:
    deleteScene(['MESH', 'ARMATURE'])  # Clear Scene
    clearListener()  # clears out console
    read(
        #"C:\\Users\\Corey\\Desktop\\AuditionOnlien\\nozomi\\model_id\\mech\\airp\\d_tnd4\\d_tnd4_pcom.fhm"
        #"C:\\Users\\Corey\\Desktop\\AuditionOnlien\\nozomi\\model_id\\mech\\airp\\d_tnd4\\d_tnd4_pcom\\d_tnd4_pcom.fhm_13.NDXR"
        "G:\\WA3_memory\\f16xl.ndp3"
        )
    messageBox("Done!")
else: acecombat_ah_imp(True)