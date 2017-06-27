=============
esri_metadata
=============

An object oriented metadata editor on top of the ESRI related xml metadata format.

Requires `arcpy` if metadata is to be edited on a spatial layer.

Examples::

	md=Metadata('path/to/metadata.xml')
	or
	md=Metadata('path/to/connection.sde/featureClass')

	print(md.dataIdInfo.idCitation.resTitle.value)
	print(md.dataIdInfo.idAbs.value)

	if not md.mdConst[0].SecConsts.is_missing:
		print(md.mdConst[0].SecConsts.useLimit.value)
		print(type(md.mdConst[0].SecConsts))

	md.dataIdInfo.idCitation.resTitle.value='test'
	md.mdConst.append()
	md.mdConst[-1].SecConsts.userNote.value='All ancestor elements will be created'
	md.mdConst.append(md.dataIdInfo.resConst[2])

	del md.dqInfo
	del md.mdConst[1]
