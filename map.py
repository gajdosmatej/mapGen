from collections import deque
import numpy

class Tile:
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
		self.colour = None

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

class Map:
	def __init__(self, centre_x :int, centre_y :int):
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y
	
	def tileIterator(self, active_only = False, gui = None):	#active_only ... those that are rendered
		queue = deque()
		def conditionFunc(tile):	return (not active_only) or ((0 < tile.x < gui.screen_width) and (0 < tile.y < gui.screen_height)) 
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
	
	def updateSandpiles(self, tiles):
		for tile in tiles:
			neighbours = tile.getExistingNeighbours()
			'''lower_neighbours = list(filter(lambda n: n.altitude < tile.altitude-0.2, neighbours))
			tile.altitude -= 0.05*len(lower_neighbours)
			for neighbour in lower_neighbours:
				neighbour.altitude += 0.05
			'''
			for neighbour in neighbours:
				diff = (neighbour.altitude - tile.altitude) / 2
				#neighbour.altitude, tile.altitude = neighbour.altitude - 0.5*diff, tile.altitude + 0.5*diff
				tile.altitude += 0.5*diff

	def generateGraph(self, gui):
		self.centre_tile.altitude = numpy.random.random()
		gen_queue = deque()
		gen_queue.append(self.centre_tile)
		while gen_queue:
			tile = gen_queue.popleft()
			if tile.x > 0 and tile.w == None:
					new_tile = Tile()
					new_tile.e = tile
					tile.w = new_tile
					if tile.nw != None:	
						tile.nw.sw = new_tile
						new_tile.ne = tile.nw
					if tile.sw != None:	
						tile.sw.nw = new_tile
						new_tile.se = tile.sw
					new_tile.x = tile.x - 2*0.866*gui.tile_side_length
					new_tile.y = tile.y
					new_tile.setAltitude()
					gen_queue.append(new_tile)
			if tile.x > 0 and tile.y > 0 and tile.nw == None:
					new_tile = Tile()
					new_tile.se = tile
					tile.nw = new_tile
					if tile.w != None:
						tile.w.ne = new_tile
						new_tile.sw = tile.w
					if tile.ne != None:
						tile.ne.w = new_tile
						new_tile.e = tile.ne
					new_tile.x = tile.x - 0.866*gui.tile_side_length
					new_tile.y = tile.y - 1.5*gui.tile_side_length
					new_tile.setAltitude()
					gen_queue.append(new_tile)
			if tile.x < gui.canv_width and tile.y > 0 and tile.ne == None:
					new_tile = Tile()
					new_tile.sw = tile
					tile.ne = new_tile
					if tile.e != None:
						tile.e.nw = new_tile
						new_tile.se = tile.e
					if tile.nw != None:
						tile.nw.e = new_tile
						new_tile.w = tile.nw
					new_tile.x = tile.x + 0.866*gui.tile_side_length
					new_tile.y = tile.y - 1.5*gui.tile_side_length
					new_tile.setAltitude()
					gen_queue.append(new_tile)
			if tile.x < gui.canv_width and tile.e == None:
				new_tile = Tile()
				new_tile.w = tile
				tile.e = new_tile
				if tile.ne != None:
					tile.ne.se = new_tile
					new_tile.nw = tile.ne
				if tile.se != None:
					tile.se.ne = new_tile
					new_tile.sw = tile.se
				new_tile.x = tile.x + 2*0.866*gui.tile_side_length
				new_tile.y = tile.y
				new_tile.setAltitude()
				gen_queue.append(new_tile)
			if tile.x < gui.canv_width and tile.y < gui.canv_height and tile.se == None:
					new_tile = Tile()
					new_tile.nw = tile
					tile.se = new_tile
					if tile.e != None:
						tile.e.sw = new_tile
						new_tile.ne = tile.e
					if tile.sw != None:
						tile.sw.e = new_tile
						new_tile.w = tile.sw
					new_tile.x = tile.x + 0.866*gui.tile_side_length
					new_tile.y = tile.y + 1.5*gui.tile_side_length
					new_tile.setAltitude()
					gen_queue.append(new_tile)
			if tile.x > 0 and tile.y < gui.canv_height and tile.sw == None:
					new_tile = Tile()
					new_tile.ne = tile
					tile.sw = new_tile
					if tile.w != None:
						tile.w.se = new_tile
						new_tile.nw = tile.w
					if tile.se != None:
						tile.se.w = new_tile
						new_tile.e = tile.se
					new_tile.x = tile.x - 0.866*gui.tile_side_length
					new_tile.y = tile.y + 1.5*gui.tile_side_length
					new_tile.setAltitude()
					gen_queue.append(new_tile)
		for _ in range(4):	
			self.updateSandpiles(self.tileIterator())
		for tile in self.tileIterator():	#VYKRESLOVANI PRESUNUTO SEM
			colour = gui.getColourFromAltitude(tile.altitude)
			gui.plotTile(tile, colour)


