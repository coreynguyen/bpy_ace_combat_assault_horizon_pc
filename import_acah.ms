clearlistener()

if classof toUpper == UndefinedClass do (
	global toUpper
	fn toUpper instring = (
		local upper, lower, outstring
		upper="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		lower="abcdefghijklmnopqrstuvwxyz"
		outstring=copy instring
		for i=1 to outstring.count do (
			j=findString lower outstring[i]
			if (j != undefined) do outstring[i]=upper[j]
			)
		outstring
		)
	)
fn readHalf &f = (
	inputAsInt = readShort f #unsigned
	sign = (bit.and (bit.shift inputAsInt -15) 0x00000001)
	exponent = (bit.shift (bit.and inputAsInt 0x7C00) -10) as integer + 112
	fraction = (bit.and inputAsInt 0x03FF)
	bit.intasfloat ((bit.or (bit.or (bit.shift fraction 13) (bit.shift exponent 23)) (bit.shift sign 31)))
	)
struct ndxr_entry_info_cmd_table2 (
	unk081 = 0,
	name_addr = 0,
	name = "",
	unk083 = 0,
	unk084 = 0,
	unk085 = 0.0,
	unk086 = 0.0,
	unk087 = 0.0,
	unk088 = 0.0,
	fn read_info_cmd_table2 &strings_addr &f = (
		unk081 = readLong f #unsigned
		name_addr = readLong f #unsigned
		unk083 = readLong f #unsigned
		unk084 = readLong f #unsigned
		unk085 = readFloat f
		unk086 = readFloat f
		unk087 = readFloat f
		unk088 = readFloat f
		local pos = ftell f
		fseek f (strings_addr + name_addr) #seek_set
		name = readString f
		fseek f pos #seek_set
		--format "\t\tparam:\t%\n" name
		)
	)
struct ndxr_entry_info_cmd_table1 ( -- 24 bytes
	unk061 = 0,
	unk062 = 0,
	unk063 = 0,
	unk064 = 0,
	unk065 = 0,
	unk066 = 0,
	unk067 = 0,
	unk068 = 0,
	unk069 = 0,
	unk070 = 0,
	unk071 = 0,
	unk072 = 0,
	unk073 = 0,
	unk074 = 0,
	unk075 = 0,
	unk076 = 0,
	fn read_info_cmd_table1 &f = (
		unk061 = readByte f #unsigned
		unk062 = readShort f #unsigned
		unk063 = readLong f #unsigned
		unk064= readByte f #unsigned
		unk065 = readShort f #unsigned
		unk066 = readLong f #unsigned
		unk067 = readByte f #unsigned
		unk068 = readByte f #unsigned
		unk069 = readByte f #unsigned
		unk070 = readByte f #unsigned
		unk071 = readByte f #unsigned
		unk072 = readByte f #unsigned
		unk073 = readByte f #unsigned
		unk074 = readByte f #unsigned
		unk075 = readByte f #unsigned
		unk076 = readByte f #unsigned
		)
	)
struct ndxr_entry_info_cmd (
	unk041 = 0,
	unk042 = 0,
	unk043 = 0,
	unk044 = 0,
	unk045 = 0,
	table1_count = 0, -- count
	unk046 = 0,
	unk047 = 0,
	unk048 = 0,
	unk049 = 0,
	unk050 = 0,
	table1 = #(),
	unk051 = 0,
	unk052 = 0,
	unk053 = 0,
	table2 = #(),
	fn read_info_cmd &strings_addr &f = (
		local i = 1
		unk041 = readByte f #unsigned
		unk042 = readShort f #unsigned
		unk043 = readByte f #unsigned
		unk044 = readShort f #unsigned
		unk045 = readLong f #unsigned
		table1_count = readShort f #unsigned
		unk046 = readShort f #unsigned
		unk047 = readLong f #unsigned
		unk048 = readLong f #unsigned
		unk049 = readByte f #unsigned
		unk050 = readShort f #unsigned
		if table1_count > 0 do (
			table1[table1_count] = ndxr_entry_info_cmd_table1()
			for i = 1 to table1_count do (
				table1[i] = ndxr_entry_info_cmd_table1()
				table1[i].read_info_cmd_table1 &f
				)
			)
		unk051 = readByte f #unsigned
		unk052 = readShort f #unsigned
		unk053 = readLong f #unsigned
		i = 0
		do (
			i += 1
			append table2 (ndxr_entry_info_cmd_table2())
			table2[i].read_info_cmd_table2 strings_addr f
			) while table2[i].unk081 == 0x20
		)
	)
