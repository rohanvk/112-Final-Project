from cmu_graphics import *
from ui import drawRoundedRect
#I wrote roundedrect before this class

class Button:
    def __init__(self, cx, cy, width, height, label, radius=10, fill='white', textSize=20, bold=True, textFill='black'):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.label = label
        self.radius = radius
        self.fill = fill
        self.textSize = textSize
        self.bold = bold
        self.textFill = textFill

    #draw method
    def draw(self):
        x = self.cx - self.width / 2
        y = self.cy - self.height / 2
        drawRoundedRect(x, y, self.width, self.height, self.radius, fill=self.fill)
        drawLabel(self.label, self.cx, self.cy, size=self.textSize, bold=self.bold, fill=self.textFill)
    
    #clicked inside method
    def contains(self, mouseX, mouseY):
        return (self.cx - self.width/2 <= mouseX <= self.cx + self.width/2 and
                self.cy - self.height/2 <= mouseY <= self.cy + self.height/2)
