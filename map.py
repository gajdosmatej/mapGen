from collections import deque
import numpy

class RiverVertex:
	def __init__(self, tile, is_start=False):
		self.is_start = is_start
		self.end = None
		self.end_side = None
		self.gui_id = None
	
	def setCoords(self, tile):
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
	def __init__(self, tile):
		self.start = None
		self.end = None
		
		self.start_side = None
		self.end_side = None
		self.gui_id = None

	def setCoords(self, tile):
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
	side_length = 15
	def __init__(self, iterator_state=False):
		#neighbour compass directions
		self.e = None
		self.ne = None
		self.nw = None
		self.w = None
		self.sw = None
		self.se = None

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

	'''
	def setRivers(self):
		river_add_probability = 0.1
		def indexToSide(index):
			sides = ["w", "nw", "ne", "e", "se", "sw"]
			return sides[index]
		def sideToIndex(side):
			indices = {"w": 0, "nw": 1, "ne": 2, "e": 3, "se": 4, "sw": 5}
			return indices[side]
		def indexToNeighbour(tile, index):
			neighbours = [tile.w, tile.nw, tile.ne, tile.e, tile.se, tile.sw]
			return neighbours[index]
		
		added_river = False
		for i in range(6):
			neighbour = indexToNeighbour(self, i)
			if neighbour != None:
				for river in neighbour.rivers:
					if river.start_side == indexToSide( (i+3)%6 ):
						new_river = RiverSegment(self, indexToSide( numpy.random.choice([j for j in range(6) if j != i]) ), indexToSide(i))
						river.start = new_river
						new_river.end = river
						self.rivers.append(new_river)
						added_river = True
					elif river.end_side == indexToSide( (i+3)%6 ):
						new_river = RiverSegment(self, indexToSide(i), indexToSide( numpy.random.choice([j for j in range(6) if j != i]) ))
						river.end = new_river
						new_river.start = river
						self.rivers.append(new_river)
						added_river = True
		
		if not added_river and numpy.random.random() < river_add_probability:
			end = numpy.random.choice( [i for i in range(6) if (indexToNeighbour(self,i) != None and not indexToNeighbour(self, i).was_plotted) ] )
			start = numpy.random.choice([i for i in range(6) if i != end])
			self.rivers.append( RiverSegment(self, indexToSide(start), indexToSide(end) ) )
		'''

	def getExistingNeighbours(self):
		'''Returns iterator of neighbouring tiles, which are not None.'''
		neighbours = [self.w, self.nw, self.ne, self.e, self.se, self.sw]
		return filter(lambda tile: tile != None, neighbours)


	def setAltitude(self):
		'''existing_neighbours = self.getExistingNeighbours()
		existing_altitudes = [tile.altitude for tile in existing_neighbours]
		self.altitude = 0.3*(numpy.random.random()-0.5)
		if existing_neighbours:
			self.altitude += sum(existing_altitudes) / len(existing_altitudes)
		'''
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
	
	#EXPERIMENTAL
	def plotAllBounds(self, gui):
		for tile in self.tileIterator():
			for neighbour in tile.getExistingNeighbours():
				gui.canvas.create_line((tile.x, tile.y), (neighbour.x, neighbour.y))


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
			if tile.w and tile.w.iterator_state == old_state and conditionFunc(tile.w):	not_visited_tiles.append(tile.w)
			if tile.nw and tile.nw.iterator_state == old_state and conditionFunc(tile.nw):	not_visited_tiles.append(tile.nw)
			if tile.ne and tile.ne.iterator_state == old_state and conditionFunc(tile.ne):	not_visited_tiles.append(tile.ne)
			if tile.e and tile.e.iterator_state == old_state and conditionFunc(tile.e):	not_visited_tiles.append(tile.e)
			if tile.se and tile.se.iterator_state == old_state and conditionFunc(tile.se):	not_visited_tiles.append(tile.se)
			if tile.sw and tile.sw.iterator_state == old_state and conditionFunc(tile.sw):	not_visited_tiles.append(tile.sw)
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
		for neighbour in self.centre_tile.getExistingNeighbours():
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
				neighbours = list( tile.getExistingNeighbours() )
				if neighbours != []:
					average_neighbouring_altitude = sum(neighbour.altitude for neighbour in neighbours) / len(list(neighbours))
					tile.altitude = (tile.altitude + alpha*average_neighbouring_altitude) / (1+alpha)
					rand_shift = tile.altitude + beta*numpy.random.random()
					if -1 < rand_shift < 1:	tile.altitude = rand_shift


	def makeRivers(self, river_tiles):
		def indexToSide(index):
			sides = ["w", "nw", "ne", "e", "se", "sw"]
			return sides[index]
		def sideToIndex(side):
			indices = {"w": 0, "nw": 1, "ne": 2, "e": 3, "se": 4, "sw": 5}
			return indices[side]
		def indexToNeighbour(tile, index):
			neighbours = [tile.w, tile.nw, tile.ne, tile.e, tile.se, tile.sw]
			return neighbours[index]
		
		while river_tiles != []:
			river_tile, river = river_tiles.pop()

			possible_directions = [i for i in range(6)	if indexToNeighbour(river_tile, i) != None
														and not indexToNeighbour(river_tile, i).was_plotted
														and river_tile.altitude >= indexToNeighbour(river_tile, i).altitude]
			
			if possible_directions == []:
				river.end_side = indexToSide(numpy.random.randint(0,6))
				river.setCoords(river_tile)
				river_tile.is_lake = True
				continue
			else:
				'''
				altitudes = [numpy.exp(-indexToNeighbour(river_tile, i).altitude) for i in possible_directions]
				sum_altitudes = sum(altitudes)
				probability_distribution = [ altitude / sum_altitudes for altitude in altitudes]
				direction = numpy.random.choice(possible_directions, p=probability_distribution)
				'''
			
				'''
				direction, smallest_altitude = None, numpy.Infinity
				for i in possible_directions:
					if indexToNeighbour(river_tile, i).altitude < smallest_altitude:
						smallest_altitude = indexToNeighbour(river_tile, i).altitude
						direction = i
				'''

				direction = numpy.random.choice(possible_directions)
						
					
			new_river_tile = indexToNeighbour(river_tile, direction)
			river.end_side = indexToSide(direction)
			river.setCoords(river_tile)

			if new_river_tile.altitude >= 0:
				if new_river_tile.rivers != [] or numpy.random.random() < 0:	#stop
					new_river = RiverVertex(new_river_tile, False)
					new_river_tile.rivers.append(new_river)
					river.end = new_river
					new_river.end = river
					new_river.end_side = indexToSide( (direction+3)%6 )
					new_river.setCoords(new_river_tile)
				else:
					new_river = RiverSegment(new_river_tile)
					new_river_tile.rivers.append(new_river)
					river.end = new_river
					new_river.start = river
					new_river.start_side = indexToSide( (direction+3)%6 )
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
				river = RiverVertex(tile, True)
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

		new_uppermost_tile.e = uppermost_boundary_tile
		uppermost_boundary_tile.w = new_uppermost_tile

		if uppermost_boundary_tile.sw != None:
			uppermost_boundary_tile.sw.nw = new_uppermost_tile
			new_uppermost_tile.se = uppermost_boundary_tile.sw

		new_boundary_tiles.append(new_uppermost_tile)

		for tile in self.boundary_tiles["left"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 2*0.866*tile.side_length
			new_tile.y = tile.y

			new_tile.e = tile
			tile.w = new_tile
			
			tile.nw.sw = new_tile
			new_tile.ne = tile.nw

			if tile.nw.w != None:
				tile.nw.w.se = new_tile
				new_tile.nw = tile.nw.w

			if tile.sw != None:
				tile.sw.nw = new_tile
				new_tile.se = tile.sw
			
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

		new_uppermost_tile.w = uppermost_boundary_tile
		uppermost_boundary_tile.e = new_uppermost_tile

		if uppermost_boundary_tile.se != None:
			uppermost_boundary_tile.se.ne = new_uppermost_tile
			new_uppermost_tile.nw = uppermost_boundary_tile.se

		new_boundary_tiles.append(new_uppermost_tile)

		for tile in self.boundary_tiles["right"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x + 2*0.866*tile.side_length
			new_tile.y = tile.y

			new_tile.w = tile
			tile.e = new_tile
			
			tile.ne.se = new_tile
			new_tile.nw = tile.ne

			if tile.ne.e != None:
				tile.ne.e.sw = new_tile
				new_tile.ne = tile.ne.e

			if tile.se != None:
				tile.se.ne = new_tile
				new_tile.sw = tile.se

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
		
		if leftmost_boundary_tile.sw != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setAltitude()
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y - 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.se = leftmost_boundary_tile
			leftmost_boundary_tile.nw = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["up"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 0.866*tile.side_length
			new_tile.y = tile.y - 1.5*tile.side_length

			new_tile.se = tile
			tile.nw = new_tile

			tile.w.ne = new_tile
			new_tile.sw = tile.w

			if tile.w.nw != None:
				new_tile.w = tile.w.nw
				tile.w.nw.e = new_tile

			new_boundary_tiles.append(new_tile)
		
		rightmost_boundary_tile = self.boundary_tiles["up"][-1]
		if rightmost_boundary_tile.se != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setAltitude()
			new_rightmost_tile.x = rightmost_boundary_tile.x + 0.866*rightmost_boundary_tile.side_length
			new_rightmost_tile.y = rightmost_boundary_tile.y - 1.5*rightmost_boundary_tile.side_length

			new_rightmost_tile.sw = rightmost_boundary_tile
			rightmost_boundary_tile.ne = new_rightmost_tile

			new_rightmost_tile.w = rightmost_boundary_tile.nw
			rightmost_boundary_tile.nw.e = new_rightmost_tile

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
		
		if leftmost_boundary_tile.nw != None:	
			new_leftmost_tile = Tile(iterator_state)
			new_leftmost_tile.setAltitude()
			new_leftmost_tile.x = leftmost_boundary_tile.x - 0.866*leftmost_boundary_tile.side_length
			new_leftmost_tile.y = leftmost_boundary_tile.y + 1.5*leftmost_boundary_tile.side_length

			new_leftmost_tile.ne = leftmost_boundary_tile
			leftmost_boundary_tile.sw = new_leftmost_tile

			new_boundary_tiles.append(new_leftmost_tile)

		for tile in self.boundary_tiles["down"][1:]:
			new_tile = Tile(iterator_state)
			new_tile.setAltitude()
			new_tile.x = tile.x - 0.866*tile.side_length
			new_tile.y = tile.y + 1.5*tile.side_length

			new_tile.ne = tile
			tile.sw = new_tile

			tile.w.se = new_tile
			new_tile.nw = tile.w

			if tile.w.sw != None:
				new_tile.w = tile.w.sw
				tile.w.sw.e = new_tile

			new_boundary_tiles.append(new_tile)
		
		rightmost_boundary_tile = self.boundary_tiles["down"][-1]
		if rightmost_boundary_tile.ne != None:
			new_rightmost_tile = Tile(iterator_state)
			new_rightmost_tile.setAltitude()
			new_rightmost_tile.x = rightmost_boundary_tile.x + 0.866*rightmost_boundary_tile.side_length
			new_rightmost_tile.y = rightmost_boundary_tile.y + 1.5*rightmost_boundary_tile.side_length

			new_rightmost_tile.nw = rightmost_boundary_tile
			rightmost_boundary_tile.se = new_rightmost_tile

			new_rightmost_tile.w = rightmost_boundary_tile.sw
			rightmost_boundary_tile.sw.e = new_rightmost_tile

			new_boundary_tiles.append(new_rightmost_tile)
		
		self.boundary_tiles["down"] = new_boundary_tiles
		self.boundary_tiles["left"].append(new_boundary_tiles[0])
		self.boundary_tiles["right"].append(new_boundary_tiles[-1])

		return river_tiles