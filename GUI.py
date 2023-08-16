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
			tile.activate()
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
		tile.gui_id = self.canvas.create_polygon(points, outline='black', fill=background_colour, width=2)

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
		need_new_layer = False

		#go through every tile on the map, which is currently visible on-screen
		for tile in mapObject.tileIterator(active_only=True):
			#move the tile's coordinates
			tile.x += dx
			tile.y += dy
			self.canvas.move(tile.gui_id, dx, dy)

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
			if len(list(tile.getExistingNeighbours())) < 6:
				need_new_layer = True

		#render tiles that are newly visible
		for tile in to_activate:
			#if not tile.gui_active:
				tile.activate()
				self.plotTile(tile, self.getColourOfTile(tile))

		#unrender tiles that are newly off the screen
		for tile in to_deactivate:
			#if tile.gui_active:
			tile.deactivate()
			self.hideTile(tile)
		
		#make the map larger if necessary
		if need_new_layer:	
			new_tiles = mapObject.generateNecessaryLayers(self, mapObject.centre_tile.iterator_state)
			
			#make the terrain smoother
			for _ in range(4):	mapObject.updateSandpiles(new_tiles)


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
