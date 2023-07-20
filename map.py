from collections import deque

class Tile:
	def __init__(self):
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
		self.GUI_pointer = None


class Map:
	def __init__(self, centre_x :int, centre_y :int):
		self.centre_tile = Tile()
		self.centre_tile.x = centre_x
		self.centre_tile.y = centre_y
	
	def generate(self, gui):
		gen_queue = deque()
		gen_queue.append(self.centre_tile)
		while gen_queue:
			tile = gen_queue.popleft()
			gui.plotTile(tile.x, tile.y, "#00FF00")
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
					gen_queue.append(new_tile)



