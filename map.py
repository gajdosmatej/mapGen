from collections import deque
import numpy

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
		self.gui_id = None
		self.start_point = None
		self.end_point = None

	def setCoords(self, tile):
		'''
		Sets coordinates of this river part boundary points for line plotting.
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
		self.gui_id = None
		self.start_point = None
		self.end_point = None


	def setCoords(self, tile):
		'''
		Sets coordinates of this river part points for line plotting.
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

class Tile:
	'''
	Class representing map tiles.
	'''
	
	#length of tile side for plotting
	side_length = 20

	def __init__(self, iterator_state :bool = False):
		'''
		Constructor of Tile class.
		@iterator_state (bool) ... Internal variable used for consistency when looping over map.
		'''

		#neighbour compass directions
		self.neighbours = {	"w": None,
							"nw": None,
							"ne": None,
							"e": None,
							"se": None,
							"sw": None}

		#tile biome parameters
		self.altitude = None
		self.is_lake = False
		self.rivers = []

		#centre coordinates
		self.x = None
		self.y = None

		#fill colour of the tile
		self.colour = "#FFFFFF"

		#tkinter-canvas hexagon object
		self.gui_id = None

		#noting which tiles were already visited by iterator
		self.iterator_state = iterator_state

		#is plotted on canvas
		self.gui_active = False

		#was ever plotted
		self.was_plotted = False


	def getExistingNeighbours(self) -> dict:
		'''
		Returns dictionary of neighbouring tiles which are not None.
		'''

		return {key: value for key, value in self.neighbours.items() if value != None}


	def setAltitude(self):

		#self.altitude = numpy.random.uniform(-1,1)
		self.altitude = 1
		if numpy.random.random() > 0.5:	self.altitude = -self.altitude

	def activate(self):
		self.gui_active = True

	def deactivate(self):
		self.gui_active = False

	def isRiverStart(self):
		k = 0.1
		if numpy.random.random() < k*self.altitude:	return True
		return False

