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
import micropython

# Initiate the 296x128 mono E-ink Badger 2040 W display:

class visuTimer:

	def __drawProgressBar(self, start, width):

		# Speed up screen updating
		self.badger.set_update_speed(3)
		
		# Draw a background white rectangle
		self.display.set_pen(15) # White pen
		self.display.rectangle(0, 0, self.WIDTH, self.top_bar_height)

		# Draw the progress bar: 
		self.display.set_pen(0) # Black pen
		self.display.rectangle(start, 0, width, self.top_bar_height)
		
		# Update Screen
		self.display.update()
		
		# Revert to normal update speed
		self.badger.set_update_speed(0)



	def ringTimer(self):
		for i in range(5):
			self.buzzer_Pin.on()
			self.ledPin.on()
			sleep_ms(500)
			self.buzzer_Pin.off()
			self.ledPin.off()
			sleep_ms(100)


	def __increaseTimer(self, timer):
		if not self.timer_stop_flag: # Run the following only if the timer has not been paused
			self.time_elapsed = self.time_elapsed + self.update_period
			if self.current_session == 'BREAK':
				progress_bar_width = round(self.WIDTH*self.time_elapsed/self.work_period)
				self.__drawProgressBar(start = self.WIDTH - progress_bar_width, width = progress_bar_width)
				if self.time_elapsed >= self.break_period:
					self.ringTimer()
					self.current_session = 'WORK'
					self.display_pomodoro_screen(self.current_session)
					self.time_elapsed = 0
			else: 
				progress_bar_width = round(self.WIDTH*self.time_elapsed/self.work_period)
				self.__drawProgressBar(start = 0, width = progress_bar_width)
				if self.time_elapsed >= self.work_period:
					self.ringTimer()
					self.current_session = 'BREAK'
					self.display_pomodoro_screen(self.current_session)
					self.time_elapsed = 0



	def startTimer(self):

		self.current_screen = 'run'

		# Show Timer Page
		self.display_pomodoro_screen(self.current_session)

		# Start Timer
		self.time_elapsed = 0 # Minutes Passed
		self.tim = Timer()
		self.tim.init( period=self.update_period*1000, callback=self.__increaseTimer ) # Update Timer every 10 sec

	def pauseTimer(self):

		self.current_screen = 'pause'
		self.display_pause_screen()
		self.timer_stop_flag = 1

	def continueTimer(self):

		self.current_screen = 'run'
		self.display_pomodoro_screen(self.current_session)
		self.timer_stop_flag = 0

	def endTimer(self):

		self.current_screen = 'home'
		self.display_home_screen()
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
		self.__draw_menu(['End Timer', 'Continue', ''])
		self.display.update()

	def display_pomodoro_screen(self, instruction):
		self.clear_screen()
		# Draw a black rectangle on the bottom of the screen
		self.display.set_pen(0)
		self.display.rectangle(0, self.HEIGHT - self.bottom_bar_height, self.WIDTH, self.bottom_bar_height)

		# Write the Instruction in white
		instruction_width = self.display.measure_text(instruction)
		text_y_position = self.HEIGHT-3*self.font_height
		text_x_position = round(self.WIDTH/2)-round(instruction_width/2)
		
		self.display.set_pen(15)
		self.display.text(instruction, text_x_position, text_y_position, scale = 2)

		self.display.update()

	def button_A_ISR(self, buttonInterrupt):
		if self.current_screen == 'home': self.startTimer()
		elif self.current_screen == 'run': self.pauseTimer()
		elif self.current_screen == 'pause': self.endTimer()
		else: pass

	def button_B_ISR(self, buttonInterrupt):
		if self.current_screen == 'home': pass
		elif self.current_screen == 'run': self.pauseTimer()
		elif self.current_screen == 'pause': self.continueTimer()
		else: pass

	def button_C_ISR(self, buttonInterrupt):
		if self.current_screen == 'home': pass
		elif self.current_screen == 'run': self.pauseTimer()
		elif self.current_screen == 'pause': pass
		else: pass


	def __init__(self):

		# Create a badger2040 object from the badger2040 library:
		self.badger = badger2040.Badger2040()
		self.badger.set_update_speed(0)

		# Instantiate PicoGraphics:
		self.display = PicoGraphics(display=DISPLAY_INKY_PACK, pen_type=PEN_1BIT)

		# Initialise Font
		self.display.set_font('bitmap8')
		self.font_height = 8

		# Set Up Display
		self.WIDTH, self.HEIGHT = self.display.get_bounds()
		self.bottom_bar_height = 4*self.font_height
		self.top_bar_height = self.HEIGHT - self.bottom_bar_height
		self.screen_displayed = 'home'




		# Initialise Buzzer Pin
		self.buzzer_Pin = Pin(28, Pin.OUT)    # create output pin on GPIO28 (Which is free)
		self.ledPin = Pin(badger2040.LED, Pin.OUT)	# create output pin on GPIO22 (Which has the LED)

		# Define timer parameters
		self.work_period = 10 # duration of work session in [s]
		self.break_period = 10 # duration of break session in [s]
		self.update_period = 4 # Screen update period in [s]
		self.timer_stop_flag = 0 # Set timer to active
		self.current_session = 'WORK' # Start with a work session

		self.current_screen = 'home'

		# self.button_map_function = {
		# 	'home': {
		# 		'butt_A': self.startTimer,
		# 		'butt_B': lambda *args, **kwargs: None,
		# 		'butt_C': lambda *args, **kwargs: None
		# 		},
		# 	'run': 	{
		# 		'butt_A': self.pauseTimer,
		# 		'butt_B': self.pauseTimer,
		# 		'butt_C': self.pauseTimer
		# 		},
		# 	'pause': {
		# 		'butt_A': self.endTimer,
		# 		'butt_B': self.continueTimer,
		# 		'butt_C': lambda *args, **kwargs: None
		# 		},
		# }

		# def buttonA_ISR(self):

		# Interrupts:
		self.button_A = Pin(badger2040.BUTTON_A,Pin.IN,Pin.PULL_DOWN)		
		self.button_A.irq(handler=self.button_A_ISR, trigger=Pin.IRQ_RISING)

		# self.button_A = Pin(badger2040.BUTTON_A,Pin.IN,Pin.PULL_DOWN)		
		# self.button_A.irq(handler=self.startTimer, trigger=Pin.IRQ_RISING)

		self.button_B = Pin(badger2040.BUTTON_B,Pin.IN,Pin.PULL_DOWN)		
		self.button_B.irq(handler=self.button_B_ISR, trigger=Pin.IRQ_RISING)

		self.button_C = Pin(badger2040.BUTTON_C,Pin.IN,Pin.PULL_DOWN)		
		self.button_C.irq(handler=self.button_C_ISR, trigger=Pin.IRQ_RISING)



micropython.alloc_emergency_exception_buf(100)
visuTimer = visuTimer()
visuTimer.display_home_screen()
# visuTimer.startTimer()
