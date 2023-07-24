import tkinter
import map

class WindowHandler:
	'''
	Graphics interface class.
	'''
	def __init__(self):
		self.root = tkinter.Tk()
		self.screen_width = self.root.winfo_screenwidth()
		self.screen_height = self.root.winfo_screenheight()
		self.canv_width = self.screen_width // 2
		self.canv_height = self.screen_height // 2
		self.canvas = tkinter.Canvas(self.root, height=self.canv_height, width=self.canv_width)
		self.canvas.pack()

		self.tile_side_length = 50
		#self.plotTile(200,150, "#006611")
		
		mapObj = map.Map(self.screen_width//4, self.screen_height//4)
		mapObj.generateGraph(self)

		self.root.bind("<KeyPress-w>", lambda event, gui=self: gui.moveMap(mapObj, 0, 10))
		self.root.bind("<KeyPress-a>", lambda event, gui=self: gui.moveMap(mapObj, 10, 0))
		self.root.bind("<KeyPress-s>", lambda event, gui=self: gui.moveMap(mapObj, 0, -10))
		self.root.bind("<KeyPress-d>", lambda event, gui=self: gui.moveMap(mapObj, -10, 0))

		tkinter.mainloop()

	def plotTile(self, x_pos, y_pos, background_colour):
		'''
		Plot hexagon tile to the WindowHandler's canvas.
		@x_pos: Pixel x position of the hexagon centre.
		@y_pos: Pixel y position of the hexagon centre.
		@background_colour: Fill colour of the tile.
		'''
		points = [	x_pos, y_pos-self.tile_side_length,
					x_pos+0.866*self.tile_side_length, y_pos-0.5*self.tile_side_length,
					x_pos+0.866*self.tile_side_length, y_pos+0.5*self.tile_side_length,
					x_pos, y_pos+self.tile_side_length,
					x_pos-0.866*self.tile_side_length, y_pos+0.5*self.tile_side_length,
					x_pos-0.866*self.tile_side_length, y_pos-0.5*self.tile_side_length]
		return self.canvas.create_polygon(points, outline='black', fill=background_colour, width=2)
	
	def moveMap(self, mapObject, dx, dy):
		leftmost_tiles, rightmost_tiles, upmost_tiles, downmost_tiles = [], [], [], []

		for tile in mapObject.tileIterator():
			self.canvas.move(tile.gui_id, dx, dy)
			tile.x += dx
			tile.y += dy

			if tile.w == None:	leftmost_tiles.append(tile)
			if tile.e == None:	rightmost_tiles.append(tile)
			if tile.nw == None and tile.ne == None:	upmost_tiles.append(tile)
			if tile.sw == None and tile.se == None:	downmost_tiles.append(tile)
		
		for tile in leftmost_tiles:
			if tile.x > 0:
				new_tile = map.Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 2*0.866*self.tile_side_length
				new_tile.y = tile.y
				new_tile.gui_id = self.plotTile(new_tile.x, new_tile.y, "#FF0000")

				tile.w = new_tile
				new_tile.e = tile
				if tile.nw != None:
					tile.nw.sw = new_tile
					new_tile.ne = tile.nw
				if tile.sw != None:
					tile.sw.nw = new_tile
					new_tile.se = tile.sw

		for tile in rightmost_tiles:
			if tile.x < self.canv_width:
				new_tile = map.Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x + 2*0.866*self.tile_side_length
				new_tile.y = tile.y
				new_tile.gui_id = self.plotTile(new_tile.x, new_tile.y, "#FF0000")
				
				tile.e = new_tile
				new_tile.w = tile
				if tile.ne != None:
					tile.ne.se = new_tile
					new_tile.nw = tile.ne
				if tile.se != None:
					tile.se.ne = new_tile
					new_tile.sw = tile.se 

		for tile in upmost_tiles:
			if tile.y > 0:
				new_tile = map.Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 0.866*self.tile_side_length
				new_tile.y = tile.y - 1.5*self.tile_side_length
				new_tile.gui_id = self.plotTile(new_tile.x, new_tile.y, "#FF0000")

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

		for tile in downmost_tiles:
			if tile.y < self.canv_height:
				new_tile = map.Tile(iterator_state = tile.iterator_state)
				new_tile.x = tile.x - 0.866*self.tile_side_length
				new_tile.y = tile.y + 1.5*self.tile_side_length
				new_tile.gui_id = self.plotTile(new_tile.x, new_tile.y, "#FF0000")

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