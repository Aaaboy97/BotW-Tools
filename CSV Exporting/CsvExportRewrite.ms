-- Aaaboy97 2018


buttonIds = #()
fn main = (
	try (
		local saveFileName = getSaveFileName initialDir:"$export" filename:"dope.csv"
		local saveFile = createFile saveFileName

		local data = #()

		clearlistener()
		for poly in geometry do (
			if classOf poly != BoneGeometry do (
				local snap = snapshotAsMesh poly
				select poly

				local polyData = #()
				append polyData poly.Name

				local copyUVs
				local expNorms
				for i in buttonIds do (
					if i[1] == poly do (
						local id = i[2]
						copyUVs = (execute ("CSVExport.chk" + (id as string) + ".state"))
						expNorms = (execute ("CSVExport.rdo" + (id as string) + ".state"))
						if expNorms == 1 then (
							expNorms = true
						) else (
							expNorms = false
						)
						exit
					)
				)
				print ("Beginning reading " + poly.Name)

				-- check if the poly has a skin with weighted bones
				local hasBones = False
				local skinMod = poly.Modifiers[#Skin]
				if skinMod != Undefined do (
					if skinOps.getNumberBones skinMod > 0 do (
						hasBones = True
					)
				)
				append polyData hasBones

				-- check if the poly has mapped colors
				local hasColors = False
				if meshOp.getMapSupport snap 0 do (
					if getNumVerts poly <= meshOp.getNumMapVerts snap 0 do (
						hasColors = True
					)
				)
				append polyData hasColors

				-- check number of UV maps
				local numMaps = 1
				for i = 2 to 4 do (
					if meshOp.getMapSupport snap i do (
						numMaps = i
					)
				)
				if copyUVs and (numMaps < 2) do (
					numMaps = 2
				)
				append polyData numMaps

				-- read all the vertex and face data
				local vertArr = #()
				local faceArr = #()

				if expNorms do (
					local editNorm = EditNormals()
					addModifier poly editNorm
				)

				-- not iterating to getFaceCount because the value is occasionally misreported
				local i = 0
				while True do (
					i += 1
					local faceArr1 = #()
					local faceMesh
					local faceMaps = #()
					try (
						faceMesh = getFace snap i
						for j = 1 to numMaps do (
							if j == 2 and copyUVs then (
								append faceMaps (meshOp.getMapFace snap 1 i)
							) else (
								append faceMaps (meshOp.getMapFace snap j i)
							)
						)
					) catch (
						print ("Finished reading " + poly.Name)
						exit
					)

					local vertsMesh = #(faceMesh.x, faceMesh.y, faceMesh.z)
					local vertsMaps = #()
					for faceMap in faceMaps do (
						append vertsMaps #(faceMap.x, faceMap.y, faceMap.z)
					)

					local faceColor
					local vertsColor
					if hasColors do (
						faceColor = getVCFace snap i
						vertsColor = #(faceColor.x, faceColor.y, faceColor.z)
					)

					for j = 1 to 3 do (
						local vMesh = vertsMesh[j]
						local vMaps = #()
						for vertsMap in vertsMaps do (
							append vMaps vertsMap[j]
						)
						local vertArr1 = vertArr[vMesh]
						local makeVert = True
						if vertArr1 != Undefined then (
							for k = 1 to vertArr1.count do (
								local allMatch = True
								for l = 1 to numMaps do (
									local vertUVW
									try (
										if l == 2 and copyUVs then (
											vertUVW = meshOp.getMapVert snap 1 vMaps[1]
										) else (
											vertUVW = meshOp.getMapVert snap l vMaps[l]
										)
									) catch (
										vertUVW = point3 0 0 0
									)
									vertUVW.z = 0
									local compare = vertArr1[k][3 + l]
									compare = point3 compare[1] compare[2] 0
									if length (vertUVW - compare) != 0 do (
										allMatch = False
										exit
									)
								)
								if allMatch do (
									makeVert = False
									append faceArr1 #(vMesh, k)
									exit
								)
							)
						) else (
							vertArr1 = #()
						)

						if makeVert do (
							local vertArr2 = #()
							local vert = getVert snap vMesh
							append vertArr2 #(vert.x, vert.y, vert.z)

							local norm
							if expNorms then (
								-- read explicit normals from Edit_Normals modifier
								-- instead of using `getNormal snap vMesh`, which recalculates normals
								local normIds = #{}
								editNorm.ConvertVertexSelection #{vMesh} &normIds
								norm = editNorm.GetNormal (normIds as array)[1]
							) else (
								norm = getNormal snap vMesh
							)
							append vertArr2 #(norm.x, norm.y, norm.z)

							local col
							if hasColors then (
								col = meshOp.getMapVert snap 0 vertsColor[j]
								col = #(ceil(col.x*127), ceil(col.y*127), ceil(col.z*127), 127)
							) else (
								col = #(127, 127, 127, 127)
							)
							append vertArr2 col

							for k = 1 to numMaps do (
								if k == 2 and copyUVs then (
									try (
										local vertUVW = meshOp.getMapVert snap 1 vMaps[1]
										append vertArr2 #(vertUVW.x, vertUVW.y)
									) catch (
										append vertArr2 #(0, 0)
									)
								) else (
									try (
										local vertUVW = meshOp.getMapVert snap k vMaps[k]
										append vertArr2 #(vertUVW.x, vertUVW.y)
									) catch (
										append vertArr2 #(0, 0)
									)
								)
							)

							append vertArr1 vertArr2
							append faceArr1 #(vMesh, vertArr1.count)
							vertArr[vMesh] = vertArr1
						)
					)
					append faceArr faceArr1
				)

				if expNorms do(
					deleteModifier poly editNorm
				)

				-- reorder data to match previous CSV file format
				-- also clone vertices that have multiple UV mapped coordinates
				local newVertArr = #()
				local indexArr = #()
				for i = 1 to vertArr.count do (
					local vert = vertArr[i]
					if vert != Undefined do (
						for j = 1 to vert.count do (
							append newVertArr vert[j]
							local index = indexArr[i]
							if index == Undefined then (
								indexArr[i] = #()
								indexArr[i][j] = newVertArr.count
							) else (
								indexArr[i][j] = newVertArr.count
							)
						)
					)
				)
				-- correct faces to point towards cloned vertices
				for i = 1 to faceArr.count do (
					for j = 1 to 3 do (
						faceArr[i][j] = indexArr[faceArr[i][j][1]][faceArr[i][j][2]]
					)
				)

				append polyData newVertArr
				append polyData faceArr

				if hasBones do (
					local boneArr = #()

					for i = 1 to indexArr.count do (
						if indexArr[i] != Undefined do (
							local vertBoneCount = skinOps.GetVertexWeightCount skinMod i
							local boneArr1 = #()
							for j = 1 to vertBoneCount do (
								local boneId = skinOps.GetVertexWeightBoneId skinMod i j
								local boneName = skinOps.GetBoneName skinMod boneId 0
								local boneWeight = skinOps.GetVertexWeight skinMod i j
								append boneArr1 #(boneName, boneWeight)
							)
							-- copy weights multiple times if vertex has been cloned
							for j = 1 to indexArr[i].count do (
								append boneArr boneArr1
							)
						)
					)

					append polyData boneArr
				)

				delete snap
				append data polyData
			)
		)

		print "Beginning to write to CSV..."
		-- write to CSV file
		for poly in data do (
			print ("Writing " + poly[1])
			format "Obj Name:%\n" poly[1] to:saveFile
			-- "Support" is misspelled here to maintain compatibility with previous CSV files
			if poly[2] do (
				format "Bone_Suport\n" to:saveFile
			)
			if poly[3] do (
				format "Color_Suport\n" to:saveFile
			)
			format "UV_Num:%\n" poly[4] to:saveFile
			format "vert_Array\n" to:saveFile
			for vert in poly[5] do (
				for elem in vert do (
					for i = 1 to elem.count do (
						if i < elem.count then (
							format "%," elem[i] to:saveFile
						) else (
							format "%" elem[i] to:saveFile
						)
					)
					format "\n" to:saveFile
				)
			)
			format "face_Array\n" to:saveFile
			for face in poly[6] do (
				format "%, %, %\n" face[1] face[2] face[3] to:saveFile
			)
			if poly[2] do (
				format "bone_Array\n" to:saveFile
				for boneArr in poly[7] do (
					for boneWeight in boneArr do (
						format "%, %," boneWeight[1] boneWeight[2] to:saveFile
					)
					format "\n" to:saveFile
				)
			)
		)

		try (
			destroyDialog CSVExport
		) catch ()
		try (
			close saveFile
		) catch ()
		print "Succesfully completed!"
	) catch (
		try (
			destroyDialog CSVExport
		) catch ()
		try (
			close saveFile
		) catch ()
		throw()
	)
)

command = "rollout CSVExport \"CSV Exporter\" (\n"
command += "label name \"Model Name\" align:#left across:3\n"
command += "label uvs \"Copy UVs\" align:#right\n"
command += "label nrms \"Explicit Normals\" align:#right\n"
i = 0
for poly in geometry do (
	if classOf poly != BoneGeometry do (
		i += 1
		local j = i as string
		command += "label lbl" + j + " \"" + poly.Name + "\" align:#left across:3\n"
		command += "checkbox chk" + j + " align:#right\n"
		command += "radiobuttons rdo" + j + " labels:#(\"Yes\",\"No\") align:#right\n"
		append buttonIds #(poly, i)
	)
)
command += "button exportBtn \"Export\" align:#right\n"
command += "on exportBtn pressed do (main())"
command += ")"
execute command
clearListener()
createDialog CSVExport width:600
