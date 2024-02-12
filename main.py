'''

VisuTimer
The Visual Pomodoro Timer based on Raspberry Pi Pico and Badger 2040 W!


Created by: 
@alberto-montemiglio, 2024

'''



'''

Screens:

Pages: 
On start: Start / Edit
While Running: Press any button to -> Start / Stop / Change / Reset
Change Screen: Blink 'WORK' / 'BREAK'. Use arrows to change. Select. Back to Default. Confirm. -> Back to While Running


'''
from picographics import PicoGraphics, DISPLAY_INKY_PACK, PEN_1BIT


# Initiate the 296x128 mono E-ink Badger 2040 W display:


class Screen:
	def __init__(self, font):
		self.display = PicoGraphics(display=DISPLAY_INKY_PACK, pen_type=PEN_1BIT)
		self.WIDTH, self.HEIGHT = display.get_bounds()
		self.display.set_font(bitmap8)
		self.font_height = 8


	def menu(self, menu_items, padding = 4):
		text_y_position = self.HEIGHT-self.font_height+padding
		for index, menu_item in enumerate(menu_items):
			self.display.text(menu_item, (self.WIDTH/3*index), text_y_position)