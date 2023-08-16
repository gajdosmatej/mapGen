from collections import deque
import numpy

class Tile:
	side_length = 12
	def __init__(self, iterator_state=False):
		#neighbour compass directions
		self.e = None
		self.ne = None
		self.nw = None
		self.w = None
		self.sw = None
		self.se = None

		#tile biome parameters
		self.temperature = None
		self.altitude = None
		self.humidity = None

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
		self.altitude = numpy.random.uniform(-1,1)

	def activate(self):
		self.gui_active = True

	def deactivate(self):
		self.gui_active = False

class Map:
	def __init__(self, centre_x :int, centre_y :int):
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y
		self.centre_tile.setAltitude()
	
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
		for tile in tiles:
			for neighbour in tile.getExistingNeighbours():
				tile.altitude = (tile.altitude + 0.5*neighbour.altitude) / 1.5


	def generateGraph(self, gui):
		self.centre_tile.w = Tile()
		self.centre_tile.nw = Tile()
		self.centre_tile.ne = Tile()
		self.centre_tile.e = Tile()
		self.centre_tile.se = Tile()
		self.centre_tile.sw = Tile()

		w, nw, ne, e, se, sw = self.centre_tile.w, self.centre_tile.nw, self.centre_tile.ne, self.centre_tile.e, self.centre_tile.se, self.centre_tile.sw

		w.x = self.centre_tile.x - 2*0.866*self.centre_tile.side_length
		nw.x = self.centre_tile.x - 0.866*self.centre_tile.side_length
		ne.x = self.centre_tile.x + 0.866*self.centre_tile.side_length
		e.x = self.centre_tile.x + 2*0.866*self.centre_tile.side_length
		se.x = self.centre_tile.x + 0.866*self.centre_tile.side_length
		sw.x = self.centre_tile.x - 0.866*self.centre_tile.side_length

		w.y = self.centre_tile.y
		nw.y = self.centre_tile.y - 1.5*self.centre_tile.side_length
		ne.y = self.centre_tile.y - 1.5*self.centre_tile.side_length
		e.y = self.centre_tile.y
		se.y = self.centre_tile.y + 1.5*self.centre_tile.side_length
		sw.y = self.centre_tile.y + 1.5*self.centre_tile.side_length
		
		w.e = self.centre_tile
		w.ne = nw
		w.se = sw

		nw.se = self.centre_tile
		nw.e = ne
		nw.sw = w

		ne.sw = self.centre_tile
		ne.w = nw
		ne.se = e

		e.w = self.centre_tile
		e.nw = ne
		e.sw = se

		se.nw = self.centre_tile
		se.ne = e
		se.w = sw

		sw.ne = self.centre_tile
		sw.e = se
		sw.nw = w

		w.setAltitude()
		nw.setAltitude()
		ne.setAltitude()
		e.setAltitude()
		se.setAltitude()
		sw.setAltitude()

		self.generateNecessaryLayers(gui)
		
		for _ in range(5):
			self.updateSandpiles(self.tileIterator())


	def generateNecessaryLayers(self, gui, iterator_state = False):
		all_new_tiles = []
		need_new_layer = True
		while need_new_layer:
			layer_new_tiles = self.generateNewLayer(iterator_state)
			need_new_layer = False
			for tile in layer_new_tiles:
				if gui.isTileOnScreen(tile):	
					need_new_layer = True
					break
			all_new_tiles += layer_new_tiles
		return all_new_tiles


	def generateNewLayer(self, iterator_state = False):
		new_tiles = []
		start = self.centre_tile
		while start.w != None:
			start = start.w
		
		def indexToNeighbour(tile, index):
			neighbours = [tile.w, tile.nw, tile.ne, tile.e, tile.se, tile.sw]
			return neighbours[index]
		
		stack = [(start, -1)]
		while stack:
			boundary_tile, index_of_previous = stack.pop()
			found = False
			for neigh_i in range(6):
				neigh_i = (neigh_i+index_of_previous)%6	#chytry zpusob obihani
				if neigh_i == index_of_previous:	continue	#nevracet se zpatky
				neighbour = indexToNeighbour(boundary_tile, neigh_i)
				if neighbour == None:	#cas pridat policko
					new_tiles.append( (boundary_tile, neigh_i) )	#(policko, kam-nove-policko)
				elif neighbour != start:
					for neigh_neigh_i in range(6):
						neigh_neigh = indexToNeighbour(neighbour, neigh_neigh_i)
						if neigh_neigh == None and not found:	#soused boundary_tile ma nejake volne pole
							stack.append( (neighbour, (neigh_i+3)%6 ) )	#(policko, smer-kterym-se-nevracet)
							found = True
							break
		
		unique_new_tiles = []
		x_offsets = [-2*0.866, -0.866, 0.866, 2*0.866, 0.866, -0.866]
		y_offsets = [0, -1.5, -1.5, 0, 1.5, 1.5]
		for creator_tile, index in new_tiles:
			if indexToNeighbour(creator_tile, index) == None:
				new_tile = Tile()
				new_tile.iterator_state = iterator_state
				new_tile.x = creator_tile.x + x_offsets[index]*new_tile.side_length
				new_tile.y = creator_tile.y + y_offsets[index]*new_tile.side_length
				new_tile.setAltitude()
				unique_new_tiles.append(new_tile)
				#gui.plotTile(new_tile, gui.getColourOfTile(new_tile))
				#i = input()
			else:
				new_tile = indexToNeighbour(creator_tile, index)
			if index == 0:	#w
				creator_tile.w = new_tile
				new_tile.e = creator_tile
				if creator_tile.nw != None:
					creator_tile.nw.sw = new_tile
					new_tile.ne = creator_tile.nw
				if creator_tile.sw != None:
					creator_tile.sw.nw = new_tile
					new_tile.se = creator_tile.sw
				
			elif index == 1:	#nw
				creator_tile.nw = new_tile
				new_tile.se = creator_tile
				if creator_tile.w != None:
					creator_tile.w.ne = new_tile
					new_tile.sw = creator_tile.w
				if creator_tile.ne != None:
					creator_tile.ne.w = new_tile
					new_tile.e = creator_tile.ne
				
			elif index == 2:	#ne
				creator_tile.ne = new_tile
				new_tile.sw = creator_tile
				if creator_tile.nw != None:
					creator_tile.nw.e = new_tile
					new_tile.w = creator_tile.nw
				if creator_tile.e != None:
					creator_tile.e.nw = new_tile
					new_tile.se = creator_tile.e
				
			elif index == 3:	#e
				creator_tile.e = new_tile
				new_tile.w = creator_tile
				if creator_tile.ne != None:
					creator_tile.ne.se = new_tile
					new_tile.nw = creator_tile.ne
				if creator_tile.se != None:
					creator_tile.se.ne = new_tile
					new_tile.sw = creator_tile.se
			
			elif index == 4:	#se
				creator_tile.se = new_tile
				new_tile.nw = creator_tile
				if creator_tile.e != None:
					creator_tile.e.sw = new_tile
					new_tile.ne = creator_tile.e
				if creator_tile.sw != None:
					creator_tile.sw.e = new_tile
					new_tile.w = creator_tile.sw

			elif index == 5:	#sw
				creator_tile.sw = new_tile
				new_tile.ne = creator_tile
				if creator_tile.se != None:
					creator_tile.se.w = new_tile
					new_tile.e = creator_tile.se
				if creator_tile.w != None:
					creator_tile.w.se = new_tile
					new_tile.nw = creator_tile.w

		return unique_new_tiles
