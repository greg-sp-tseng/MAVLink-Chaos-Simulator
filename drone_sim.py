import time
import math
import random
import sys
import select
import termios
import tty
import atexit
from pymavlink import mavutil

# ==========================================
# Terminal key listening settings (WSL/Linux only)
# ==========================================
# Store terminal original settings to ensure the program can restore normal settings when it ends
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)

def restore_terminal():
    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

atexit.register(restore_terminal)
# Set the terminal to cbreak mode (key presses respond immediately, no need to press Enter).
tty.setcbreak(fd)

def check_key():
    """Non-blocking key input reading"""
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

# ==========================================
# Subroutine 1：Normal Send
# ==========================================
def send_normal(master, uptime_ms, loop_counter, roll, pitch, yaw):
    """Simulate an ideal radio environment without interference"""
    if loop_counter % 10 == 0:
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
            128, 0, 4
        )
        print(f"[{uptime_ms}ms] [🟢 Normal] 💓 Sending HEARTBEAT")

    master.mav.attitude_send(uptime_ms, roll, pitch, yaw, 0.0, 0.0, 0.0)
    print(f"[{uptime_ms}ms] [🟢 Normal] 🛩️ Sending ATTITUDE -> Roll: {roll:.2f}")

# ==========================================
# Subroutine 2：Interference
# ==========================================
def send_interfere(master, uptime_ms, loop_counter, roll, pitch, yaw):
    """Simulates a harsh RF environment with high packet loss."""
    drop_rate = 0.7  # 70% chance packets will be lost due to interference

    if random.random() < drop_rate:
        print(f"[{uptime_ms}ms] [⚠️ Interference] 〰️ Packet dropped")
        return  # Immediate return prevents sending MAVLink commands in interference path.

    # 30% chance to successfully send despite interference
    if loop_counter % 10 == 0:
        master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_QUADROTOR,
            mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
            128, 0, 4
        )
        print(f"[{uptime_ms}ms] [⚠️ Interference] 💓 Sending HEARTBEAT (lucky survival)")

    master.mav.attitude_send(uptime_ms, roll, pitch, yaw, 0.0, 0.0, 0.0)
    print(f"[{uptime_ms}ms] [⚠️ Interference] 🛩️ Sending ATTITUDE -> Roll: {roll:.2f} (lucky survival)")

# ==========================================
# Subroutine 3：Mask (Jamming/Blackout)
# ==========================================
def send_mask(uptime_ms):
    """Simulate electronic warfare jamming, crash, or complete loss of connection"""
    # Nothing is sent, only print status
    print(f"[{uptime_ms}ms] [🚫 Mask] 💥 Radio completely blocked, packets cannot be sent...")

# ==========================================
# Main Program: Menu and State Machine
# ==========================================
def main():
    print("="*50)
    print("🛸 MAVLink Virtual Drone (RF Environment Simulator) 🛸")
    print("="*50)
    print("Use the following number keys to switch states (no need to press Enter):")
    print("  [1] 🟢 Switch to 【Normal Sending】")
    print("  [2] ⚠️ Switch to 【Random Interference】(simulate 70% packet loss)")
    print("  [3] 🚫 Switch to 【Mask/Blackout】(simulate complete loss of connection)")
    print("  [q] 🛑 End program")
    print("="*50)
    print("⏳ Waiting for commands to start...")

    # Initializes UDP MAVLink connection in the main program.
    master = mavutil.mavlink_connection('udpout:127.0.0.1:14550', source_system=1, source_component=1)
    
    current_state = 'WAITING'
    start_time = time.time()
    loop_counter = 0

    try:
        while True:
            # 1. Check keyboard input (non-blocking)
            key = check_key()
            if key:
                if key == '1':
                    current_state = 'NORMAL'
                    print("\n>>>>> Switch to：🟢 Normal Sending <<<<<\n")
                elif key == '2':
                    current_state = 'INTERFERE'
                    print("\n>>>>> Switch to：⚠️ Random Interference <<<<<\n")
                elif key == '3':
                    current_state = 'MASK'
                    print("\n>>>>> Switch to：🚫 Mask/Blackout <<<<<\n")
                elif key.lower() == 'q':
                    print("\n🛑 End program.")
                    break

            # 2. If still waiting, don't execute sending logic
            if current_state == 'WAITING':
                time.sleep(0.1)
                continue

            # 3. Prepare test data
            current_time = time.time()
            uptime_ms = int((current_time - start_time) * 1000)
            roll = math.sin(current_time) * 0.5
            pitch = math.cos(current_time * 0.5) * 0.3
            yaw = (current_time % (2 * math.pi)) - math.pi

            # 4. Call the corresponding subroutine based on state
            if current_state == 'NORMAL':
                send_normal(master, uptime_ms, loop_counter, roll, pitch, yaw)
            elif current_state == 'INTERFERE':
                send_interfere(master, uptime_ms, loop_counter, roll, pitch, yaw)
            elif current_state == 'MASK':
                send_mask(uptime_ms)

            loop_counter += 1
            time.sleep(0.1) # Maintain 10Hz main loop

    except KeyboardInterrupt:
        print("\n🛑 Force termination of simulation.")

if __name__ == "__main__":
    main()