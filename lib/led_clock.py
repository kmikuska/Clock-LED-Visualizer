"""
LED Clock Animation Module
Creates an analog-style clock display on a circular neopixel LED strip
"""

import time
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


class LedClock:
    """
    Analog clock display on a circular LED strip

    Design for 120 LEDs:
    - LEDs arranged in a circle (LED 0 at bottom, 6 o'clock position)
    - Hour hand: Red
    - Minute hand: Green
    - Second hand: Blue
    - Hour markers: Dim white at 12, 3, 6, 9 positions
    """

    def __init__(self, led_strip, led_count=120, usersettings=None):
        """
        Initialize LED clock

        Args:
            led_strip: LedStrip object from ledstrip.py
            led_count: Number of LEDs in the strip (default 120)
            usersettings: Optional UserSettings object to load colors from config
        """
        self.strip = led_strip
        self.led_count = led_count
        self.running = False
        self.usersettings = usersettings

        # Clock hand lengths (in number of LEDs from center)
        self.hour_hand_length = 5
        self.minute_hand_length = 8
        self.second_hand_length = 10

        # Clock hand colors (R, G, B) - defaults
        self.hour_color = (255, 0, 0)      # Red
        self.minute_color = (0, 255, 0)    # Green
        self.second_color = (0, 0, 255)    # Blue
        self.marker_color = (30, 30, 30)   # Dim white
        self.background_color = (0, 0, 0)  # Black/off

        # Load colors from settings if available
        if self.usersettings:
            self._load_colors_from_settings()

        logger.info(f"LED Clock initialized with {led_count} LEDs")

    def _load_colors_from_settings(self):
        """Load clock hand colors from user settings"""
        try:
            # Load hour hand color
            hour_r = self.usersettings.get_setting_value("clock_hour_red")
            hour_g = self.usersettings.get_setting_value("clock_hour_green")
            hour_b = self.usersettings.get_setting_value("clock_hour_blue")
            if hour_r is not None and hour_g is not None and hour_b is not None:
                self.hour_color = (int(hour_r), int(hour_g), int(hour_b))
                logger.info(f"Loaded hour hand color: {self.hour_color}")

            # Load minute hand color
            minute_r = self.usersettings.get_setting_value("clock_minute_red")
            minute_g = self.usersettings.get_setting_value("clock_minute_green")
            minute_b = self.usersettings.get_setting_value("clock_minute_blue")
            if minute_r is not None and minute_g is not None and minute_b is not None:
                self.minute_color = (int(minute_r), int(minute_g), int(minute_b))
                logger.info(f"Loaded minute hand color: {self.minute_color}")

            # Load second hand color
            second_r = self.usersettings.get_setting_value("clock_second_red")
            second_g = self.usersettings.get_setting_value("clock_second_green")
            second_b = self.usersettings.get_setting_value("clock_second_blue")
            if second_r is not None and second_g is not None and second_b is not None:
                self.second_color = (int(second_r), int(second_g), int(second_b))
                logger.info(f"Loaded second hand color: {self.second_color}")

        except Exception as e:
            logger.warning(f"Failed to load colors from settings: {e}")

    def _led_position_from_time(self, value, max_value):
        """
        Convert time value to LED position

        Args:
            value: Current time value (hour, minute, or second)
            max_value: Maximum value (12 for hours, 60 for minutes/seconds)

        Returns:
            LED position (0 to led_count-1)
        """
        # Calculate position as fraction of circle
        fraction = value / max_value
        # Convert to LED position and add offset so LED 0 is at bottom (6 o'clock)
        # The offset rotates the entire clock 180 degrees
        position = int(fraction * self.led_count) + (self.led_count // 2)
        return position % self.led_count

    def _draw_hand(self, position, length, color, brightness=1.0):
        """
        Draw a clock hand on the LED strip

        Args:
            position: LED position for the hand tip
            length: Length of the hand in LEDs
            color: (R, G, B) tuple
            brightness: Brightness multiplier (0.0 to 1.0)
        """
        for i in range(length):
            # Calculate LED position for this segment
            # Hand extends from center outward
            offset = int((length - i - 1) * (self.led_count / 120.0))
            led_pos = (position - offset) % self.led_count

            # Fade brightness toward the center
            segment_brightness = brightness * (1.0 - (i / length) * 0.5)

            # Apply color with brightness
            r = int(color[0] * segment_brightness)
            g = int(color[1] * segment_brightness)
            b = int(color[2] * segment_brightness)

            self.strip.set_pixel(led_pos, r, g, b)

    def _draw_hour_markers(self):
        """Draw hour markers at 12, 3, 6, 9 positions"""
        marker_positions = [
            self.led_count // 2,        # 12 o'clock (top)
            (self.led_count * 3) // 4,  # 3 o'clock (right)
            0,                          # 6 o'clock (bottom, LED 0)
            self.led_count // 4         # 9 o'clock (left)
        ]

        for pos in marker_positions:
            r, g, b = self.marker_color
            self.strip.set_pixel(pos, r, g, b)

    def update(self):
        """
        Update the clock display with current time
        """
        # Get current time
        now = datetime.now()
        hours = now.hour % 12  # Convert to 12-hour format
        minutes = now.minute
        seconds = now.second
        microseconds = now.microsecond

        # Add fractional seconds for smooth second hand movement
        seconds_fractional = seconds + (microseconds / 1000000.0)

        # Add fractional minutes for smooth minute hand movement
        minutes_fractional = minutes + (seconds / 60.0)

        # Add fractional hours for smooth hour hand movement
        hours_fractional = hours + (minutes / 60.0)

        # Calculate LED positions for each hand
        hour_pos = self._led_position_from_time(hours_fractional, 12)
        minute_pos = self._led_position_from_time(minutes_fractional, 60)
        second_pos = self._led_position_from_time(seconds_fractional, 60)

        # Clear the strip
        self.strip.clear_all()

        # Draw hour markers
        self._draw_hour_markers()

        # Draw clock hands (from shortest to longest so they layer correctly)
        self._draw_hand(hour_pos, self.hour_hand_length, self.hour_color, brightness=1.0)
        self._draw_hand(minute_pos, self.minute_hand_length, self.minute_color, brightness=1.0)
        self._draw_hand(second_pos, self.second_hand_length, self.second_color, brightness=0.8)

        # Update the physical LED strip
        self.strip.show()

    def run(self, update_interval=0.05):
        """
        Run the clock continuously

        Args:
            update_interval: Time between updates in seconds (default 0.05 = 20 FPS)
        """
        self.running = True
        logger.info("LED Clock started")

        try:
            while self.running:
                self.update()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            logger.info("LED Clock stopped by user")
            self.stop()

    def stop(self):
        """Stop the clock and clear the LEDs"""
        self.running = False
        self.strip.clear_all()
        self.strip.show()
        logger.info("LED Clock stopped")

    def set_colors(self, hour_color=None, minute_color=None, second_color=None):
        """
        Set custom colors for clock hands

        Args:
            hour_color: (R, G, B) tuple for hour hand
            minute_color: (R, G, B) tuple for minute hand
            second_color: (R, G, B) tuple for second hand
        """
        if hour_color:
            self.hour_color = hour_color
        if minute_color:
            self.minute_color = minute_color
        if second_color:
            self.second_color = second_color

    def set_brightness(self, brightness):
        """
        Set overall brightness

        Args:
            brightness: 0-100 percentage
        """
        self.strip.set_brightness(brightness)

    def reload_colors_from_settings(self):
        """
        Reload clock hand colors from user settings
        Useful for updating colors without recreating the clock object
        """
        if self.usersettings:
            self._load_colors_from_settings()
        else:
            logger.warning("No user settings available to reload colors")
