import tkinter
from map import Map, Tile
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

		#create tkinter canvas inside the window
		self.canv_width = self.screen_width // 2
		self.canv_height = self.screen_height // 2
		self.canvas = tkinter.Canvas(self.root, height=self.canv_height, width=self.canv_width)
		self.canvas.pack()
		
		#create new map (only the structure - create and connect those tiles that will be visible into graph) 
		mapObj = Map(self.screen_width//4, self.screen_height//4)
		mapObj.generateGraph(self)

		#plot all the newly created tiles
		for tile in mapObj.tileIterator():
			self.plotTile(tile, self.getColourOfTile(tile))

		#create triggers that will move the map when WASD keyboard keys are pressed
		self.root.bind("<KeyPress-w>", lambda event, gui=self: gui.moveMap(mapObj, 0, 10))
		self.root.bind("<KeyPress-a>", lambda event, gui=self: gui.moveMap(mapObj, 10, 0))
		self.root.bind("<KeyPress-s>", lambda event, gui=self: gui.moveMap(mapObj, 0, -10))
		self.root.bind("<KeyPress-d>", lambda event, gui=self: gui.moveMap(mapObj, -10, 0))

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
		tile.gui_active = True
		tile.gui_id = self.canvas.create_polygon(points, outline='black', fill=background_colour, width=2)

	def hideTile(self, tile :Tile):
		'''
		Destroy @tile's hexagon plot from the tkinter canvas.
		@tile ... Tile object which is being removed from the canvas.
		'''
		self.canvas.delete(tile.gui_id)
		tile.gui_active = False
	
	def isTileOnScreen(self, tile :Tile) -> bool:
		'''
		Returns True if the @tile's coordinates are inside the visible canvas area.
		@tile ... Tile object which coordinates are being considered.
		'''
		offset_delta = tile.side_length
		return (-offset_delta < tile.x < self.screen_width+offset_delta and -offset_delta < tile.y < self.screen_height+offset_delta)

	def moveTiles(self, mapObject :Map, dx :float, dy :float) -> dict[list[Tile]]:
		'''
		Moves the plotted tiles in the specified direction. Returns lists of tiles, which are located on the map boundaries, organised in a dictionary.
		@mapObject ... Map object which contains the tiles that are being moved.
		@dx ... The x coordinate of the moving direction vector.
		@dy ... The y coordinate of the moving direction vector.
		'''
		boundary_tiles = {"left": [], "up": [], "right": [], "down": []}
		
		#go through every tile on the map
		for tile in mapObject.tileIterator():
			#move the tile's coordinates
			tile.x += dx
			tile.y += dy

			#deactivate tile that is off the screen and remove it from the canvas
			if not self.isTileOnScreen(tile):
				self.hideTile(tile)
			#activate tile that is on the screen and plot it on the canvas
			elif not tile.gui_active:
				self.plotTile(tile, self.getColourOfTile(tile))
			#move tile plot on the canvas
			else:
				self.canvas.move(tile.gui_id, dx, dy)
			
			#determine, whether the tile lies on the map boundary_tiles
			if tile.w == None:	boundary_tiles["left"].append(tile)
			if tile.e == None:	boundary_tiles["right"].append(tile)
			if tile.nw == None and tile.ne == None:	boundary_tiles["up"].append(tile)
			if tile.sw == None and tile.se == None:	boundary_tiles["down"].append(tile)	
		
		return boundary_tiles

	def updateBoundaries(self, boundary_tiles :dict[list[Tile]]) -> list[Tile]:
		'''
		Checks the tiles located on the map boundaries. Creates new tiles, where there would be otherwise a blank space after map movement, and returns a list of them.
		@boundary_tiles ... Dictionary with keys 'left', 'right', 'up' and 'down' pointing to list of corresponding boundary tiles.
		'''
		new_tiles = []
		for tile in boundary_tiles["left"]:
			if tile.x > 0:
				new_tile = Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 2*0.866*tile.side_length
				new_tile.y = tile.y

				tile.w = new_tile
				new_tile.e = tile
				if tile.nw != None:
					tile.nw.sw = new_tile
					new_tile.ne = tile.nw
				if tile.sw != None:
					tile.sw.nw = new_tile
					new_tile.se = tile.sw

				new_tile.setAltitude()
				new_tiles.append(new_tile)

		for tile in boundary_tiles["right"]:
			if tile.x < self.canv_width:
				new_tile = Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x + 2*0.866*tile.side_length
				new_tile.y = tile.y
				
				tile.e = new_tile
				new_tile.w = tile
				if tile.ne != None:
					tile.ne.se = new_tile
					new_tile.nw = tile.ne
				if tile.se != None:
					tile.se.ne = new_tile
					new_tile.sw = tile.se 

				new_tile.setAltitude()
				new_tiles.append(new_tile)

		for tile in boundary_tiles["up"]:
			if tile.y > 0:
				new_tile = Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 0.866*tile.side_length
				new_tile.y = tile.y - 1.5*tile.side_length

				tile.nw = new_tile
				new_tile.se = tile
				if tile.w != None:
					tile.w.ne = new_tile
					new_tile.sw = tile.w

					if tile.w.nw != None:
						tile.w.nw.e = new_tile
						new_tile.w = tile.w.nw

				if tile.ne != None:
					tile.ne.w = new_tile
					new_tile.e = tile.ne

				new_tile.setAltitude()
				new_tiles.append(new_tile)

		for tile in boundary_tiles["down"]:
			if tile.y < self.canv_height:
				new_tile = Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 0.866*tile.side_length
				new_tile.y = tile.y + 1.5*tile.side_length

				tile.sw = new_tile
				new_tile.ne = tile
				if tile.w != None:
					tile.w.se = new_tile
					new_tile.nw = tile.w

					if tile.w.sw != None:
						tile.w.sw.e = new_tile
						new_tile.w = tile.w.sw
						
				if tile.se != None:
					tile.se.w = new_tile
					new_tile.e = tile.se

				new_tile.setAltitude()
				new_tiles.append(new_tile)
		
		return new_tiles


	def moveMap(self, mapObject :Map, dx :float, dy :float):
		'''
		Moves the plotted tiles in the specified direction and dynamically creates new tiles, if needed.
		@mapObject ... Map object which contains the tiles that are being moved.
		@dx ... The x coordinate of the moving direction vector.
		@dy ... The y coordinate of the moving direction vector.
		'''
		#Lists of tiles that are located on the map boundaries
		boundary_tiles = self.moveTiles(mapObject, dx, dy)

		#possibly update mapObject.centre_tile after movement
		mapObject.updateCentreTile(self.canv_width / 2, self.canv_height / 2)

		#newly created tiles on the map boundaries
		new_tiles = self.updateBoundaries(boundary_tiles)
		
		#make the terrain smoother
		for _ in range(4):	mapObject.updateSandpiles(new_tiles)
		
		#plot the newly created tiles
		for tile in new_tiles:
			self.plotTile(tile, self.getColourOfTile(tile))


	def getColourOfTile(self, tile :Tile) -> str:
		'''
		Returns the plotting fill colour based on the @tile attributes.
		@tile ... Tile object for which the colour is being chosen.
		'''
		if tile.altitude >= 0:
			val = str(min(int(numpy.floor(100*tile.altitude)), 79) + 10)
			if len(val) == 1:	val = "0" + val
			return "#00" + val + "00"
		else:
			return "#0022BB"
