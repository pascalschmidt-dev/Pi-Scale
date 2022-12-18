#!/usr/bin/python

pin = 7674

import os, pygame, re, serial, sys, time, urllib, datetime

os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDEV', '/dev/input/event0')
os.putenv('SDL_MOUSEDRV', 'TSLIB')

sh = 240
sw = 320
start_time = 0
last_times = []
last_weights = []
rects = []

white = pygame.Color('white')
black = pygame.Color('black')
green = pygame.Color('green')
blue = pygame.Color('blue')
red = pygame.Color('red')
yellow = pygame.Color('yellow')
purple = pygame.Color('purple')
orange = pygame.Color('orange')
light_grey = pygame.Color('light grey')
grey = pygame.Color(160, 160, 160)
	
def start_timeout():
	global start_time
	start_time = time.time()
	
def check_timeout(duration):
	global start_time
	return start_time + duration > time.time()
	
def backlight(on_off):
	value = ['1', '0']
	dev = open('/sys/class/backlight/fb_ili9341/bl_power', 'w')
	dev.write(value[on_off])
	dev.close
	
def read_regex(regex):
	mo = None
	str = ''
	while not mo:
		str = str + ser.read(1000)
		mo = re.search(regex, str)
	print(str)
	return mo.group(1)

def write_delay(cmd):
	time.sleep(0.1)
	ser.write(cmd)

def read_weight():
	write_delay(b'0')
	return read_regex('-?([0-9]+.[0-9]),kg,')
	
def start_calib():
	write_delay(b'x')
	read_regex('(>)')
	write_delay(b'1')

def end_calib():
	read_regex('(>)')
	write_delay(b'x')

def reset_display():
	backlight(False)
	lcd.fill(black)
	pygame.display.update()

def blit_text(word, x, y, color, fonts):
	word = fonts.render(word, True, color)
	word_rect = word.get_rect(center=(x,y))
	lcd.blit(word, word_rect)
	
	
def show_weight(weight, color, fontes):
	lcd.fill(black)
	blit_text(weight, sw/2, sh/2, color, fontes)
	pygame.display.update()

def get_weight():
	equal = 0
	last_weight = 0
	start_timeout()
	while equal < 2 and check_timeout(10):
		print start_time
		current_weight = read_weight()
		if last_weight == current_weight and len(current_weight) > 3:
			equal = equal + 1
		else:
			equal = 0
		last_weight = current_weight
		show_weight(current_weight, red, font_big)
		if len(current_weight) > 3:
			start_timeout()
	if equal == 2:
		show_weight(current_weight, green, font_big)
		time.sleep(3)
		return float(current_weight)
	return 0
	
def menu():
	blit_text('Pascal', sw/2, sh/4, green, font) 
	pygame.draw.line(lcd, white, (0, sh/2), (sw, sh/2))
	blit_text('Guest', sw/2, sh/4 * 3, blue, font)
	pygame.display.update()
	start_timeout()
	while check_timeout(10):
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				height = event.pos[1]
				print(height)
				
			elif event.type == pygame.MOUSEBUTTONUP:
				if height <= sh/2:
					print('pascal')
					return 1
				else:
					print('guest')
					return 2

	return 0
					
def color_gradient():
	width = gradient.get_width() - 320
	for i in range(0,width,5):
		lcd.blit(gradient, (0,0), (i, 0, sw, sh))
		lcd.blit(logo,(0, 0))
		pygame.display.update()
		
def pad():
	rects.insert(0, pygame.Rect(sw/4 * 3, 0, sw/4, sh/3 - 1))
	for i in range(1, 10):
		rects.insert(i, pygame.Rect(int((i-1) % 3) * sw/4, int((i-1) / 3) * sh/3, sw / 4 - 1, sh/3 - 1))
	rects.insert(10, pygame.Rect(sw/4 * 3, sh/3, sw/4, sh/3 * 2 - 1))
	
def button(digit, pressed = False):
	fg = [white, black]
	bg = [black, light_grey]
	rect = rects[digit]
	pygame.draw.rect(lcd, bg[pressed], rect)
	if digit < 10:
		number = font.render(str(digit), True, fg[pressed])
		number_rect = number.get_rect(center=(rect.center))
		lcd.blit(number, number_rect)
	else:
		pygame.draw.lines(lcd, fg[pressed], False, ((rect.left + 50, rect.top +  60), (rect.left + 50, rect.top + 100), (rect.left + 30, rect.top + 100)), 5)
		pygame.draw.lines(lcd, fg[pressed], False, ((rect.left + 35, rect.top + 105), (rect.left + 30, rect.top + 100), (rect.left + 35, rect.top +  95)), 5)

