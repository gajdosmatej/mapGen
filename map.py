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
	def __init__(self, px_width :int, px_height :int):
		self.centre_tile = None
	
	def generate(self):
		pass



