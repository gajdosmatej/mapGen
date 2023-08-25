import tkinter
from mapPkg import Tile, Map, RiverSegment, RiverVertex
from mapPkg import numpy

class WindowHandler:
	'''
	Graphics interface class.
	'''

	def __init__(self):
		'''
		Constructor of WindowHandler class.
		'''

		#initiate tkinter window and save screen size
		self.root = tkinter.Tk()
		self.root.title("Hex Map Generator")
		self.screen_width = self.root.winfo_screenwidth()
		self.screen_height = self.root.winfo_screenheight()
		
		#set the number of pixels in which the map moves on one keypress
		self.move_speed = 10

		#how many layers are added simultaneously
		self.chunk_size = 10

		#create tkinter canvas inside the window
		self.canv_width = self.screen_width // 1.5
		self.canv_height = self.screen_height // 1.5
		self.canvas = tkinter.Canvas(self.root, height=self.canv_height, width=self.canv_width)
		self.canvas.pack()
		
		#create new map (only the structure - create and connect those tiles that will be visible into graph) 
		mapObj = Map(self.canv_width//2, self.canv_height//2)
		mapObj.generateGraph(self)

		#plot all the newly created tiles
		for tile in mapObj.tileIterator():
			tile.gui_active = True
			self.setColourOfTile(tile)
			self.plotTile(tile)

			for river in tile.rivers:
				self.plotRiver(river)

		#create triggers that will move the map when WASD keyboard keys are pressed
		self.root.bind("<KeyPress-w>", lambda event, gui=self: gui.moveMap(mapObj, 0, self.move_speed))
		self.root.bind("<KeyPress-a>", lambda event, gui=self: gui.moveMap(mapObj, self.move_speed, 0))
		self.root.bind("<KeyPress-s>", lambda event, gui=self: gui.moveMap(mapObj, 0, -self.move_speed))
		self.root.bind("<KeyPress-d>", lambda event, gui=self: gui.moveMap(mapObj, -self.move_speed, 0))

		#complete the tkinter window creation
		tkinter.mainloop()


	def plotTile(self, tile :Tile):
		'''
		Plot hexagon tile on the canvas.
		@tile (Tile) ... Tile which is being plotted.
		'''
		points = [	tile.x, tile.y - Tile.side_length,
					tile.x + 0.866*Tile.side_length, tile.y - 0.5*Tile.side_length,
					tile.x + 0.866*Tile.side_length, tile.y + 0.5*Tile.side_length,
					tile.x, tile.y + Tile.side_length,
					tile.x - 0.866*Tile.side_length, tile.y + 0.5*Tile.side_length,
					tile.x - 0.866*Tile.side_length, tile.y - 0.5*Tile.side_length]		
		tile.gui_id = self.canvas.create_polygon(points, outline='black', fill=tile.colour, width=2)
		tile.was_plotted = True


	def plotRiver(self, river):
		'''
		Plot @river (RiverVertex || RiverSegment) from it's coordinates.
		'''

		#RiverVertex is plotted differently than RiverSegment
		if isinstance(river, RiverVertex):
			x, y = river.start_point
			river.gui_ids = [self.canvas.create_line(river.start_point, river.end_point, width=3, fill="#0022BB")]

			#small circle indicating river source
			if river.is_start:
				river.gui_ids.append( self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#0022BB") )
		else:
			river.gui_ids = [self.canvas.create_line(river.start_point, river.mid_point, width=3, fill="#0022BB"), 
							self.canvas.create_line(river.mid_point, river.end_point, width=3, fill="#0022BB")]


	def hideRiver(self, river):
		'''
		Remove @river's (RiverVertex || RiverSegment) plot from the canvas.
		'''

		for id in river.gui_ids:
			self.canvas.delete(id)


	def hideTile(self, tile :Tile):
		'''
		Remove @tile's (Tile) hexagon plot from the canvas.
		'''

		self.canvas.delete(tile.gui_id)


	def hideTiles(self, tiles :list[Tile]):
		'''
		Remove tiles and their rivers specified in @tiles (list[Tile]) from the canvas.
		'''

		for tile in tiles:
			tile.gui_active = False
			self.hideTile(tile)
			for river in tile.rivers:
				self.hideRiver(river)


	def plotTiles(self, tiles :list[Tile]):
		'''
		Plot tiles and their rivers specified in @tiles (list[Tile]) on the canvas. 
		'''

		for tile in tiles:
				tile.gui_active = True

				#set fill colour of tiles that were created in previous _moveMap_
				if not tile.was_plotted:
					self.setColourOfTile(tile)

				self.plotTile(tile)
				for river in tile.rivers:
					river.setCoords(tile)
					self.plotRiver(river)


	def isTileOnScreen(self, tile :Tile):
		'''
		Returns True if the @tile's (Tile) coordinates are inside the visible canvas area.
		'''

		offset_delta = Tile.side_length
		return (-offset_delta < tile.x < self.canv_width+offset_delta and -offset_delta < tile.y < self.canv_height+offset_delta)


	def moveMap(self, mapObject :Map, dx :float, dy :float):
		'''
		Moves the plotted tiles in the specified direction.
		@mapObject (Map) ... Map object which contains the tiles that are being moved.
		@dx (float) ... The x coordinate of the moving direction vector.
		@dy (float) ... The y coordinate of the moving direction vector.
		'''

		to_activate = set()
		to_deactivate = set()
		need_new_layer = {"up": False, "down": False, "left": False, "right": False}

		#go through every tile which is currently visible on-screen
		for tile in mapObject.tileIterator(active_only=True):

			#move the tile's coordinates
			tile.x += dx
			tile.y += dy
			self.canvas.move(tile.gui_id, dx, dy)
			
			#move the tile's rivers
			for river in tile.rivers:
				for id in river.gui_ids:
					self.canvas.move(id, dx, dy)

			#if the tile moved off the screen, deactivate it
			if not self.isTileOnScreen(tile):
				to_deactivate.add(tile)
			
			#the tile is on the screen
			else:

				#look at all neighbours, update coordinates of those that are not rendered
				for key in tile.neighbours:
					neighbour = tile.neighbours[key]
					if neighbour != None and not neighbour.gui_active:
						neighbour.setRelativeCoordinates(tile, key)

						#if the neighbours' new coordinates are on the screen, render that tile
						if self.isTileOnScreen(neighbour):
							to_activate.add(neighbour)
							neighbour.iterator_state = tile.iterator_state

			#check, whether a visible tile is also on the map boundary
			if tile.neighbours["w"] == None:
				need_new_layer["left"] = True

			if tile.neighbours["nw"] == None:
				need_new_layer["up"] = True

			if tile.neighbours["e"] == None:
				need_new_layer["right"] = True

			if tile.neighbours["sw"] == None:
				need_new_layer["down"] = True

		#unrender tiles that are newly off the screen
		self.hideTiles(to_deactivate)
		
		#generate new necessary layers
		mapObject.generateNewLayers(need_new_layer, self.chunk_size)

		#render tiles that are newly visible
		self.plotTiles(to_activate)

		#possibly update mapObject.centre_tile after movement
		mapObject.updateCentreTile(self.canv_width / 2, self.canv_height / 2)


	def setColourOfTile(self, tile :Tile):
		'''
		Sets the @tile's (Tile) fill colour based on the @tile attributes.
		'''

		mapping = ['7','5','3','1']
		brightness = int( numpy.floor(10*tile.altitude) )

		#ocean
		if tile.altitude < 0:
			tile.colour = "#0022BB"
		elif tile.is_lake:
			tile.colour = "#0022BB"
		#mountains
		elif tile.altitude > 0.45:
			tile.colour = "#AAAAAA"
		elif tile.altitude > 0.3:
			tile.colour = "#444444"
		else:
			tile.colour = "#00" + mapping[brightness] + "000"