struct ndxr_entry_info (
	face_addr = 0, -- face buffer addr?
	vert_addr = 0, -- vert buffer addr?
	unk033 = 0, -- 0
	vert_count = 0, -- vertex count?
	unk036 = 0, -- 6
	unk037 = 0, -- ? vertex format? 17=28bytes, 16=20bytes
	cmd_addr = 0,
	cmd = ndxr_entry_info_cmd(),
	unk038 = 0, -- 0
	unk039 = 0, -- 0
	unk040 = 0, -- 0
	face_count = 0, -- face count?
	unk042 = 0, -- 0
	unk043 = 0, -- 0
	unk044 = 0, -- 0
	fn read_info &pos &strings_addr &f = (
		face_addr = readLong f #unsigned
		vert_addr = readLong f #unsigned
		unk033 = readLong f #unsigned
		vert_count = readShort f #unsigned
		unk036 = readByte f #unsigned
		unk037 = readByte f #unsigned
		cmd_addr = readLong f #unsigned
		unk038 = readLong f #unsigned
		unk039 = readLong f #unsigned
		unk040 = readLong f #unsigned
		face_count = readLong f #unsigned
		unk042 = readLong f #unsigned
		unk043 = readLong f #unsigned
		unk044 = readLong f #unsigned
		--format "Unk:\t%\t%\n" unk036 unk037
		if cmd_addr > 0 do (
			fseek f (pos + cmd_addr) #seek_set
			cmd.read_info_cmd strings_addr f 
			)
		)
	)
struct ndxr_entry (
	unk011 = 0.0,
	unk012 = 0.0,
	unk013 = 0.0,
	unk014 = 0.0,
	unk015 = 0.0,
	unk016 = 0.0,
	unk017 = 0.0,
	unk018 = 0,
	name_addr = 0,
	name = "",
	unk019 = 0,
	unk020 = 0,
	unk021 = 0,
	unk022 = 0,	-- info count
	info_addr = 0,
	info = #(),
	fn read_entry &pos &strings_addr &f = (
		local i = 1
		unk011 = readFloat f
		unk012 = readFloat f
		unk013 = readFloat f
		unk014 = readFloat f
		unk015 = readFloat f
		unk016 = readFloat f
		unk017 = readFloat f
		unk018 = readLong f #unsigned
		name_addr = readLong f #unsigned
		unk019 = readShort f #unsigned
		unk020 = readShort f #unsigned
		unk021 = readShort f #unsigned
		unk022 = readShort f #unsigned
		info_addr = readLong f #unsigned
		fseek f (strings_addr + name_addr) #seek_set
		name = readString f
		--format "\tName:\t%\n" name
		if unk022 > 0 and info_addr > 0 do (
			info[unk022] = ndxr_entry_info()
			for i = 1 to unk022 do (
				fseek f (pos + info_addr + ((i - 1) * 48)) #seek_set
				info[i] = ndxr_entry_info()
				info[i].read_info pos strings_addr  f
				)
			)
		)
	)
