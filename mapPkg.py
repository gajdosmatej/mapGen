from riverPkg import RiverSegment, RiverVertex
import numpy


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

		self.setAltitude()

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




class Map:
	'''
	Class representing the main map.
	'''

	def __init__(self, centre_x :int, centre_y :int):
		'''
		Constructor of Map class.
		@centre_x (int) ... x coordinate of the GUI canvas' centre.
		@centre_y (int) ... y coordinate of the GUI canvas' centre.
		'''

		#the nearest tile to the canvas' centre
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y

		#the tiles on the map edges
		self.boundary_tiles = {"left": [self.centre_tile], "up": [self.centre_tile], "right": [self.centre_tile], "down": [self.centre_tile]}


	def tileIterator(self, active_only = False):
		'''
		Iterator of the map tiles, which iterates over the whole map, or over the currently plotted tiles only, depending on the value of @active_only (bool).
		'''

		#iterator_state which marks the unvisited tiles
		old_state = self.centre_tile.iterator_state

		#iterator state which marks the visited tiles
		new_state = not old_state

		#initialise DFS
		stack = []
		def conditionFunc(tile):	return (not active_only) or tile.gui_active
		stack.append(self.centre_tile)
		self.centre_tile.iterator_state = new_state

		#DFS
		while stack != []:
			tile = stack.pop()
			not_visited_tiles = []

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
		@centre_x ... Canvas' centre x position.
		@centre_y ... Canvas' centre y position.
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
				if -1 < rand_shift < 1:	tile.altitude = rand_shift


	def makeRivers(self, river_stack :list):
		'''
		Creates whole rivers from the @river_stack (list[ (Tile, RiverVertex || RiverSegment) ]) incomplete rivers and the tiles in which the rivers are contained. 
		'''
		
		opposing_sides = {"w": "e", "nw": "se", "ne": "sw", "e": "w", "se": "nw", "sw": "ne"}
		
		while river_stack != []:
			river_tile, river = river_stack.pop()

			#find the current river_tile's sides in which the altitude decreases (rivers usually flow downstream ;-;)
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
						new_river.end_side = opposing_sides[direction]
						new_river.setCoords(new_river_tile)
					#there is no river in the new_river_tile, so continue with the current'river's creation by adding new RiverSegment to the river_stack
					else:
						new_river = RiverSegment()
						new_river.start_side = opposing_sides[direction]
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
			index = len( self.boundary_tiles[key] ) // 2
			tile = self.boundary_tiles[key][index]
			while gui.isTileOnScreen(tile):
				generate_functions[key](gui)
				tile = self.boundary_tiles[key][index]
		
		#make the height map of the whole new map smoother
		self.updateSandpiles( list(self.tileIterator()) )
		
		#find tiles which are chosen to have river sources
		for tile in self.tileIterator():
			if tile.isRiverStart():
				river = RiverVertex(True)
				tiles_rivers.append( (tile, river) )
		
		#generate the rest of rivers from the new sources
		self.makeRivers(tiles_rivers)


	def generateLeftSide(self, gui):
		new_boundary_tiles = []
		uppermost_boundary_tile = self.boundary_tiles["left"][0]
		iterator_state = uppermost_boundary_tile.iterator_state
		
		new_uppermost_tile = Tile(iterator_state)
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


	def generateRightSide(self, gui):
		new_boundary_tiles = []

		uppermost_boundary_tile = self.boundary_tiles["right"][0]
		iterator_state = uppermost_boundary_tile.iterator_state
		
		new_uppermost_tile = Tile(iterator_state)
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


	def generateUpSide(self, gui):
		new_boundary_tiles = []
		leftmost_boundary_tile = self.boundary_tiles["up"][0]
		iterator_state = leftmost_boundary_tile.iterator_state
		
		if leftmost_boundary_tile.neighbours["sw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y - 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.neighbours["se"] = leftmost_boundary_tile
			leftmost_boundary_tile.neighbours["nw"] = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["up"][1:]:
			new_tile = Tile(iterator_state)
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

	def generateDownSide(self, gui):
		new_boundary_tiles = []
		leftmost_boundary_tile = self.boundary_tiles["down"][0]
		iterator_state = leftmost_boundary_tile.iterator_state
		
		if leftmost_boundary_tile.neighbours["nw"] != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y + 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.neighbours["ne"] = leftmost_boundary_tile
			leftmost_boundary_tile.neighbours["sw"] = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["down"][1:]:
			new_tile = Tile(iterator_state)
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