class Map:
	def __init__(self, centre_x :int, centre_y :int):
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y
		self.centre_tile.setAltitude()
		self.boundary_tiles = {"left": [self.centre_tile], "up": [self.centre_tile], "right": [self.centre_tile], "down": [self.centre_tile]}


	def tileIterator(self, active_only = False):	#active_only ... those that are rendered
		queue = deque()
		def conditionFunc(tile):	return (not active_only) or tile.gui_active
		queue.append(self.centre_tile)
		old_state = self.centre_tile.iterator_state
		new_state = not old_state
		self.centre_tile.iterator_state = new_state

		while queue:
			tile = queue.popleft()
			not_visited_tiles = []
			if tile.neighbours["w"] and tile.neighbours["w"].iterator_state == old_state and conditionFunc(tile.neighbours["w"]):	not_visited_tiles.append(tile.neighbours["w"])
			if tile.neighbours["nw"] and tile.neighbours["nw"].iterator_state == old_state and conditionFunc(tile.neighbours["nw"]):	not_visited_tiles.append(tile.neighbours["nw"])
			if tile.neighbours["ne"] and tile.neighbours["ne"].iterator_state == old_state and conditionFunc(tile.neighbours["ne"]):	not_visited_tiles.append(tile.neighbours["ne"])
			if tile.neighbours["e"] and tile.neighbours["e"].iterator_state == old_state and conditionFunc(tile.neighbours["e"]):	not_visited_tiles.append(tile.neighbours["e"])
			if tile.neighbours["se"] and tile.neighbours["se"].iterator_state == old_state and conditionFunc(tile.neighbours["se"]):	not_visited_tiles.append(tile.neighbours["se"])
			if tile.neighbours["sw"] and tile.neighbours["sw"].iterator_state == old_state and conditionFunc(tile.neighbours["sw"]):	not_visited_tiles.append(tile.neighbours["sw"])
			for new_tile in not_visited_tiles:
				new_tile.iterator_state = new_state
				queue.append(new_tile)
			yield tile


	def updateCentreTile(self, centre_x :float, centre_y :float):
		'''
		Checks, whether there is a tile that is closer to the canvas centre than the current centre_tile. If there is that tile, it becomes new centre_tile.
		@centre_x ... Canvas' centre x position.
		@centre_y ... Canvas' centre y position.
		'''
		#squared standard euclidean distance from the canvas' centre
		def squareDistCentre(tile):	return (tile.x - centre_x)**2 + (tile.y - centre_y)**2
		curr_dist = squareDistCentre(self.centre_tile)
		
		#go through the current centre_tile's neighbours, if a neighbour is closer to the canvas centre, make it the new centre_tile
		for key in self.centre_tile.getExistingNeighbours():
			neighbour = self.centre_tile.neighbours[key]
			if squareDistCentre(neighbour) < curr_dist:	
				self.centre_tile = neighbour
				curr_dist = squareDistCentre(neighbour)


	def updateSandpiles(self, tiles :list[Tile]):
		'''
		Make the altitudes of @tiles more smooth by averaging tile altitude with its neighbours' altitudes.
		@tiles ... List of tiles, which altitudes are being updated. 
		'''
		alpha = 20
		beta=0.01
		for i in range(5):
			for tile in tiles:
				neighbours = tile.getExistingNeighbours()
				if neighbours != {}:
					average_neighbouring_altitude = sum(neighbours[key].altitude for key in neighbours) / len(neighbours)
					tile.altitude = (tile.altitude + alpha*average_neighbouring_altitude) / (1+alpha)
					rand_shift = tile.altitude + beta*numpy.random.uniform(-1,1)
					if -1 < rand_shift < 1:	tile.altitude = rand_shift


	def makeRivers(self, river_tiles):
		def indexToSide(index):
			sides = ["w", "nw", "ne", "e", "se", "sw"]
			return sides[index]
		def sideToIndex(side):
			indices = {"w": 0, "nw": 1, "ne": 2, "e": 3, "se": 4, "sw": 5}
			return indices[side]
		
		opposing_sides = {"w": "e", "nw": "se", "ne": "sw", "e": "w", "se": "nw", "sw": "ne"}
		
		while river_tiles != []:
			river_tile, river = river_tiles.pop()

			possible_directions = [key for key in river_tile.neighbours	if river_tile.neighbours[key] != None
														and not river_tile.neighbours[key].was_plotted
														and river_tile.altitude >= river_tile.neighbours[key].altitude]
			
			if possible_directions == []:
				river.end_side = indexToSide(numpy.random.randint(0,6))
				river.setCoords(river_tile)
				river_tile.is_lake = True
				continue
			else:
				direction = numpy.random.choice(possible_directions)
						
			new_river_tile = river_tile.neighbours[direction]
			river.end_side = direction
			river.setCoords(river_tile)

			if new_river_tile.altitude >= 0:
				if new_river_tile.rivers != [] or numpy.random.random() < 0:	#stop
					new_river = RiverVertex(False)
					new_river_tile.rivers.append(new_river)
					new_river.end_side = opposing_sides[direction]
					new_river.setCoords(new_river_tile)
				else:
					new_river = RiverSegment()
					new_river_tile.rivers.append(new_river)
					new_river.start_side = opposing_sides[direction]
					river_tiles.append( (new_river_tile, new_river) )



	def generateGraph(self, gui):

		river_tiles = []

		tile = self.boundary_tiles["left"][len(self.boundary_tiles["left"])//2]
		while gui.isTileOnScreen(tile):
			self.generateLeftSide(gui)
			tile = self.boundary_tiles["left"][len(self.boundary_tiles["left"])//2]
		
		tile = self.boundary_tiles["up"][len(self.boundary_tiles["up"])//2]
		while gui.isTileOnScreen(tile):
			self.generateUpSide(gui)
			tile = self.boundary_tiles["up"][len(self.boundary_tiles["up"])//2]

		tile = self.boundary_tiles["right"][len(self.boundary_tiles["right"])//2]
		while gui.isTileOnScreen(tile):
			self.generateRightSide(gui)
			tile = self.boundary_tiles["right"][len(self.boundary_tiles["right"])//2]

		tile = self.boundary_tiles["down"][len(self.boundary_tiles["down"])//2]
		while gui.isTileOnScreen(tile):
			self.generateDownSide(gui)
			tile = self.boundary_tiles["down"][len(self.boundary_tiles["down"])//2]
		
		self.updateSandpiles( list(self.tileIterator()) )
		
		for tile in self.tileIterator():
			if tile.isRiverStart():
				river = RiverVertex(True)
				tile.rivers.append(river)
				river_tiles.append( (tile, river) )
		self.makeRivers(river_tiles)


	def generateLeftSide(self, gui):
		new_boundary_tiles = []
		river_tiles = []
		uppermost_boundary_tile = self.boundary_tiles["left"][0]
		iterator_state = uppermost_boundary_tile.iterator_state
		
		new_uppermost_tile = Tile(iterator_state)
		new_uppermost_tile.setAltitude()
		new_uppermost_tile.x = uppermost_boundary_tile.x - 2*0.866*uppermost_boundary_tile.side_length
		new_uppermost_tile.y = uppermost_boundary_tile.y

		new_uppermost_tile.neighbours["e"] = uppermost_boundary_tile
		uppermost_boundary_tile.neighbours["w"] = new_uppermost_tile

		if uppermost_boundary_tile.neighbours["sw"] != None:
			uppermost_boundary_tile.neighbours["sw"].neighbours["nw"] = new_uppermost_tile
			new_uppermost_tile.neighbours["se"] = uppermost_boundary_tile.neighbours["sw"]

		new_boundary_tiles.append(new_uppermost_tile)

		for tile in self.boundary_tiles["left"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 2*0.866*tile.side_length
			new_tile.y = tile.y

			new_tile.neighbours["e"] = tile
			tile.neighbours["w"] = new_tile
			
			tile.neighbours["nw"].neighbours["sw"] = new_tile
			new_tile.neighbours["ne"] = tile.neighbours["nw"]

			if tile.neighbours["nw"].neighbours["w"] != None:
				tile.neighbours["nw"].neighbours["w"].neighbours["se"] = new_tile
				new_tile.neighbours["nw"] = tile.neighbours["nw"].neighbours["w"]

			if tile.neighbours["sw"] != None:
				tile.neighbours["sw"].neighbours["nw"] = new_tile
				new_tile.neighbours["se"] = tile.neighbours["sw"]
			
			new_boundary_tiles.append(new_tile)
		
		self.boundary_tiles["left"] = new_boundary_tiles
		self.boundary_tiles["up"].insert(0, new_boundary_tiles[0])
		self.boundary_tiles["down"].insert(0, new_boundary_tiles[-1])

		return river_tiles

	def generateRightSide(self, gui):
		new_boundary_tiles = []
		river_tiles = []

		uppermost_boundary_tile = self.boundary_tiles["right"][0]
		iterator_state = uppermost_boundary_tile.iterator_state
		
		new_uppermost_tile = Tile(iterator_state)
		new_uppermost_tile.setAltitude()
		new_uppermost_tile.x = uppermost_boundary_tile.x + 2*0.866*uppermost_boundary_tile.side_length
		new_uppermost_tile.y = uppermost_boundary_tile.y

		new_uppermost_tile.neighbours["w"] = uppermost_boundary_tile
		uppermost_boundary_tile.neighbours["e"] = new_uppermost_tile

		if uppermost_boundary_tile.neighbours["se"] != None:
			uppermost_boundary_tile.neighbours["se"].neighbours["ne"] = new_uppermost_tile
			new_uppermost_tile.neighbours["nw"] = uppermost_boundary_tile.neighbours["se"]

		new_boundary_tiles.append(new_uppermost_tile)

		for tile in self.boundary_tiles["right"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x + 2*0.866*tile.side_length
			new_tile.y = tile.y

			new_tile.neighbours["w"] = tile
			tile.neighbours["e"] = new_tile
			
			tile.neighbours["ne"].neighbours["se"] = new_tile
			new_tile.neighbours["nw"] = tile.neighbours["ne"]

			if tile.neighbours["ne"].neighbours["e"] != None:
				tile.neighbours["ne"].neighbours["e"].neighbours["sw"] = new_tile
				new_tile.neighbours["ne"] = tile.neighbours["ne"].neighbours["e"]

			if tile.neighbours["se"] != None:
				tile.neighbours["se"].neighbours["ne"] = new_tile
				new_tile.neighbours["sw"] = tile.neighbours["se"]

			new_boundary_tiles.append(new_tile)
		
		self.boundary_tiles["right"] = new_boundary_tiles
		self.boundary_tiles["up"].append(new_boundary_tiles[0])
		self.boundary_tiles["down"].append(new_boundary_tiles[-1])

		return river_tiles


	def generateUpSide(self, gui):
		new_boundary_tiles = []
		river_tiles = []
		leftmost_boundary_tile = self.boundary_tiles["up"][0]
		iterator_state = leftmost_boundary_tile.iterator_state
		
		if leftmost_boundary_tile.neighbours["sw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setAltitude()
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y - 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.neighbours["se"] = leftmost_boundary_tile
			leftmost_boundary_tile.neighbours["nw"] = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["up"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 0.866*tile.side_length
			new_tile.y = tile.y - 1.5*tile.side_length

			new_tile.neighbours["se"] = tile
			tile.neighbours["nw"] = new_tile

			tile.neighbours["w"].neighbours["ne"] = new_tile
			new_tile.neighbours["sw"] = tile.neighbours["w"]

			if tile.neighbours["w"].neighbours["nw"] != None:
				new_tile.neighbours["w"] = tile.neighbours["w"].neighbours["nw"]
				tile.neighbours["w"].neighbours["nw"].neighbours["e"] = new_tile

			new_boundary_tiles.append(new_tile)
		
		rightmost_boundary_tile = self.boundary_tiles["up"][-1]
		if rightmost_boundary_tile.neighbours["se"] != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setAltitude()
			new_rightmost_tile.x = rightmost_boundary_tile.x + 0.866*rightmost_boundary_tile.side_length
			new_rightmost_tile.y = rightmost_boundary_tile.y - 1.5*rightmost_boundary_tile.side_length

			new_rightmost_tile.neighbours["sw"] = rightmost_boundary_tile
			rightmost_boundary_tile.neighbours["ne"] = new_rightmost_tile

			new_rightmost_tile.neighbours["w"] = rightmost_boundary_tile.neighbours["nw"]
			rightmost_boundary_tile.neighbours["nw"].neighbours["e"] = new_rightmost_tile

			new_boundary_tiles.append(new_rightmost_tile)
		
		self.boundary_tiles["up"] = new_boundary_tiles
		self.boundary_tiles["left"].insert(0, new_boundary_tiles[0])
		self.boundary_tiles["right"].insert(0, new_boundary_tiles[-1])

		return river_tiles

	def generateDownSide(self, gui):
		river_tiles = []
		new_boundary_tiles = []
		leftmost_boundary_tile = self.boundary_tiles["down"][0]
		iterator_state = leftmost_boundary_tile.iterator_state
		
		if leftmost_boundary_tile.neighbours["nw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setAltitude()
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y + 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.neighbours["ne"] = leftmost_boundary_tile
			leftmost_boundary_tile.neighbours["sw"] = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["down"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 0.866*tile.side_length
			new_tile.y = tile.y + 1.5*tile.side_length

			new_tile.neighbours["ne"] = tile
			tile.neighbours["sw"] = new_tile

			tile.neighbours["w"].neighbours["se"] = new_tile
			new_tile.neighbours["nw"] = tile.neighbours["w"]

			if tile.neighbours["w"].neighbours["sw"] != None:
				new_tile.neighbours["w"] = tile.neighbours["w"].neighbours["sw"]
				tile.neighbours["w"].neighbours["sw"].neighbours["e"] = new_tile

			new_boundary_tiles.append(new_tile)
		
		rightmost_boundary_tile = self.boundary_tiles["down"][-1]
		if rightmost_boundary_tile.neighbours["ne"] != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setAltitude()
			new_rightmost_tile.x = rightmost_boundary_tile.x + 0.866*rightmost_boundary_tile.side_length
			new_rightmost_tile.y = rightmost_boundary_tile.y + 1.5*rightmost_boundary_tile.side_length

			new_rightmost_tile.neighbours["nw"] = rightmost_boundary_tile
			rightmost_boundary_tile.neighbours["se"] = new_rightmost_tile

			new_rightmost_tile.neighbours["w"] = rightmost_boundary_tile.neighbours["sw"]
			rightmost_boundary_tile.neighbours["sw"].neighbours["e"] = new_rightmost_tile

			new_boundary_tiles.append(new_rightmost_tile)
		
		self.boundary_tiles["down"] = new_boundary_tiles
		self.boundary_tiles["left"].append(new_boundary_tiles[0])
		self.boundary_tiles["right"].append(new_boundary_tiles[-1])

		return river_tiles