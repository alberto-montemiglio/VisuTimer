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
from picographics import PicoGraphics, DISPLAY_INKY_PACK, PEN_1BIT, bitmap8
import jpegdec


# Initiate the 296x128 mono E-ink Badger 2040 W display:

class Screen:
	def __init__(self, bottom_bar_height = 20):
		self.display = PicoGraphics(display=DISPLAY_INKY_PACK, pen_type=PEN_1BIT)
		self.WIDTH, self.HEIGHT = self.display.get_bounds()
		self.display.set_font(bitmap8)
		self.font_height = 8
		self.timer_position = 0
		self.bottom_bar_height = bottom_bar_height

	def __display_menu(self, menu_items, padding = 4):
		text_y_position = self.HEIGHT-self.font_height+padding
		
		for index, menu_item in enumerate(menu_items):
			self.display.text(menu_item, (self.WIDTH/3*index), text_y_position)

	def __display_logo(self):
		# TODO: change this to an actual logo
		self.display.text("VisuTimer", 10, 10, scale=2)

	def __display_pomodoro_instruction(self, instruction, padding=4):
		# Draw a black background
		self.display.set_pen(0)
		self.display.rectangle(0, self.HEIGHT - self.bottom_bar_height, self.WIDTH, self.bottom_bar_height)

		# Write the Instruction in white
		self.display.set_pen(15)
		instruction_width = self.display.measure_text(instruction)
		text_y_position = self.HEIGHT-self.font_height*2+padding

		self.display.text(instruction, self.HEIGHT/2-instruction_width/2, text_y_position, scale = 2)

	def display_home_screen(self):
		self.__display_logo()
		self.__display_menu(['Start', '', ''])

	def display_pause_screen(self):
		self.__display_logo()
		self.__display_menu(['Restart', 'Continue', ''])

	def display_pomodoro_screen(self):
		self.__display_pomodoro_instruction()

	def increase_timer(self):
		self.timer_position += 1
		self.display.line(self.timer_position, 0, self.timer_position, self.HEIGHT - self.bottom_bar_height)

	def decrease_timer(self):
		self.timer_position -= 1
		self.display.line(self.timer_position, 0, self.timer_position, self.HEIGHT - self.bottom_bar_height)

	def clear(self):
		self.display.clear()


home = Screen()

