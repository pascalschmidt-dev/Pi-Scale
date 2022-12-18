## Pi-Scale

In 2017 I got interested in automatically tracking my body weight online. By that time, so-called smart bathroom scales were readily available. However, I didn't see myself buying a pretty expensive smart scale only to know the manufacturer selling my data to some health insurance company. So I implemented my own smart scale named _Pi-Scale_.

### Hardware

I already had an unused Raspberry Pi with a [2.8" touch panel](https://shop.watterott.com/RPi-Display-B-28-Touch-Display-for-Raspberry-Pi-1-A-B-Pi2-Pi3) and a matching [enclosure](https://shop.watterott.com/TEK-BERRY3-Enclosure-black-with-Cutout-for-RPi-Display) so I decided to go from there.

For the actual scale, I used a cheap ordinary bathroom scale and removed the the PCB with the LCD display. I learned that the [HX711](http://en.aviaic.com/detail/730856.html) ADC was the right choice to read the Wheatstone bridge load cell of such scales.

However, the HX711 output is a customized serial interface. I quickly noticed that bit banging this protocol from an ordinary Linux process on the RPi wouldn't work well. Therefore I opted for the [SparkFun OpenScale](https://www.sparkfun.com/products/13261). This board combines the HX711 with an [ATmega328P](https://www.microchip.com/en-us/product/ATmega328P) uC, which is preprogrammed to provide a simple terminal type command interface. The board uses USB both for power supply and data I/O with an [FT231XS](https://ftdichip.com/products/ft231xs/) USB/serial bridge.

I placed the OpenScale inside the batchroom scale where the original PCB had been. A 5 ft USB cable was connected to the RPi which served as an easy to read and operate remote control unit.

### Software

I wrote the RPi software in Python using [Pygame](https://www.pygame.org/).

When the user wakes up the RPi display with a touch, the load cell is calibrated. To bridge the time necessary to do so, an animation is displayed. Then the user identifies himself either as _Guest_ or _Pascal_. The former makes Pi-Scale work just like an ordinary scale while the latter asks for a PIN before invoking the smart scale feature.

After the weighing process, the result is send to an [IFTTT Webhook](https://ifttt.com/maker_webhooks). The IFTTT Applet triggered by that Webhook adds a new row with the weight and the date to a Google Sheets spreadsheet . Additionally a graph with the last 10 weigh-ins is drawn on the RPi display.

### Demo

The [demo](https://github.com/pascalschmidt-dev/Pi-Scale/raw/main/demo.mp4) video shows on the lower right the actual RPi display. On the left, you see the terminal output of the OpenScale board, which is normally invisible.

The demo starts with the initial boot sequence. Then a complete weighing process as described above is shown. Finally the camera moves to the Google Sheets spreadsheet that already shows the new row just added.

<video width="320" height="240" controls><source src="https://github.com/pascalschmidt-dev/Pi-Scale/raw/main/demo.mp4" type="video/mp4"></video>
