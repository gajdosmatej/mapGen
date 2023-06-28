import tkinter

class WindowHandler:
	'''Graphics interface class.'''
	def __init__(self):
		self.root = tkinter.Tk()
		self.screen_width = self.root.winfo_screenwidth()
		self.screen_height = self.root.winfo_screenheight()

		self.canvas = tkinter.Canvas(self.root, height=0.5*self.screen_height, width=0.5*self.screen_width)
		self.canvas.pack()
		tkinter.mainloop()