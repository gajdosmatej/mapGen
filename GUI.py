import tkinter
from map import Map, Tile, RiverSegment, RiverVertex
import numpy

class WindowHandler:
	'''
	Graphics interface class.
	'''
	def __init__(self):
		#initiate tkinter window and save its size
		self.root = tkinter.Tk()
		self.screen_width = self.root.winfo_screenwidth()
		self.screen_height = self.root.winfo_screenheight()
		self.move_speed = 8

		#create tkinter canvas inside the window
		self.canv_width = self.screen_width // 1.5
		self.canv_height = self.screen_height // 1.5
		self.canvas = tkinter.Canvas(self.root, height=self.canv_height, width=self.canv_width)
		self.canvas.pack()
		
		#create new map (only the structure - create and connect those tiles that will be visible into graph) 
		mapObj = Map(self.screen_width//4, self.screen_height//4)
		mapObj.generateGraph(self)

		#plot all the newly created tiles
		for tile in mapObj.tileIterator():
			tile.activate()
			#self.plotTile(tile, self.getColourOfTile(tile))
			self.plotTile(tile, self.getColourOfTile(tile))
			for river in tile.rivers:
				self.plotRiver(river)

		#create triggers that will move the map when WASD keyboard keys are pressed
		self.root.bind("<KeyPress-w>", lambda event, gui=self: gui.moveMap(mapObj, 0, self.move_speed))
		self.root.bind("<KeyPress-a>", lambda event, gui=self: gui.moveMap(mapObj, self.move_speed, 0))
		self.root.bind("<KeyPress-s>", lambda event, gui=self: gui.moveMap(mapObj, 0, -self.move_speed))
		self.root.bind("<KeyPress-d>", lambda event, gui=self: gui.moveMap(mapObj, -self.move_speed, 0))

		#mapObj.plotAllBounds(self)

		#complete the tkinter window creation
		tkinter.mainloop()

	def plotTile(self, tile :Tile, background_colour :str):
		'''
		Plot hexagon tile to the WindowHandler's canvas.
		@tile ... Tile object which is being plotted.
		@background_colour ... Filling colour of the plotted tile represented by '#RRGGBB' hexadecimal string.
		'''
		points = [	tile.x, tile.y-tile.side_length,
					tile.x+0.866*tile.side_length, tile.y-0.5*tile.side_length,
					tile.x+0.866*tile.side_length, tile.y+0.5*tile.side_length,
					tile.x, tile.y+tile.side_length,
					tile.x-0.866*tile.side_length, tile.y+0.5*tile.side_length,
					tile.x-0.866*tile.side_length, tile.y-0.5*tile.side_length]		
		tile.gui_id = self.canvas.create_polygon(points, outline='black', fill=background_colour, width=2)
		tile.was_plotted = True

	def plotRiver(self, river):
		#self.canvas.create_line(river.start_point, river.mid_point, width=3, fill="#FFFFFF")
		#self.canvas.create_line(river.mid_point, river.end_point, width=3, fill="#FFFFFF")
		if isinstance(river, RiverVertex):
			x, y = river.start_point
			river.gui_id = [self.canvas.create_line(river.start_point, river.end_point, width=3, fill="#0022BB")] 
			if river.is_start:
				river.gui_id.append( self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="#0022BB") )
			#river.gui_id = [self.canvas.create_line(river.start_point, river.end_point, width=3, fill="#0000FF")]
		else:
			river.gui_id = [self.canvas.create_line(river.start_point, river.mid_point, width=3, fill="#0022BB"), 
							self.canvas.create_line(river.mid_point, river.end_point, width=3, fill="#0022BB")]
	
	def hideRiver(self, river):
		for id in river.gui_id:
			self.canvas.delete(id)

	def hideTile(self, tile :Tile):
		'''
		Destroy @tile's hexagon plot from the tkinter canvas.
		@tile ... Tile object which is being removed from the canvas.
		'''
		self.canvas.delete(tile.gui_id)
	
	def isTileOnScreen(self, tile :Tile) -> bool:
		'''
		Returns True if the @tile's coordinates are inside the visible canvas area.
		@tile ... Tile object which coordinates are being considered.
		'''
		offset_delta = tile.side_length
		return (-offset_delta < tile.x < self.canv_width+offset_delta and -offset_delta < tile.y < self.canv_height+offset_delta)

	def moveTiles(self, mapObject :Map, dx :float, dy :float) -> dict[list[Tile]]:
		'''
		Moves the plotted tiles in the specified direction. Returns lists of tiles, which are located on the map boundaries, organised in a dictionary.
		@mapObject ... Map object which contains the tiles that are being moved.
		@dx ... The x coordinate of the moving direction vector.
		@dy ... The y coordinate of the moving direction vector.
		'''

		to_activate = set()
		to_deactivate = set()
		need_new_layer = {"up": False, "down": False, "left": False, "right": False}

		#go through every tile on the map, which is currently visible on-screen
		for tile in mapObject.tileIterator(active_only=True):
			#move the tile's coordinates
			tile.x += dx
			tile.y += dy
			self.canvas.move(tile.gui_id, dx, dy)
			for river in tile.rivers:
				for id in river.gui_id:
					self.canvas.move(id, dx, dy)
					#pass

			#the tile moved off the screen
			if not self.isTileOnScreen(tile):
				to_deactivate.add(tile)
			#the tile is on the screen
			else:
				neighbours = [tile.w, tile.nw, tile.ne, tile.e, tile.se, tile.sw]
				delta_xs = [-2*0.866, -0.866, 0.866, 2*0.866, 0.866, -0.866]
				delta_ys = [0, -1.5, -1.5, 0, 1.5, 1.5]

				#look at all neighbours, update coordinates of those that are not rendered
				for i in range(6):
					if neighbours[i] != None and not neighbours[i].gui_active:
						neighbours[i].x = tile.x + delta_xs[i]*tile.side_length
						neighbours[i].y = tile.y + delta_ys[i]*tile.side_length
						#if the neighbours' new coordinates are on the screen, render that tile
						if self.isTileOnScreen(neighbours[i]):
							to_activate.add(neighbours[i])
							neighbours[i].iterator_state = tile.iterator_state

			#check, whether a visible tile is also on the map boundary
			if tile.w == None:
				need_new_layer["left"] = True
			if tile.nw == None:
				need_new_layer["up"] = True
			if tile.e == None:
				need_new_layer["right"] = True
			if tile.sw == None:
				need_new_layer["down"] = True

		#unrender tiles that are newly off the screen
		for tile in to_deactivate:
			#if tile.gui_active:
			tile.deactivate()
			self.hideTile(tile)
			for river in tile.rivers:
				self.hideRiver(river)

		chunk_size = 5
		new_tiles = []
		river_tiles = []
		
		for key in ["left", "right", "up", "down"]:
			for tile in mapObject.boundary_tiles[key]:
				for river in tile.rivers:
					if river.end == None:	river_tiles.append( (tile, river) )

		if need_new_layer["up"]:
			for _ in range(chunk_size):
				river_tiles += mapObject.generateUpSide(self)
				new_tiles += mapObject.boundary_tiles["up"]
		if need_new_layer["left"]:
			for _ in range(chunk_size):
				river_tiles += mapObject.generateLeftSide(self)
				new_tiles += mapObject.boundary_tiles["left"]
		if need_new_layer["right"]:
			for _ in range(chunk_size):
				river_tiles += mapObject.generateRightSide(self)
				new_tiles += mapObject.boundary_tiles["right"]
		if need_new_layer["down"]:
			for _ in range(chunk_size):
				river_tiles += mapObject.generateDownSide(self)
				new_tiles += mapObject.boundary_tiles["down"]
		
		#make the terrain smoother	
		mapObject.updateSandpiles(new_tiles)
		for tile in new_tiles:
			if tile.isRiverStart():
				river = RiverVertex(tile, is_start=True)
				tile.rivers.append(river)
				river_tiles.append( (tile, river) )
		mapObject.makeRivers(river_tiles)

		#render tiles that are newly visible
		for tile in to_activate:
			#if not tile.gui_active:
				tile.activate()
				self.plotTile(tile, self.getColourOfTile(tile))
				for river in tile.rivers:
					river.setCoords(tile)
					self.plotRiver(river)



	def moveMap(self, mapObject :Map, dx :float, dy :float):
		'''
		Moves the plotted tiles in the specified direction and dynamically creates new tiles, if needed.
		@mapObject ... Map object which contains the tiles that are being moved.
		@dx ... The x coordinate of the moving direction vector.
		@dy ... The y coordinate of the moving direction vector.
		'''
		#move the map tiles
		self.moveTiles(mapObject, dx, dy)

		#possibly update mapObject.centre_tile after movement
		mapObject.updateCentreTile(self.canv_width / 2, self.canv_height / 2)

		#for tile in mapObject.tileIterator():
		#	print(tile.altitude, tile.temperature)



	def getColourOfTile(self, tile :Tile) -> str:
		'''
		Returns the plotting fill colour based on the @tile attributes.
		@tile ... Tile object for which the colour is being chosen.
		'''

		mapping = ['7','5','3','1']
		brightness = int( numpy.floor(100*tile.altitude) )
		first_digit = brightness // 10
		second_digit = brightness % 10

		#ocean
		if tile.altitude < 0:
			return "#0022BB"
		elif tile.is_lake:
			return "#0022BB"
		#mountains
		elif tile.altitude > 0.45:
			return "#AAAAAA"
		elif tile.altitude > 0.3:
			return "#444444"
		else:
			return "#00" + mapping[first_digit] + "000"