struct ndxr_file (
	fileid = 0,
	unk001 = 0,
	unk002 = 0,
	count = 0,
	unk007 = 0,
	unk003 = 0,
	face_addr = 0,
	face_size = 0,
	vert_size = 0,
	unk004 = 0,
	unk005 = 0,
	unk006 = [0.0, 0.0, 0.0],
	entries = #(),
	fn read &f = (
		local pos = ftell f
		local header_size = 48
		fileid = readLong f #unsigned
		unk001 = readLong f #unsigned
		unk002 = readShort f #unsigned
		count = readShort f #unsigned
		unk003 = readShort f #unsigned
		unk007 = readShort f #unsigned
		face_addr = readLong f #unsigned
		face_size = readLong f #unsigned
		vert_size = readLong f #unsigned
		unk004 = readLong f #unsigned
		unk005 = readLong f #unsigned
		unk006 = [readFloat f, readFloat f, readFloat f]
		
		face_addr += pos + header_size
		local vert_addr = face_addr + face_size
		local strings_addr = vert_addr + vert_size
		local entry_size = 48
		local i = 1
		local ii = 1
		local vertArray = #()
		local normArray = #()
		local faceArray = #()
		local matidArray = #()
		local tvertArray = #()
		local msh = undefined
		local v = 1
		local tmp = #()
		local vertex_stride = 0
		local face = [1, 1, 1]
		local facePosition = 1
		local faceCW = true
		local maxIndex = 0
		
		
		if count > 0 do (
			entries[count] = ndxr_entry()
			for i = 1 to count do (
				fseek f (pos + header_size + ((i - 1) * entry_size)) #seek_set
				--format "Entry[%]:\t0x%\n" i (bit.IntAsHex((ftell f) as integer))
				entries[i] = ndxr_entry()
				entries[i].read_entry pos strings_addr f
				)
			)
		
		-- Generate Size List to Estimate the Vertex Stride
		
		for i = 1 to count do (
			for ii = 1 to entries[i].unk022 do (
				append tmp (entries[i].info[ii].vert_addr + vert_addr)
				)
			)
		--format "strings addr:\t%\n" strings_addr
		append tmp strings_addr
		sort tmp
		
		
		for i = 1 to count do (	-- mesh entry
			vertArray = #()
			tvertArray = #()
			faceArray = #()
			normArray = #()
			matidArray = #()
			facePosition = 1
			for ii = 1 to entries[i].unk022 do ( -- level of detail meshes?
				
				
				-- Read Faces
				fseek f (face_addr + entries[i].info[ii].face_addr) #seek_set
				v = 0
				maxIndex = 0
				while v < entries[i].info[ii].face_count do (
					faceCW = true
					face[1] = readShort f #unsigned
					face[2] = readShort f #unsigned
					v += 2
					while v < entries[i].info[ii].face_count do (
						face[3] = readShort f #unsigned
						if face[3] == 0xFFFF or face[3] == -1 do exit
						if face[1] != face[2] and face[2] != face[3] and face[1] != face[3] do (
							if faceCW then (
								append faceArray (face + facePosition)
								)
							else (
								append faceArray ([face[1], face[3], face[2]] + facePosition)
								)
							append matidArray ii
							if face[1] > maxIndex do maxIndex = face[1]
							if face[2] > maxIndex do maxIndex = face[2]
							if face[3] > maxIndex do maxIndex = face[3]
							)
						faceCW = not faceCW
						face = [face[2], face[3], face[1]]
						v += 1
						)
					)
				facePosition += entries[i].info[ii].vert_count
				
				-- Reading Vertices
				vertex_stride = (tmp[(findItem tmp (entries[i].info[ii].vert_addr + vert_addr)) + 1] - (entries[i].info[ii].vert_addr + vert_addr)) / entries[i].info[ii].vert_count
				vertex_stride = (vertex_stride - (mod vertex_stride 4)) as integer
				--format "Vertex Stride EST:\t%\n" vertex_stride
				--format "Vertex Addr:\t%\n" (entries[i].info[ii].vert_addr + vert_addr)
				--format "Vertex Count:\t%\n" entries[i].info[ii].vert_count
				
				--format "Vertex Format:\t%\n" entries[i].info[ii].unk036
				case entries[i].info[ii].unk036 of (
					0: (vertex_stride = 20)
					6: (vertex_stride = 28)
					7: (vertex_stride = 44)
					default: (format "Error:\tUnsupported Vertex Stride")
					)
				--format "Vertex Stride:\t%\n" vertex_stride
				--vertArray[entries[i].info[ii].vert_count] = [0.0, 0.0, 0.0]
				for v = 1 to entries[i].info[ii].vert_count do (
					fseek f (vert_addr + entries[i].info[ii].vert_addr + ((v - 1) * vertex_stride)) #seek_set
					append vertArray [readFloat f, readFloat f, readFloat f]
					if vertex_stride >= 28 then (
						fseek f 8 #seek_cur--append normArray ([readHalf f, readHalf f, readHalf f] * (readHalf f))
						append tvertArray [readFloat f, readFloat f, 0.0]
						)
					else (
						fseek f 4 #seek_cur--readlong f -- normal
						append tvertArray [readHalf f, readHalf f, 0.0]
						)
					
					)
				
				
				)
			--format "verts:\t%\n" vertArray.count
			msh = mesh vertices:vertArray tverts:tvertArray faces:faceArray materialIDs:matidArray
			msh.name = entries[i].name
			msh.numTVerts = tvertArray.count
			msh.backfacecull = on
			msh.displayByLayer = false
			msh.wirecolor = random (color 0 0 0) (color 255 255 255)
			buildTVFaces msh
			for v = 1 to faceArray.count do setTVFace msh v faceArray[v]
			for v = 1 to tvertArray.count do setTVert msh v tvertArray[v]
			
			)
		
		
		
		
		
		)
	)
struct fhm_table_addr_entry (
	unk021 = 0,
	addr = 0,
	fn read_addr_entry &f = (
		unk021 = readLong f #unsigned
		addr = readLong f #unsigned
		)
	)
struct fhm_table_entry (
	unk031 = 0,
	unk032 = 0,
	unk033 = 0,
	addr = 0,
	size = 0,
	fn read_entry &f = (
		unk031 = readShort f
		unk032 = readShort f
		unk033 = readLong f #unsigned
		addr = readLong f #unsigned
		size = readLong f #unsigned
		)
	)
