import tkinter

class WindowHandler:
	'''
	Graphics interface class.
	'''
	def __init__(self):
		self.root = tkinter.Tk()
		self.screen_width = self.root.winfo_screenwidth()
		self.screen_height = self.root.winfo_screenheight()
		self.canvas = tkinter.Canvas(self.root, height=0.5*self.screen_height, width=0.5*self.screen_width)
		self.canvas.pack()

		self.tile_side_length = 50
		self.plotTile(200,150)
		tkinter.mainloop()

	def plotTile(self, x_pos, y_pos):
		'''
		Plot hexagon tile to the WindowHandler's canvas.
		@x_pos: Pixel x position of the hexagon centre.
		@y_pos: Pixel y position of the hexagon centre.
		'''
		points = [	x_pos, y_pos-self.tile_side_length,
					x_pos+0.866*self.tile_side_length, y_pos-0.5*self.tile_side_length,
					x_pos+0.866*self.tile_side_length, y_pos+0.5*self.tile_side_length,
					x_pos, y_pos+self.tile_side_length,
					x_pos-0.866*self.tile_side_length, y_pos+0.5*self.tile_side_length,
					x_pos-0.866*self.tile_side_length, y_pos-0.5*self.tile_side_length]
		self.canvas.create_polygon(points, outline='black', fill='gray', width=2)
		