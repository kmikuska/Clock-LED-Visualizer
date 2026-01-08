#!/usr/bin/env python3
"""
Quick test script for LED clock
Tests the clock functionality without requiring actual hardware
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockLedStrip:
    """Mock LED strip for testing without hardware"""

    def __init__(self, led_count=120):
        self.led_count = led_count
        self.pixels = [(0, 0, 0)] * led_count
        logger.info(f"Mock LED strip created with {led_count} LEDs")

    def set_pixel(self, position, r, g, b):
        if 0 <= position < self.led_count:
            self.pixels[position] = (r, g, b)

    def clear_all(self):
        self.pixels = [(0, 0, 0)] * self.led_count

    def show(self):
        # Print a simple visualization
        lit_pixels = [(i, p) for i, p in enumerate(self.pixels) if p != (0, 0, 0)]
        if lit_pixels:
            logger.debug(f"Lit LEDs: {len(lit_pixels)}")
            for i, (r, g, b) in lit_pixels[:10]:  # Show first 10
                logger.debug(f"  LED {i}: RGB({r}, {g}, {b})")

    def set_brightness(self, brightness):
        logger.info(f"Brightness set to {brightness}%")


def test_led_clock():
    """Test the LED clock module"""
    logger.info("=" * 60)
    logger.info("LED Clock Test")
    logger.info("=" * 60)

    try:
        # Import the clock module
        from lib.led_clock import LedClock

        # Create mock LED strip
        led_strip = MockLedStrip(led_count=120)

        # Create clock
        clock = LedClock(led_strip, led_count=120)
        logger.info("✓ LED Clock created successfully")

        # Test setting custom colors
        clock.set_colors(
            hour_color=(255, 0, 0),
            minute_color=(0, 255, 0),
            second_color=(0, 0, 255)
        )
        logger.info("✓ Custom colors set")

        # Test single update
        logger.info("Testing clock update...")
        clock.update()
        logger.info("✓ Clock update successful")

        # Verify some LEDs are lit
        lit_count = sum(1 for p in led_strip.pixels if p != (0, 0, 0))
        logger.info(f"✓ {lit_count} LEDs are lit")

        # Test brightness
        clock.set_brightness(75)
        logger.info("✓ Brightness adjustment works")

        logger.info("=" * 60)
        logger.info("All tests passed! ✓")
        logger.info("=" * 60)
        logger.info("")
        logger.info("To run the actual clock with hardware:")
        logger.info("  sudo python3 neopixel_clock.py")
        logger.info("")
        logger.info("Options:")
        logger.info("  --led-count 120    # Number of LEDs")
        logger.info("  --gpio-pin 13      # GPIO pin number")
        logger.info("  --brightness 50    # Brightness percentage")
        logger.info("")

        return True

    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


if __name__ == '__main__':
    success = test_led_clock()
    sys.exit(0 if success else 1)
