import time
import sys
import select
from pymavlink import mavutil

# ==========================================
# Parameters
# ==========================================
TIMEOUT_THRESHOLD = 3.0  # Threshold for determining disconnection (e.g., 3 seconds)

def check_key():
    """Non-blocking key input reading (for easy exit)"""
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None

def main():
    print("="*50)
    print("📡 Ground Station Parser (GCS Parser) Started...")
    print(f"⏱️  Connection timeout threshold set to: {TIMEOUT_THRESHOLD} seconds")
    print("="*50)
    print("Waiting to receive MAVLink packets...")

    # Establish UDP listening connection
    master = mavutil.mavlink_connection('udpin:127.0.0.1:14550')

    # Status tracking variables
    last_heartbeat_time = 0
    is_connected = False
    connection_lost_notified = False

    try:
        while True:
            # Add keyboard monitoring for easy exit with 'q'
            key = check_key()
            if key and key.lower() == 'q':
                break

            current_time = time.time()

            # ------------------------------------------------
            # 1. Receive and parse packets (Non-blocking)
            # ------------------------------------------------
            # blocking=False: If no packet, it won't block here, will directly return None
            msg = master.recv_match(blocking=False)
            
            if msg:
                msg_type = msg.get_type()

                if msg_type == 'HEARTBEAT':
                    # Updates the timestamp of the most recent HEARTBEAT receipt.
                    last_heartbeat_time = current_time
                    
                    if not is_connected:
                        print(f"\n✅ [System Notification] Connection established! Target System ID: {master.target_system}")
                        is_connected = True
                        connection_lost_notified = False
                    
                    print(f"[{current_time:.2f}] 💓 Received HEARTBEAT (Mode: {msg.base_mode}, Status: {msg.system_status})")
                
                elif msg_type == 'ATTITUDE':
                    print(f"[{current_time:.2f}] 🛩️ Received ATTITUDE -> Roll: {msg.roll:.3f} | Pitch: {msg.pitch:.3f}")
                
                elif msg_type == 'BAD_DATA':
                    print(f"[{current_time:.2f}] ⚠️ [Warning] Found corrupted packet or Checksum error!")

            # ------------------------------------------------
            # 2. Timeout detection logic
            # ------------------------------------------------
            # If connected before, and current time is more than the threshold since last heartbeat
            if is_connected and (current_time - last_heartbeat_time > TIMEOUT_THRESHOLD):
                # To avoid screen being flooded with warnings, we only print once when disconnected
                if not connection_lost_notified:
                    print("\n" + "!"*50)
                    print(f"🚨 [Emergency Alert] Connection lost (CONNECTION LOST)!")
                    print(f"🚨 More than {TIMEOUT_THRESHOLD} seconds have passed without receiving a heartbeat. The drone may have crashed or been jammed.")
                    print("!"*50 + "\n")
                    connection_lost_notified = True
                    is_connected = False # Mark as disconnected, wait for next heartbeat to trigger connection establishment

            # Slightly rest to avoid 100% CPU load
            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Parser closed.")

if __name__ == "__main__":
    import termios
    import tty
    import atexit

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def restore_terminal():
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    atexit.register(restore_terminal)
    tty.setcbreak(fd)
    
    main()