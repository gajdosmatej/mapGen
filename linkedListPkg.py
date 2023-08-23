class Node:
	'''
	Class representing node of LinkedList class. 
	'''

	def __init__(self, value = None):
		'''
		Constructor of Node class.
		@value ... Value to be stored in this node.
		'''

		self.value = value
		self.previous = None
		self.next = None



class LinkedList:
	'''
	Class representing two-directional linked list with start, middle and end pointer.
	'''

	def __init__(self, values :list):
		'''
		Constructor of LinkedList class.
		@value (list) ... Values to be stored in this object. 
		'''

		self.start = None
		self.middle = None
		self.end = None

		#each append adds +1, each prepend adds -1
		#value +2 or -2 means that the middle tile has to be accordingly shifted
		self.middle_counter = 0

		for val in values:
			self.append(val)

	def balance(self):
		'''
		Checks self.middle_counter and accordingly changes self.middle.
		'''

		if self.middle_counter == 2:
			self.middle_counter = 0
			self.middle = self.middle.next

		elif self.middle_counter == -2:
			self.middle_counter = 0
			self.middle = self.middle.previous


	def append(self, value):
		'''
		Adds @value to the end of this linked list.
		'''

		#empty list
		if self.end == None:
			node = Node(value)
			self.start = node
			self.end = node
			self.middle = node
		else:
			node = Node(value)
			self.end.next = node
			node.previous = self.end
			self.end = self.end.next
			self.middle_counter += 1
			self.balance()


	def prepend(self, value):
		'''
		Adds @value to the start of this linked list.
		'''

		#empty list
		if self.start == None:
			node = Node(value)
			self.start = node
			self.end = node
			self.middle = node
		else:
			node = Node(value)
			node.next = self.start
			self.start.previous = node
			self.start = node
			self.middle_counter -= 1
			self.balance()
	

	def popleft(self):
		'''
		Removes start value end returns it.
		'''

		if self.start == None:
			return None
		
		node = self.start
		self.start = node.next
		self.middle_counter += 1
		self.balance()

		return node.value


	def popright(self):
		'''
		Removes end value end returns it.
		'''
		
		if self.end == None:
			return None

		node = self.end
		self.end = node.previous
		self.middle_counter -= 1
		self.balance()

		return node.value


	def iterator(self):
		'''
		Iterator over this list.
		'''

		pointer = self.start
		while pointer != None:
			yield pointer.value
			pointer = pointer.next
