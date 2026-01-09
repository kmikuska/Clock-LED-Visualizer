# Neopixel LED Clock

A standalone analog clock display for circular neopixel LED strips, running on Raspberry Pi.

## Features

- **Analog Clock Display**: Traditional clock with hour, minute, and second hands
- **Smooth Animation**: Hands move smoothly (not in discrete steps)
- **Customizable Colors**: Configure colors for each clock hand
- **Hour Markers**: Visual markers at 12, 3, 6, and 9 o'clock positions
- **Adjustable Brightness**: Control LED brightness from 0-100%
- **Flexible GPIO**: Works with PWM-capable GPIO pins

## Hardware Requirements

### Components
- Raspberry Pi (any model with GPIO)
- WS2812B or WS2811 Neopixel LED strip (120 LEDs recommended)
- 5V power supply for LEDs (calculate: 60mA per LED × number of LEDs)
- Logic level shifter (optional but recommended for 5V LEDs)

### Wiring

```
Raspberry Pi GPIO 13 -----> LED Strip Data In (DI/DIN)
Power Supply GND    -----> LED Strip GND
Power Supply 5V     -----> LED Strip 5V
Raspberry Pi GND    -----> Power Supply GND (common ground)
```

**Important Notes:**
- Use a separate power supply for the LEDs (do NOT power from Pi's 5V)
- Connect all grounds together (common ground)
- Consider using a logic level shifter between GPIO (3.3V) and LED data line (5V)
- Add a 300-500Ω resistor between GPIO and LED data line
- Add a 1000µF capacitor across LED power supply

## GPIO Pin Options

The clock uses **GPIO 13** by default, but you can use any PWM-capable pin:

| GPIO Pin | PWM Channel | Notes |
|----------|-------------|-------|
| **13** (default) | PWM1 | Recommended for this clock |
| 12 | PWM0 | Alternative option |
| 18 | PWM0 | Used by default visualizer |
| 19 | PWM1 | Alternative option |

## Installation

### 1. Install Dependencies

```bash
# Install rpi_ws281x library
sudo pip3 install rpi_ws281x

# Or install from source:
git clone https://github.com/jgarff/rpi_ws281x_python.git
cd rpi_ws281x_python
sudo python3 setup.py install
```

### 2. Enable PWM (if needed)

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add or uncomment:
```
# Enable PWM on GPIO 13
dtoverlay=pwm,pin=13,func=4
```

Reboot:
```bash
sudo reboot
```

## Usage

### Basic Usage

Run the clock with default settings (120 LEDs, GPIO 13, 50% brightness):

```bash
sudo python3 neopixel_clock.py
```

**Note:** `sudo` is required for GPIO access.

### Command Line Options

```bash
# Custom LED count
sudo python3 neopixel_clock.py --led-count 60

# Different GPIO pin
sudo python3 neopixel_clock.py --gpio-pin 12

# Adjust brightness
sudo python3 neopixel_clock.py --brightness 75

# Disable smooth movement (update once per second)
sudo python3 neopixel_clock.py --no-smooth

# Combine options
sudo python3 neopixel_clock.py --led-count 120 --gpio-pin 13 --brightness 50
```

### Run at Startup

Create a systemd service to run the clock automatically:

```bash
sudo nano /etc/systemd/system/led-clock.service
```

Add the following:

```ini
[Unit]
Description=Neopixel LED Clock
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/user/Clock-LED-Visualizer
ExecStart=/usr/bin/python3 /home/user/Clock-LED-Visualizer/neopixel_clock.py --led-count 120 --gpio-pin 13 --brightness 50
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable led-clock.service
sudo systemctl start led-clock.service
```

Check status:
```bash
sudo systemctl status led-clock.service
```

View logs:
```bash
sudo journalctl -u led-clock.service -f
```

## Clock Design

### LED Layout

The 120 LEDs are arranged in a circle:
- **LED 0** is at the bottom (6 o'clock position)
- LEDs count clockwise around the circle
- 120 LEDs = 2 LEDs per minute/second position

### Clock Hands

| Hand | Color (default) | Length | Update Rate |
|------|----------------|--------|-------------|
| Hour | Red | 5 LEDs | Continuous (smooth) |
| Minute | Green | 8 LEDs | Continuous (smooth) |
| Second | Blue | 10 LEDs | 20 FPS (smooth) |

### Hour Markers

Dim white LEDs appear at:
- 12 o'clock (LED 60)
- 3 o'clock (LED 90)
- 6 o'clock (LED 0)
- 9 o'clock (LED 30)

## Customization

### Via Web Interface

The easiest way to customize clock hand colors is through the web interface:

1. Access the visualizer web interface (typically at `http://[raspberry-pi-ip]`)
2. Navigate to **LED Settings** page
3. Find the **Clock Colors** section
4. Use the color pickers or RGB sliders to customize:
   - **Hour Hand** (default: Red)
   - **Minute Hand** (default: Green)
   - **Second Hand** (default: Blue)
5. Colors are automatically saved to `config/default_settings.xml`
6. Restart the clock script to apply changes

**Note:** The clock automatically loads colors from the configuration file if the `lib/usersettings` module is available.

### In Python Code

You can also customize the clock by modifying `neopixel_clock.py`:

```python
# Change clock hand colors
clock.set_colors(
    hour_color=(255, 100, 0),    # Orange hour hand
    minute_color=(0, 255, 255),  # Cyan minute hand
    second_color=(255, 0, 255)   # Magenta second hand
)
```

### In the Library

Edit `lib/led_clock.py` to modify:
- Hand lengths (`hour_hand_length`, `minute_hand_length`, `second_hand_length`)
- Marker positions and colors
- Animation behavior

### Configuration File

Colors are stored in `config/default_settings.xml`:

```xml
<!-- LED Clock Colors -->
<clock_hour_red>255</clock_hour_red>
<clock_hour_green>0</clock_hour_green>
<clock_hour_blue>0</clock_hour_blue>

<clock_minute_red>0</clock_minute_red>
<clock_minute_green>255</clock_minute_green>
<clock_minute_blue>0</clock_minute_blue>

<clock_second_red>0</clock_second_red>
<clock_second_green>0</clock_second_green>
<clock_second_blue>255</clock_second_blue>
```

## Troubleshooting

### Permission Denied
```
Error: Permission denied
```
**Solution:** Run with `sudo` for GPIO access

### No Module Named 'rpi_ws281x'
```
ImportError: No module named 'rpi_ws281x'
```
**Solution:** Install the library: `sudo pip3 install rpi_ws281x`

### LEDs Not Lighting Up
1. Check power supply (LEDs need separate 5V supply)
2. Verify wiring (data line to correct GPIO pin)
3. Check common ground connection
4. Try increasing brightness: `--brightness 100`
5. Test with a simple example: `python3 tests/strandtest.py`

### Wrong Colors or Flickering
1. Check LED strip type (WS2812B vs WS2811)
2. Try different GPIO pins (12, 13, 18, 19)
3. Add resistor to data line (300-500Ω)
4. Ensure adequate power supply

### Clock Running Fast/Slow
The clock uses system time from the Raspberry Pi. Ensure:
```bash
# Check time
date

# Sync with NTP
sudo timedatectl set-ntp true
```

## Technical Details

### LED Strip Compatibility
- **WS2812B** (most common): 3-pin, integrated controller
- **WS2811**: 4-pin, external controller
- **SK6812**: Similar to WS2812B
- **APA102/SK9822**: Not supported (uses different protocol)

### Performance
- Update rate: 20 FPS (0.05s interval) for smooth animation
- CPU usage: < 5% on Raspberry Pi 3/4
- Memory: < 50MB

### Files

| File | Description |
|------|-------------|
| `neopixel_clock.py` | Main executable script |
| `lib/led_clock.py` | Clock animation logic |
| `LED_CLOCK_README.md` | This documentation |

## Example Configurations

### 60 LED Clock (Half Resolution)
```bash
sudo python3 neopixel_clock.py --led-count 60 --gpio-pin 13
```

### 144 LED Clock (High Resolution)
```bash
sudo python3 neopixel_clock.py --led-count 144 --gpio-pin 13
```

### Low Power Mode (Dim)
```bash
sudo python3 neopixel_clock.py --brightness 10
```

### Different GPIO Pin
```bash
sudo python3 neopixel_clock.py --gpio-pin 12
```

## License

This code is part of the Clock-LED-Visualizer project.

## Support

For issues and questions:
- GitHub Issues: https://github.com/onlaj/Clock-LED-Visualizer/issues
- Check the main project README for general setup

## Credits

Created for the Clock-LED-Visualizer project by onlaj.
LED clock module designed for circular neopixel displays.
