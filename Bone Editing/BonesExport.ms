-- Aaaboy97 2018


saveFileName = getSaveFileName initialDir:"$export" filename:"bones.csv"
saveFile = createFile saveFileName

no_bones = true
fn handle n =
(
	if no_bones then
	(
		no_bones = false
		format "Bones Geometry\n" to:saveFile
	)
	trf = n.transform
	p = n.parent
	if p != undefined then
	(
		n.transform *= (inverse p.transform)
	)
	s = n.scale
	r = (inverse n.rotation) as eulerangles
	r = quat (r.x*pi/180) (r.y*pi/180) (r.z*pi/180) 1.0
	t = n.position
	format "%\n%,%,%\n%,%,%,%\n%,%,%\n" n.name s.x s.y s.z r.x r.y r.z r.w t.x t.y t.z to:saveFile
	n.transform = trf
)

for h in helpers do
(
	handle(h)
)

for b in geometry do
(
	if classOf b == boneGeometry then
	(
		handle(b)
	)
)

close saveFile