struct fhm_file (
	fileid = 0,
	unk001 = 0,
	unk002 = 0,
	unk003 = 0,
	unk004 = 0,
	unk005 = 0,
	unk006 = 0,
	unk007 = 0,
	unk008 = 0,
	unk009 = 0,
	unk010 = 0,
	unk011 = 0,
	file_count = 0,
	file_addr_table = #(),
	file_table = #(),
	fn read &f = (
		fileid = readLong f #unsigned
		if fileid != 0x004D4846 do (
			format "Error:\tInvalid File Type\n"
			continue
			)
		unk001 = readLong f #unsigned
		unk002 = readLong f #unsigned
		unk003 = readLong f #unsigned
		unk004 = readLong f #unsigned
		unk005 = readLong f #unsigned
		unk006 = readLong f #unsigned
		unk007 = readLong f #unsigned
		unk008 = readLong f #unsigned
		unk009 = readLong f #unsigned
		unk010 = readLong f #unsigned
		unk011 = readLong f #unsigned
		file_count = readLong f #unsigned
		if file_count > 0 do (
			local i = 1
			file_addr_table[file_count] = fhm_table_addr_entry()
			file_table[file_count] = fhm_table_entry()
			for i = 1 to file_count do (
				file_addr_table[i] = fhm_table_addr_entry()
				file_addr_table[i].read_addr_entry(f)
				)
			for i = 1 to file_count do (
				fseek f (0x30 + file_addr_table[i].addr) #seek_set
				file_table[i] = fhm_table_entry()
				file_table[i].read_entry(f)
				)
			)
		)
	)
fn dump_fhm file = (
	
	local f = try(fopen file "rb")catch(undefined)
	
	if f != undefined then (
		local s = undefined
		local i = 1
		
		fseek f 0x30 #seek_set
		local count = readLong f
		
		fseek f (count * 8) #seek_cur
		
		local pos = ftell f
		local addr = 0
		local size = 0
		local x= 1
		local type = ""
		for i = 1 to count do (
			fseek f (pos + ((i - 1) * 16)) #seek_set
			
			
			readLong f
			readLong f
			addr = readLong f
			size = readLong f
			
			fseek f (addr + 0x30) #seek_set
			type = "."
			for x = 1 to 4 do (
				type += bit.IntAsChar(readbyte f)
				)
			s = fopen (file + "_" + (i as string) + type) "wb"
			
			fseek f (addr + 0x30) #seek_set
			for x = 1 to size do (
				writebyte s (readbyte f)
				
				)
			
			
			fclose s
			)
		fclose f

		) else (messagebox "No File?")
	)
fn read file = (
	local f = undefined
	local fhm = fhm_file()
	local i = 1
	local type = 0
	local ndxr = ndxr_file()
	local fileID = 0

	f = try(fopen file "rb") catch(undefined)
	if f != undefined then (
		
		fileID = readLong f #unsigned
		fseek f 0 #seek_set
		
		if fileID == 0x004D4846 then (	-- FHM
			fhm.read(f)
			
			for i = 1 to fhm.file_table.count do (
				fseek f (fhm.file_table[i].addr + 0x30) #seek_set
				type = readLong f #unsigned
				fseek f (fhm.file_table[i].addr + 0x30) #seek_set
				case type of (
					0x5258444E: (	-- NDXR
						format "#%\t%\t@ 0x%\n" \
							i "NDXR" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						ndxr = ndxr_file()
						ndxr.read(f)
						)
					0x32504F4D: (	-- MOP2
						format "#%\t%\t@ 0x%\n" \
							i "MOP2" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					0x484C4F43: (	-- COLH
						format "#%\t%\t@ 0x%\n" \
							i "COLH" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					0x4554414D: (	-- MATE
						format "#%\t%\t@ 0x%\n" \
							i "MATE" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					0x00544E4D: (	-- MNT
						format "#%\t%\t@ 0x%\n" \
							i "MNT" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					0x41535754: (	-- TWSA
						format "#%\t%\t@ 0x%\n" \
							i "TWSA" (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					default: (
						format "#%\tUnknown Block:\t%\t@ 0x%\n" \
							i type (bit.IntAsHex((fhm.file_table[i].addr + 0x30) as integer))
						)
					)
				)
			)
		else if fileID == 0x5258444E then (	-- NDXR
			ndxr = ndxr_file()
			ndxr.read(f)
			)
		else (format "Error:\tUnsupported File Type\n")
		
		fclose f
		)
	else (format "Error:\tFailed to Read File\n")
	)
delete $*

read (
	"C:\\Users\\Corey\\Desktop\\AuditionOnlien\\nozomi\\model_id\\mech\\airp\\d_tnd4\\d_tnd4_pcom.fhm"
-- 	"C:\\Users\\Corey\\Desktop\\AuditionOnlien\\nozomi\\model_id\\mech\\airp\\d_tnd4\\d_tnd4_pcom\\d_tnd4_pcom.fhm_13.NDXR"
	GetOpenFileName types:"ace combat 7 model (*.fhm)|*.fhm;*.ndxr|All files (*.*)|*.*|"
	)
/*
dump_fhm(GetOpenFileName types:"ace combat 7 model (*.fhm)|*.fhm;*.ndxr|All files (*.*)|*.*|")
*/