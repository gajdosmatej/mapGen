class RiverVertex:
	'''
	Class representing river starts and ends.
	'''

	def __init__(self, is_start :bool = False):
		'''
		Constructor of RiverVertex class.
		@is_start (bool) ... Whether this RiverVertex represents river's source (used only for plotting).
		'''

		self.is_start = is_start
		self.end_side = None
		self.gui_ids = None
		self.start_point = None
		self.end_point = None


	def setCoords(self, tile):
		'''
		Sets coordinates of this river part boundary points for line plotting. Should be called after this object's @end_side is set.
		@tile (Tile) ... The tile in which this river is located.
		'''

		side_xs = {	"w": tile.x - 0.866*tile.side_length,
					"nw": tile.x - 0.5*0.866*tile.side_length,
					"ne": tile.x + 0.5*0.866*tile.side_length,
					"e": tile.x + 0.866*tile.side_length,
					"se": tile.x + 0.5*0.866*tile.side_length,
					"sw": tile.x - 0.5*0.866*tile.side_length}
		side_ys = {	"w": tile.y,
					"nw": tile.y - 0.75*tile.side_length,
					"ne": tile.y - 0.75*tile.side_length,
					"e": tile.y,
					"se": tile.y + 0.75*tile.side_length,
					"sw": tile.y + 0.75*tile.side_length}

		self.start_point = (tile.x, tile.y)
		self.end_point = (side_xs[self.end_side], side_ys[self.end_side])


class RiverSegment:
	'''
	Class representing river parts which are not its boundaries.
	'''

	def __init__(self):
		'''
		Constructor of RiverSegment class.
		'''

		self.start_side = None
		self.end_side = None
		self.gui_ids = None
		self.start_point = None
		self.end_point = None


	def setCoords(self, tile):
		'''
		Sets coordinates of this river part boundary points for line plotting. Should be called after this object's @start_side and @end_side is set.
		@tile (Tile) ... The tile in which this river is located.
		'''

		side_xs = {	"w": tile.x - 0.866*tile.side_length,
					"nw": tile.x - 0.5*0.866*tile.side_length,
					"ne": tile.x + 0.5*0.866*tile.side_length,
					"e": tile.x + 0.866*tile.side_length,
					"se": tile.x + 0.5*0.866*tile.side_length,
					"sw": tile.x - 0.5*0.866*tile.side_length}
		side_ys = {	"w": tile.y,
					"nw": tile.y - 0.75*tile.side_length,
					"ne": tile.y - 0.75*tile.side_length,
					"e": tile.y,
					"se": tile.y + 0.75*tile.side_length,
					"sw": tile.y + 0.75*tile.side_length}

		self.start_point = (side_xs[self.start_side], side_ys[self.start_side])
		self.mid_point = (tile.x, tile.y)
		self.end_point = (side_xs[self.end_side], side_ys[self.end_side])