def query_pin():
	lcd.fill(grey)
	pygame.draw.line(lcd, black, (0, sh), (sw,sh),3)
	for i in range(11):
		button(i)
	pygame.display.update()
	done = False
	finnish = False
	input = 0
	key = 0
	start_timeout()
	while check_timeout(5) and not done:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN:
				start_timeout()
				for key in range(11):
					if rects[key].collidepoint(event.pos):
						if key < 10:
							input = input * 10 + key

						else:
							done = True
						button(key, True)
						pygame.display.update()
						break
			elif event.type == pygame.MOUSEBUTTONUP:
				button(key)
				pygame.display.update()

	if pin != input:
		lcd.fill(black)
		blit_text('Wrong PIN', sw/2, sh/2, red, font)
		pygame.display.update()
		time.sleep(2)
		lcd.fill(black)
		pygame.display.update()
		return False
	else:
		return True
		
def save(weight):
	if weight > 0:
		last_weights.insert(0,weight)
		last_times.insert(0,time.time())
		if len(last_weights) > 10:
			del last_weights[10]
			del last_times[10]

def graph():
	difference  = 75 - 60
	pixel = sh/5 * 4 / difference
	for i in range(1,len(last_weights)):
		weight_first = last_weights[len(last_weights)-i]
		weight_secound = last_weights[len(last_weights)- 1 -i]
		hight_first = ((75 - weight_first) * int(pixel)) + sh/10
		hight_secound = ((75 - weight_secound) * int(pixel)) + sh/10
		pygame.draw.line(lcd, white, (sw/11 * i, hight_first), (sw/11 * (i+1), hight_secound))
	blit_text('75', sw/22, sh/10, red, font_small)
	blit_text('70', sw/22, sh/10 * 8/3 + sh/10, orange, font_small)
	blit_text('65', sw/22, sh/10 * 16/3 + sh/10, orange, font_small)
	blit_text('60', sw/22, sh/10 * 9, green, font_small)
	pygame.display.update()
	print last_weights
	time.sleep(10)
	
def upload(weight):
	if weight > 0:
		date = time.strftime('%d.%m.%Y')
		weight = str(weight)
		weight_correct = weight[0] + weight[1] + ',' + weight[3]
		url1 = 'https://maker.ifttt.com/trigger/weighing/with/key/csd-N2T14kRxzTr21STWZg' + '?value1=' + weight_correct + '&value2=' + date
		url2 = 'https://maker.ifttt.com/trigger/weight/with/key/csd-N2T14kRxzTr21STWZg'   + '?value1=' + weight_correct
		print url
		urllib.urlopen(url1)
		urllib.urlopen(url2)
	
pygame.init()
lcd = pygame.display.set_mode((sw, sh))
pygame.mouse.set_visible(False)
font = pygame.font.SysFont(None, 50)
font_small = pygame.font.SysFont(None, 20)
font_big = pygame.font.SysFont(None, 150)
backlight(True)

lcd.fill(black)
blit_text('init running', sw/2, sh/2, white, font) 
pygame.display.update()

ser = serial.Serial('/dev/ttyUSB0', timeout = 0) 
ser.setDTR(False)
time.sleep(0.022)
ser.setDTR(True)

logo = pygame.image.load('/home/pi/logo.png').convert_alpha()
gradient = pygame.image.load('/home/pi/gradient.jpg').convert()

read_regex('-?([0-9]+.[0-9]),kg,')
pad()
lcd.fill(black)
blit_text('init complete', sw/2, sh/2, white, font) 
pygame.display.update()
time.sleep(1)

reset_display()
while True:
	time.sleep(0.1)
	for event in pygame.event.get():
		if event.type == pygame.MOUSEBUTTONDOWN:
			down_x = event.pos[0]

		elif event.type == pygame.MOUSEBUTTONUP:
			swipe = down_x - event.pos[0]
			backlight(True)
			
			if abs(swipe) > 100:
				if swipe < 0:
					blit_text('halt', sw/2, sh/2, white, font)
					pygame.display.update()
					os.system('sudo halt')
					sys.exit()
				else:
					blit_text('quit', sw/2, sh/2, white, font)
					pygame.display.update()
					time.sleep(2)
					sys.exit()

			else:
				start_calib()
				color_gradient()
				end_calib()
				done = False
				while not done:
					mode = menu()
					if mode == 1:
						lcd.fill(black)
						if query_pin():
							weight = get_weight()
							lcd.fill(black)
							save(weight)
							for event in pygame.event.get():
								if event.type == pygame.MOUSEBUTTONUP:
									upload(weight)
									graph()
							done = True
					elif mode  == 2:
						get_weight()
						done = True
					else:
						done = True

				reset_display()
					
				