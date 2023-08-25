from riverPkg import RiverSegment, RiverVertex
from linkedListPkg import LinkedList
import numpy


class Tile:
	'''
	Class representing map tiles.
	'''
	
	#length of tile side for plotting
	side_length = 25

	#coefficients used for calculating tile's coordinates based on neighbouring tile's coordinates
	#if @tile_1 coordinates (x_1, y_1) are known and @tile_2 is located on @side of @tile_1, then
	# x_2 = x_1 + tile_delta_xs[side] * side_length
	# y_2 = y_1 + tile_delta_ys[side] * side_length 
	delta_xs = {	"w": -2*0.866, 
					"nw": -0.866, 
					"ne": 0.866, 
					"e": 2*0.866, 
					"se": 0.866, 
					"sw": -0.866}

	delta_ys = {	"w": 0, 
					"nw": -1.5, 
					"ne": -1.5, 
					"e": 0, 
					"se": 1.5, 
					"sw": 1.5}
	
	opposing_sides = {	"w": "e",
						"nw": "se",
						"ne": "sw",
						"e": "w",
						"se": "nw",
						"sw": "ne"}


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

		self.setAltitude()

		#centre coordinates
		self.x = None
		self.y = None

		#tkinter-canvas hexagon object
		self.gui_id = None

		#noting which tiles were already visited by iterator
		self.iterator_state = iterator_state

		#is plotted on canvas
		self.gui_active = False

		#was ever plotted
		self.was_plotted = False

		#plot fill colour
		self.colour = None


	def getExistingNeighbours(self) -> dict:
		'''
		Returns dictionary of neighbouring tiles which are not None.
		'''

		return {key: value for key, value in self.neighbours.items() if value != None}


	def setAltitude(self):
		'''
		Sets first random altitude of this tile, which is later updated by Map._updateSandpiles_.
		'''

		self.altitude = numpy.random.choice([-1, 1])


	def isRiverStart(self):
		'''
		Determines, whether a river should have a source in this tile.
		'''

		k = 0.1
		if numpy.random.random() < k*self.altitude:	return True
		return False


	def setRelativeCoordinates(self, tile, side :str):
		'''
		Sets this tile's coordinates based on the @tile (Tile) coordinates, which has this tile on it's @side (str) side.
		'''

		self.x = tile.x + Tile.delta_xs[side] * Tile.side_length
		self.y = tile.y + Tile.delta_ys[side] * Tile.side_length


	def bindTile(self, tile, side :str):
		'''
		Connects @tile (Tile) to this tile's @side (str) (and vice versa). 
		'''
		
		self.neighbours[side] = tile
		opposing_side = Tile.opposing_sides[side]
		tile.neighbours[opposing_side] = self


