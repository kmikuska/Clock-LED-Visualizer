#!/usr/bin/env python3
"""
Neopixel LED Clock
Displays an analog clock on a circular neopixel LED strip

Hardware Requirements:
- Raspberry Pi
- WS2812B/WS2811 Neopixel LED strip (120 LEDs)
- GPIO Pin 13 (PWM1) connected to LED strip data pin
- Appropriate power supply for LED strip

Usage:
    python3 neopixel_clock.py [options]

Options:
    --led-count NUM     Number of LEDs in the strip (default: 120)
    --gpio-pin NUM      GPIO pin number (default: 13)
    --brightness NUM    Brightness 0-100 (default: 50)
    --no-smooth         Disable smooth hand movement
"""

import sys
import argparse
import logging
import signal
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import rpi_ws281x
try:
    from rpi_ws281x import PixelStrip, ws
    HAS_HARDWARE = True
except ImportError:
    logger.warning("rpi_ws281x not found. Running in simulation mode.")
    HAS_HARDWARE = False
    # Create mock classes for development/testing
    class PixelStrip:
        def __init__(self, *args, **kwargs):
            self.num_pixels = args[0] if args else 120
            logger.info(f"Mock PixelStrip created with {self.num_pixels} LEDs")
        def begin(self):
            pass
        def setPixelColor(self, n, color):
            pass
        def show(self):
            pass
        def setBrightness(self, brightness):
            pass

    class ws:
        WS2811_STRIP_GRB = 0


class SimpleLedStrip:
    """
    Simplified LED strip wrapper for clock application
    """

    def __init__(self, led_count, gpio_pin, brightness=50):
        """
        Initialize LED strip

        Args:
            led_count: Number of LEDs
            gpio_pin: GPIO pin number
            brightness: Brightness 0-100
        """
        self.led_count = led_count
        self.gpio_pin = gpio_pin
        self.brightness = brightness

        # LED strip configuration
        LED_FREQ_HZ = 800000    # LED signal frequency (800kHz)
        LED_DMA = 10            # DMA channel
        LED_INVERT = False      # Don't invert signal
        LED_CHANNEL = 0         # PWM channel (0 for GPIO 12/18, 1 for GPIO 13/19)

        # Use channel 1 for GPIO 13
        if gpio_pin == 13 or gpio_pin == 19:
            LED_CHANNEL = 1

        logger.info(f"Initializing LED strip: {led_count} LEDs on GPIO {gpio_pin} (Channel {LED_CHANNEL})")

        # Create PixelStrip object
        self.strip = PixelStrip(
            led_count,
            gpio_pin,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            brightness,
            LED_CHANNEL,
            ws.WS2811_STRIP_GRB
        )

        # Initialize the library
        self.strip.begin()
        logger.info("LED strip initialized successfully")

    def set_pixel(self, position, r, g, b):
        """Set a single pixel color"""
        if 0 <= position < self.led_count:
            color = (r << 16) | (g << 8) | b
            self.strip.setPixelColor(position, color)

    def clear_all(self):
        """Clear all LEDs"""
        for i in range(self.led_count):
            self.strip.setPixelColor(i, 0)

    def show(self):
        """Update the LED strip"""
        self.strip.show()

    def set_brightness(self, brightness):
        """Set brightness (0-100)"""
        self.brightness = max(0, min(100, brightness))
        brightness_value = int((self.brightness / 100.0) * 255)
        self.strip.setBrightness(brightness_value)


# Import our clock module
try:
    from lib.led_clock import LedClock
except ImportError:
    logger.error("Could not import led_clock module. Make sure lib/led_clock.py exists.")
    sys.exit(1)

# Try to import UserSettings for color configuration
try:
    from lib.usersettings import UserSettings
    HAS_USER_SETTINGS = True
except ImportError:
    logger.info("UserSettings not available. Using default clock colors.")
    HAS_USER_SETTINGS = False
    UserSettings = None


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Neopixel LED Clock - Display analog clock on LED strip',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 neopixel_clock.py                           # Use defaults (120 LEDs, GPIO 13)
  python3 neopixel_clock.py --led-count 60            # Use 60 LEDs
  python3 neopixel_clock.py --gpio-pin 12             # Use GPIO 12
  python3 neopixel_clock.py --brightness 75           # Set brightness to 75%
        """
    )

    parser.add_argument(
        '--led-count',
        type=int,
        default=120,
        help='Number of LEDs in the strip (default: 120)'
    )

    parser.add_argument(
        '--gpio-pin',
        type=int,
        default=13,
        help='GPIO pin number (default: 13, PWM-capable pins: 12, 13, 18, 19)'
    )

    parser.add_argument(
        '--brightness',
        type=int,
        default=50,
        help='Brightness percentage 0-100 (default: 50)'
    )

    parser.add_argument(
        '--no-smooth',
        action='store_true',
        help='Disable smooth hand movement'
    )

    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()

    # Validate GPIO pin
    valid_gpio_pins = [12, 13, 18, 19]
    if args.gpio_pin not in valid_gpio_pins:
        logger.warning(f"GPIO {args.gpio_pin} may not support PWM. Valid pins: {valid_gpio_pins}")

    # Validate brightness
    if not 0 <= args.brightness <= 100:
        logger.error("Brightness must be between 0 and 100")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Neopixel LED Clock")
    logger.info("=" * 60)
    logger.info(f"LED Count: {args.led_count}")
    logger.info(f"GPIO Pin: {args.gpio_pin}")
    logger.info(f"Brightness: {args.brightness}%")
    logger.info(f"Smooth movement: {not args.no_smooth}")
    logger.info("=" * 60)

    try:
        # Try to load user settings for clock colors
        usersettings = None
        if HAS_USER_SETTINGS:
            try:
                usersettings = UserSettings()
                logger.info("Loaded user settings for clock colors")
            except Exception as e:
                logger.warning(f"Could not load user settings: {e}")

        # Initialize LED strip
        led_strip = SimpleLedStrip(
            led_count=args.led_count,
            gpio_pin=args.gpio_pin,
            brightness=args.brightness
        )

        # Initialize clock with optional user settings
        clock = LedClock(led_strip, led_count=args.led_count, usersettings=usersettings)

        # Optional: Customize clock colors
        # clock.set_colors(
        #     hour_color=(255, 0, 0),      # Red
        #     minute_color=(0, 255, 0),    # Green
        #     second_color=(0, 0, 255)     # Blue
        # )

        # Setup signal handler for clean shutdown
        def signal_handler(sig, frame):
            logger.info("Shutdown signal received")
            clock.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run the clock
        logger.info("Starting clock... (Press Ctrl+C to exit)")
        clock.run(update_interval=0.05 if not args.no_smooth else 1.0)

    except Exception as e:
        logger.error(f"Error running clock: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
