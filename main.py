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
import badger2040
import jpegdec
from machine import Pin, Timer
from time import sleep_ms


# Initiate the 296x128 mono E-ink Badger 2040 W display:

class visuTimer:
	def __init__(self):

		# Create a badger2040 object from the badger2040 library:
		self.badger = badger2040.Badger2040()
		self.badger.set_update_speed(0)

		# Initialise the display:
		self.display = PicoGraphics(display=DISPLAY_INKY_PACK, pen_type=PEN_1BIT)
		self.WIDTH, self.HEIGHT = self.display.get_bounds()
		self.bottom_bar_height = 4*self.font_height
		self.top_bar_height = self.HEIGHT - self.bottom_bar_height
		self.screen_displayed = 'home'


		# Initialise Font
		self.display.set_font('bitmap8')
		self.font_height = 8

		# Initialise Buzzer Pin
		self.buzzer_Pin = Pin(28, Pin.OUT)    # create output pin on GPIO28 (Which is free)
	
		# Define timer parameters
		self.work_period = 25*60 # duration of work session in [s]
		self.break_period = 5*60 # duration of break session in [s]
		self.update_period = 10 # Screen update period in [s]
		
		button_map_function = {
			'home': {
				'butt_A': 'runTimer',
				'butt_B': '',
				'butt_C': ''
				},
			'run': 	{
				'butt_A': 'pauseScreen',
				'butt_B': 'pauseScreen',
				'butt_C': 'pauseScreen'},
			'pause': {
				'butt_A': 'home',
				'butt_B': 'continue',
				'butt_C': ''},
		}

		# Interrupts:
	# 	button_A = Pin(badger2040.BUTTON_A,Pin.IN,Pin.PULL_UP)

	# 	Pin.irq(handler=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)
		
	# 	button_A.irq(handler=None, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

	# def __button_A(self):
	# 	self.UI_map[self.screen_displayed][button_A]
		
	# 	'''
		# if screen_displayed = home 
		# UI_map = {
		# 	home: {button_A: 'start', '', ''],
		# 	pause: ['Restart', 'Continue', '']
		# 	running: ['pause', 'pause', 'pause']
		# }

		# '''
	def __drawProgressBar(self, start, width):
		
		# Draw a background white rectangle
		self.display.set_pen(15) # White pen
		self.display.rectangle(0, 0, self.WIDTH, self.top_bar_height)

		# Draw the progress bar: 
		self.display.set_pen(0) # Black pen
		self.display.rectangle(start, 0, width, self.top_bar_height)
		
		# Update Screen
		self.badger.set_update_speed(3)
		self.badger.partial_update(0, 0, self.WIDTH, self.top_bar_height)
		self.badger.set_update_speed(0)

	def ringTimer(self):
		for i in range(5):
			self.buzzer_Pin.on()
			self.badger.LED.on()
			sleep_ms(500)
			self.buzzer_Pin.off()
			self.badger.LED.off()
			sleep_ms(100)


	def __increaseTimer(self):


		if not self.timer_stop_flag: # Run the following only if the timer has not been paused
			self.time_elapsed = self.time_elapsed + self.update_period
			if self.current_session == 'break':
				if self.time_elapsed < self.break_period:
					progress_bar_width = round(self.WIDTH*self.time_elapsed/self.work_period)
					__drawProgressBar(start = self.WIDTH - progress_bar_width, width = progress_bar_width)
				else: 
					ringTimer()
					self.current_session == 'work'
			else: 
				if self.time_elapsed < self.work_period:
					progress_bar_width = round(self.WIDTH*self.time_elapsed/self.work_period)
					__drawProgressBar(start = 0, width = progress_bar_width)
				else: 
					ringTimer()
					self.current_session == 'break'



	def startTimer(self):
		# Show Timer Page
		# drawPomodoroScreen()

		# Start Timer
		self.time_elapsed = 0 # Minutes Passed
		self.tim = Timer().init( period=100000, callback=__increaseTimer() ) # Update Timer every 10 sec

	def stopTimer(self):
		self.timer_stop_flag = 1

	def continueTimer(self):
		self.timer_stop_flag = 1

	def endTimer(self):
		self.tim.deinit()

	




	def __draw_menu(self, menu_items):
		buttons_x_pos = [40, 148, 256] # Buttons positions wrt the screen [px]
		text_y_position = self.HEIGHT-2*self.font_height 
		text_x_position = [buttons_x_pos[i]-round(self.display.measure_text(menu_items[i])/2) for i in range(len(menu_items))]

		self.display.set_pen(0)
		for index, menu_item in enumerate(menu_items):
			self.display.text(menu_item, text_x_position[index], text_y_position)

	def __draw_logo(self):
		# TODO: change this to an actual logo
		self.display.text("VisuTimer", 10, 10, scale=2)

	def __draw_pomodoro_instruction(self, instruction):
		# Draw a black rectangle on the bottom of the screen
		self.display.set_pen(0)
		self.display.rectangle(0, self.HEIGHT - self.bottom_bar_height, self.WIDTH, self.bottom_bar_height)

		# Write the Instruction in white
		instruction_width = self.display.measure_text(instruction)
		text_y_position = self.HEIGHT-3*self.font_height
		text_x_position = round(self.WIDTH/2)-round(instruction_width/2)
		
		self.display.set_pen(15)
		self.display.text(instruction, text_x_position, text_y_position, scale = 2)

		# Revert to black pen
		# self.display.set_pen(0)


	def clear_screen(self):
		self.display.set_pen(15)
		self.display.clear()
		self.display.set_pen(0)

	def draw_screen(self, *elements_to_draw):
		self.clear_screen()
		for element in elements_to_draw:
			element()
		self.display.update()

	def display_home_screen(self):
		self.clear_screen()
		self.__draw_logo()
		self.__draw_menu(['Start', '', ''])
		self.display.update()


	def display_pause_screen(self):
		self.clear_screen()		
		self.__draw_logo()
		self.__draw_menu(['Restart', 'Continue', ''])
		self.display.update()

	def display_pomodoro_screen(self, instruction):
		self.clear_screen()
		self.__draw_pomodoro_instruction(instruction)
		self.display.update()


	def increase_timer(self):
		self.timer_position += 1

		self.display.set_pen(0) # Set pen back to black
		self.display.rectangle(0, 0, self.timer_position, self.top_bar_height)
		
		self.badger.set_update_speed(3)
		# self.badger.partial_update(self.timer_position-1, 0, 1, self.top_bar_height)
		self.display.set_pen(15) # Set pen to white
		self.badger.partial_update(0, 0, self.timer_position, self.top_bar_height)
		
		# self.badger.update()
		# self.display.update()

		self.badger.set_update_speed(0)


	def decrease_timer(self):
		self.timer_position -= 1
		self.display.set_pen(15) # Set pen to white
		self.display.line(self.timer_position, 0, self.timer_position, self.HEIGHT - self.bottom_bar_height)
		self.display.update()
		self.display.set_pen(0) # Set pen back to black

	def clear_screen(self):
		self.display.set_pen(15)
		self.display.clear()
		self.display.set_pen(0)


def main(): 

visuTimer = visuTimer()