class Map:
	'''
	Class representing the main map.
	'''

	def __init__(self, centre_x :float, centre_y :float):
		'''
		Constructor of Map class.
		@centre_x (float) ... x coordinate of the GUI canvas' centre.
		@centre_y (float) ... y coordinate of the GUI canvas' centre.
		'''

		#the nearest tile to the canvas' centre
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y

		#the tiles on the map edges
		self.boundary_tiles = {	"left": LinkedList( [self.centre_tile] ), 
								"up": LinkedList( [self.centre_tile] ), 
								"right": LinkedList( [self.centre_tile] ), 
								"down": LinkedList( [self.centre_tile]) 
							}


	def tileIterator(self, active_only :bool = False):
		'''
		Iterator of the map tiles, which iterates over the whole map, or over the currently plotted tiles only, depending on the value of @active_only (bool).
		'''

		#iterator_state which marks the unvisited tiles
		old_state = self.centre_tile.iterator_state

		#iterator state which marks the visited tiles
		new_state = not old_state

		#initialise DFS
		stack = []
		stack.append(self.centre_tile)
		self.centre_tile.iterator_state = new_state

		#DFS
		while stack != []:
			tile = stack.pop()

			#look at the current tile's neighbours and add to stack those that exist, were not visited yet and (optionally) are currently plotted
			for key in ["w", "nw", "ne", "e", "se", "sw"]:
				neighbour = tile.neighbours[key]
				if neighbour != None and neighbour.iterator_state == old_state and (neighbour.gui_active or not active_only):	
					neighbour.iterator_state = new_state
					stack.append(neighbour)

			yield tile


	def updateCentreTile(self, centre_x :float, centre_y :float):
		'''
		Checks, whether there is a tile that is closer to the canvas centre than the current centre_tile. If there is that tile, it becomes map's new centre_tile.
		@centre_x (float) ... Canvas' centre x position.
		@centre_y (float) ... Canvas' centre y position.
		'''

		#squared standard euclidean distance from the canvas' centre
		def squareDistCentre(tile):	return (tile.x - centre_x)**2 + (tile.y - centre_y)**2

		curr_dist = squareDistCentre(self.centre_tile)
		
		#go through the current centre_tile's neighbours; if a neighbour is closer to the canvas' centre, make it the new centre_tile
		for key in self.centre_tile.getExistingNeighbours():
			neighbour = self.centre_tile.neighbours[key]
			if squareDistCentre(neighbour) < curr_dist:
				self.centre_tile = neighbour
				curr_dist = squareDistCentre(neighbour)


	def updateSandpiles(self, tiles :list[Tile]):
		'''
		Make the altitudes of @tiles (list[Tile]) more smooth by averaging tile altitude with its neighbours' altitudes. 
		'''

		alpha = 20	#larger alpha means that the new altitude less depends on the current altitude and more on the neighbours' altitude
		beta=0.01	#larger beta means stronger effect of random change of altitude
		n = 5	#number of iterations of this method's averaging algorithm

		for _ in range(n):
			for tile in tiles:
				neighbours = tile.getExistingNeighbours()
				average_neighbouring_altitude = sum(neighbours[key].altitude for key in neighbours) / len(neighbours)
				tile.altitude = (tile.altitude + alpha*average_neighbouring_altitude) / (1+alpha)
				rand_shift = tile.altitude + beta*numpy.random.uniform(-1,1)

				#apply the random update only if the altitude is still bounded in [-1, 1]
				if -1 <= rand_shift <= 1:	tile.altitude = rand_shift


	def makeRivers(self, river_stack :list):
		'''
		Creates whole rivers from the @river_stack (list[ (Tile, RiverVertex || RiverSegment) ]) incomplete rivers and the tiles in which the rivers are contained. 
		'''
		
		while river_stack != []:
			river_tile, river = river_stack.pop()

			#find the current river_tile's sides in which the altitude decreases (rivers usually flow downstream) 
			#and which were not plotted yet (for consistency, if the tile was already plotted without a river)
			possible_directions = [key for key in river_tile.neighbours	if river_tile.neighbours[key] != None
														and not river_tile.neighbours[key].was_plotted
														and river_tile.altitude >= river_tile.neighbours[key].altitude]
			
			#the current river is located in local minimum of the map altitude function, so do not add it to river_tile.rivers and set the river_tile as lake instead 
			if possible_directions == []:
				river_tile.is_lake = True

			else:
				#add the current river to river_tile's river list (mainly for future plotting)
				river_tile.rivers.append(river)

				#choose randomly the direction in which the current river should flow
				direction = numpy.random.choice(possible_directions)
				
				#set the direction to the current river
				river.end_side = direction
				river.setCoords(river_tile)

				#if there is no ocean in the direction, create new river part
				new_river_tile = river_tile.neighbours[direction]
				if new_river_tile.altitude >= 0:

					#there is already a river in the new_river_tile, so end the current river's creation there with RiverVertex 
					if new_river_tile.rivers != []:
						new_river = RiverVertex(False)
						new_river_tile.rivers.append(new_river)
						new_river.end_side = Tile.opposing_sides[direction]
						new_river.setCoords(new_river_tile)
					#there is no river in the new_river_tile, so continue with the current river's creation by adding new RiverSegment to the river_stack
					else:
						new_river = RiverSegment()
						new_river.start_side = Tile.opposing_sides[direction]
						river_stack.append( (new_river_tile, new_river) )


	def generateGraph(self, gui):
		'''
		Extends the map so that it can be plotted for the first time.
		@gui (WindowHandler) ... The GUI object.
		'''
		
		tiles_rivers = []

		generate_functions = {	"left": self.generateLeftSide,
								"up": self.generateUpSide,
								"right": self.generateRightSide,
								"down": self.generateDownSide
							}
		
		#extend each of the map edges until it is not necessary anymore
		for key in ["left", "up", "right", "down"]:

			#the tile in the middle of the edge is most representative in evaluating whether the map needs to be extended on that side
			tile = self.boundary_tiles[key].middle.value
			while gui.isTileOnScreen(tile):
				generate_functions[key]()
				tile = self.boundary_tiles[key].middle.value
		
		#make the height map of the whole new map smoother
		self.updateSandpiles( list(self.tileIterator()) )
		
		#find tiles which are chosen to have river sources
		for tile in self.tileIterator():
			if tile.isRiverStart():
				river = RiverVertex(True)
				tiles_rivers.append( (tile, river) )
		
		#generate the rest of rivers from the new sources
		self.makeRivers(tiles_rivers)


	def generateNewLayers(self, which_sides: dict[str, bool], chunk_size :int):
		'''
		Generates new tile layers specified by @which_sides (dict[str, bool]).
		@chunk_size (int) ... Number of layers generated on one side.
		'''

		river_tiles = []
		new_tiles = []
		generating_functions = {	"up": self.generateUpSide,
									"left": self.generateLeftSide,
									"right": self.generateRightSide,
									"down": self.generateDownSide
		}

		#generate necessary layers
		for key in ["left", "up", "right", "down"]:
			if which_sides[key]:
				for _ in range(chunk_size):
					generating_functions[key]()
					new_tiles += [ tile for tile in self.boundary_tiles[key].iterator() ]
		
		#make the terrain smoother
		self.updateSandpiles(new_tiles)

		#plot rivers
		for tile in new_tiles:
			if tile.isRiverStart():
				river = RiverVertex(is_start=True)
				river_tiles.append( (tile, river) )
		self.makeRivers(river_tiles)


	def generateLeftSide(self):
		'''
		Generates one new tile layer on the map's left edge.
		'''

		new_boundary_tiles = LinkedList([])

		#generating goes from top to bottom, the tiles are stored in self.boundary_tiles["left"] in this precise order
		uppermost_boundary_tile = self.boundary_tiles["left"].popleft()
		iterator_state = uppermost_boundary_tile.iterator_state
		
		#create the first tile of the new layer
		new_uppermost_tile = Tile(iterator_state)
		new_uppermost_tile.setRelativeCoordinates(uppermost_boundary_tile, "w")

		#the first tile of the new left layer has certainly east neighbour and potentially also south-east neighbour
		uppermost_boundary_tile.bindTile(new_uppermost_tile, "w")

		if uppermost_boundary_tile.neighbours["sw"] != None:
			uppermost_boundary_tile.neighbours["sw"].bindTile(new_uppermost_tile, "nw")

		new_boundary_tiles.append(new_uppermost_tile)

		#create rest of the layer
		for tile in self.boundary_tiles["left"].iterator():
			new_tile = Tile(iterator_state)
			new_tile.setRelativeCoordinates(tile, "w")

			#these tiles have certainly east and north-east neighbours
			#and potentially also north-west and south-east neighbours (in the time of their creation)
			tile.bindTile(new_tile, "w")
			tile.neighbours["nw"].bindTile(new_tile, "sw")
			
			if tile.neighbours["nw"].neighbours["w"] != None:
				tile.neighbours["nw"].neighbours["w"].bindTile(new_tile, "se")

			if tile.neighbours["sw"] != None:
				tile.neighbours["sw"].bindTile(new_tile, "nw")
			
			new_boundary_tiles.append(new_tile)
		
		#update map's boundary_tiles ("up" and "down" got new leftmost tile)
		self.boundary_tiles["left"] = new_boundary_tiles
		self.boundary_tiles["up"].prepend( new_boundary_tiles.start.value )
		self.boundary_tiles["down"].prepend( new_boundary_tiles.end.value )


	def generateRightSide(self):
		'''
		Generates one new tile layer on the map's right edge.
		'''
		new_boundary_tiles = LinkedList([])

		#generating goes from top to bottom, the tiles are stored in self.boundary_tiles["right"] in this precise order
		uppermost_boundary_tile = self.boundary_tiles["right"].popleft()
		iterator_state = uppermost_boundary_tile.iterator_state
		
		#create the first tile of the new layer
		new_uppermost_tile = Tile(iterator_state)
		new_uppermost_tile.setRelativeCoordinates(uppermost_boundary_tile, "e")

		#the first tile of the new left layer has certainly west neighbour and potentially also south-west neighbour
		uppermost_boundary_tile.bindTile(new_uppermost_tile, "e")

		if uppermost_boundary_tile.neighbours["se"] != None:
			uppermost_boundary_tile.neighbours["se"].bindTile(new_uppermost_tile, "ne")

		new_boundary_tiles.append(new_uppermost_tile)

		#create rest of the layer
		for tile in self.boundary_tiles["right"].iterator():
			new_tile = Tile(iterator_state)
			new_tile.setRelativeCoordinates(tile, "e")

			#these tiles have certainly east and north-east neighbours
			#and potentially also north-west and south-east neighbours (in the time of their creation)
			tile.bindTile(new_tile, "e")
			tile.neighbours["ne"].bindTile(new_tile, "se")

			if tile.neighbours["ne"].neighbours["e"] != None:
				tile.neighbours["ne"].neighbours["e"].bindTile(new_tile, "sw")

			if tile.neighbours["se"] != None:
				tile.neighbours["se"].bindTile(new_tile, "ne")

			new_boundary_tiles.append(new_tile)
		
		#update map's boundary_tiles ("up" and "down" got new rightmost tile)
		self.boundary_tiles["right"] = new_boundary_tiles
		self.boundary_tiles["up"].append( new_boundary_tiles.start.value )
		self.boundary_tiles["down"].append( new_boundary_tiles.end.value )


	def generateUpSide(self):
		'''
		Generates one new tile layer on the map's top edge.
		'''

		new_boundary_tiles = LinkedList([])

		#generating goes from left to right, the tiles are stored in self.boundary_tiles["up"] in this precise order
		leftmost_boundary_tile = self.boundary_tiles["up"].popleft()
		iterator_state = leftmost_boundary_tile.iterator_state
		
		#create the first tile of the new layer in the north-west direction, if the current leftmost tile is not already exceeding
		if leftmost_boundary_tile.neighbours["sw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setRelativeCoordinates(leftmost_boundary_tile, "nw")
			leftmost_boundary_tile.bindTile(new_leftmost_tile, "nw")

			new_boundary_tiles.append(new_leftmost_tile)

		#create rest of the layer
		for tile in self.boundary_tiles["up"].iterator():
			new_tile = Tile(iterator_state)
			new_tile.setRelativeCoordinates(tile, "nw")

			#these tiles have certainly south-west and south-east neighbours
			#and usually also west neighbour (in the time of their creation)
			tile.bindTile(new_tile, "nw")
			tile.neighbours["w"].bindTile(new_tile, "ne")

			if tile.neighbours["w"].neighbours["nw"] != None:
				tile.neighbours["w"].neighbours["nw"].bindTile(new_tile, "e")

			new_boundary_tiles.append(new_tile)
		
		#create the last tile which might have been omitted
		rightmost_boundary_tile = self.boundary_tiles["up"].end.value
		if rightmost_boundary_tile.neighbours["se"] != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setRelativeCoordinates(rightmost_boundary_tile, "ne")

			rightmost_boundary_tile.bindTile(new_rightmost_tile, "ne")
			rightmost_boundary_tile.neighbours["nw"].bindTile(new_rightmost_tile, "e")

			new_boundary_tiles.append(new_rightmost_tile)

		#update map's boundary_tiles ("left" and "right" got new uppermost tile)
		self.boundary_tiles["up"] = new_boundary_tiles
		self.boundary_tiles["left"].prepend( new_boundary_tiles.start.value )
		self.boundary_tiles["right"].prepend( new_boundary_tiles.end.value )


	def generateDownSide(self):
		'''
		Generates one new tile layer on the map's bottom edge.
		'''

		new_boundary_tiles = LinkedList([])

		#generating goes from left to right, the tiles are stored in self.boundary_tiles["down"] in this precise order
		leftmost_boundary_tile = self.boundary_tiles["down"].popleft()
		iterator_state = leftmost_boundary_tile.iterator_state
		
		#create the first tile of the new layer in the south-west direction, if the current leftmost tile is not already exceeding
		if leftmost_boundary_tile.neighbours["nw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setRelativeCoordinates(leftmost_boundary_tile, "sw")
			leftmost_boundary_tile.bindTile(new_leftmost_tile, "sw")

			new_boundary_tiles.append(new_leftmost_tile)

		#create rest of the layer
		for tile in self.boundary_tiles["down"].iterator():
			new_tile = Tile(iterator_state)
			new_tile.setRelativeCoordinates(tile, "sw")
			
			#these tiles have certainly north-west and north-east neighbours
			#and usually also west neighbour (in the time of their creation)
			tile.bindTile(new_tile, "sw")
			tile.neighbours["w"].bindTile(new_tile, "se")

			if tile.neighbours["w"].neighbours["sw"] != None:
				tile.neighbours["w"].neighbours["sw"].bindTile(new_tile, "e")

			new_boundary_tiles.append(new_tile)

		#create the last tile which might have been omitted
		rightmost_boundary_tile = self.boundary_tiles["down"].end.value
		if rightmost_boundary_tile.neighbours["ne"] != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setRelativeCoordinates(rightmost_boundary_tile, "se")

			rightmost_boundary_tile.bindTile(new_rightmost_tile, "se")
			rightmost_boundary_tile.neighbours["sw"].bindTile(new_rightmost_tile, "e")

			new_boundary_tiles.append(new_rightmost_tile)

		#update map's boundary_tiles ("left" and "right" got new bottommost tile)
		self.boundary_tiles["down"] = new_boundary_tiles
		self.boundary_tiles["left"].append(new_boundary_tiles.start.value)
		self.boundary_tiles["right"].append(new_boundary_tiles.end.value)
