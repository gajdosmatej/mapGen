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
		mapObj.generate(self)

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
		self.canvas.create_polygon(points, outline='black', fill=background_colour, width=2)
		