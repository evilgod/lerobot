# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script finds information about all connected Feetech motors.
It supports reading from multiple motors connected simultaneously.

Example usage:
```bash
# Using default port
python lerobot/scripts/find_motor_id.py

# Or specify a different port
python lerobot/scripts/find_motor_id.py --port /dev/tty.usbmodem585A0080521
```
"""

import argparse
from lerobot.common.robot_devices.motors.configs import FeetechMotorsBusConfig
from lerobot.common.robot_devices.motors.feetech import FeetechMotorsBus


#DEFAULT_PORT = "/dev/tty.usbmodem58FA0923331"
#DEFAULT_PORT = "/dev/tty.usbmodem58FA1014141"
DEFAULT_PORT = "/dev/tty.usbmodem58FA0922561"
#DEFAULT_PORT = "/dev/tty.usbmodem58FA1015441"

def read_motor_info(motor_bus, motor_id):
    """Read and return information for a specific motor ID."""
    info = {
        "id": motor_id,
        "position": None,
        "voltage": None,
        "temperature": None,
        "load": None,
        "moving": None
    }
    
    try:
        info["position"] = motor_bus.read_with_motor_ids(["sts3215"], motor_id, "Present_Position")
    except Exception:
        pass

    try:
        info["voltage"] = motor_bus.read_with_motor_ids(["sts3215"], motor_id, "Present_Voltage")
    except Exception:
        pass

    try:
        info["temperature"] = motor_bus.read_with_motor_ids(["sts3215"], motor_id, "Present_Temperature")
    except Exception:
        pass

    try:
        info["load"] = motor_bus.read_with_motor_ids(["sts3215"], motor_id, "Present_Load")
    except Exception:
        pass

    try:
        info["moving"] = motor_bus.read_with_motor_ids(["sts3215"], motor_id, "Moving")
    except Exception:
        pass

    return info


def print_motor_info(info):
    """Print formatted motor information."""
    print(f"\n=== Motor ID: {info['id']} ===")
    print(f"Position: {info['position']} steps (0-4095, center at 2048)")
    if info['load'] is not None:
        print(f"Load: {info['load']}")
    if info['voltage'] is not None:
        voltage = info['voltage'] / 10.0  # Convert to actual voltage (0.1V units)
        print(f"Voltage: {voltage:.1f}V")
    if info['temperature'] is not None:
        print(f"Temperature: {info['temperature']}°C")
    if info['moving'] is not None:
        print(f"Moving: {'Yes' if info['moving'] else 'No'}")


def find_motors_info(port: str):
    # Create a temporary config with a dummy motor for initialization
    config = FeetechMotorsBusConfig(
        port=port,
        motors={"temp_motor": (1, "sts3215")},
    )
    
    # Initialize the motor bus
    motor_bus = FeetechMotorsBus(config)
    
    try:
        # Connect to the motor bus
        motor_bus.connect()
        print(f"Successfully connected to port: {port}")
        
        # Search through possible motor IDs (0-252 is the valid range for Feetech)
        print("Scanning for connected motors...")
        found_ids = motor_bus.find_motor_indices(range(253))
        
        if not found_ids:
            print("No motors found! Please check:")
            print("1. The motors are properly connected")
            print("2. The power supply is connected")
            print("3. The correct port is being used")
            return

        print(f"\nFound {len(found_ids)} motor(s)")
        
        # Create a new config with all found motors
        motors_dict = {
            f"motor_{id}": (id, "sts3215") for id in found_ids
        }
        config = FeetechMotorsBusConfig(
            port=port,
            motors=motors_dict,
        )
        
        # Reconnect with the new configuration
        motor_bus.disconnect()
        motor_bus = FeetechMotorsBus(config)
        motor_bus.connect()
        
        # Read and display information for each motor
        for motor_id in found_ids:
            motor_info = read_motor_info(motor_bus, motor_id)
            print_motor_info(motor_info)
                
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Always disconnect properly
        motor_bus.disconnect()
        print("\nDisconnected from motor bus")


def main():
    parser = argparse.ArgumentParser(
        description="Find and display information for all connected Feetech motors"
    )
    parser.add_argument(
        "--port",
        type=str,
        default=DEFAULT_PORT,
        help=f"The port where the motors are connected (default: {DEFAULT_PORT})"
    )
    
    args = parser.parse_args()
    find_motors_info(args.port)


if __name__ == "__main__":
    main() 