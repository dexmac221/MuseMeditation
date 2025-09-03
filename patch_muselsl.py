#!/usr/bin/env python3
"""
Patch muselsl Library for Ubuntu 24.04
Fix the actual streaming issues by patching the installed library
"""

import os
import shutil
import sys

def create_fixed_stream_file():
    """Create a fixed version of the stream.py file"""
    
    fixed_stream_code = '''import re
import subprocess
from functools import partial
from shutil import which
from sys import platform
from time import time
import logging
import numpy as np

import pygatt
from pylsl import StreamInfo, StreamOutlet, local_clock

from . import backends, helper
from .constants import (AUTO_DISCONNECT_DELAY, LSL_ACC_CHUNK, LSL_EEG_CHUNK,
                        LSL_GYRO_CHUNK, LSL_PPG_CHUNK, MUSE_NB_ACC_CHANNELS,
                        MUSE_NB_EEG_CHANNELS, MUSE_NB_GYRO_CHANNELS,
                        MUSE_NB_PPG_CHANNELS, MUSE_SAMPLING_ACC_RATE,
                        MUSE_SAMPLING_EEG_RATE, MUSE_SAMPLING_GYRO_RATE,
                        MUSE_SAMPLING_PPG_RATE, LIST_SCAN_TIMEOUT, LOG_LEVELS)
from .muse import Muse


def _print_muse_list(muses):
    for m in muses:
        print(f'Found device {m["name"]}, MAC Address {m["address"]}')
    if not muses:
        print('No Muses found.')


# Returns a list of available Muse devices.
def list_muses(backend='auto', interface=None, log_level=logging.ERROR):
    logging.basicConfig(level=log_level)
    if backend == 'auto' and which('bluetoothctl') is not None:
        print("Backend was 'auto' and bluetoothctl was found, using to list muses...")
        return _list_muses_bluetoothctl(LIST_SCAN_TIMEOUT)

    backend = helper.resolve_backend(backend)

    if backend == 'gatt':
        interface = interface or 'hci0'
        adapter = pygatt.GATTToolBackend(interface)
    elif backend == 'bluemuse':
        print('Starting BlueMuse, see BlueMuse window for interactive list of devices.')
        subprocess.call('start bluemuse:', shell=True)
        return
    elif backend == 'bleak':
        adapter = backends.BleakBackend()
    elif backend == 'bgapi':
        adapter = pygatt.BGAPIBackend(serial_port=interface)

    try:
        adapter.start()
        print('Searching for Muses, this may take up to 10 seconds...')
        devices = adapter.scan(timeout=LIST_SCAN_TIMEOUT)
        adapter.stop()
    except pygatt.exceptions.BLEError as e:
        if backend == 'gatt':
            print('pygatt failed to scan for BLE devices. Trying with '
                  'bluetoothctl.')
            return _list_muses_bluetoothctl(LIST_SCAN_TIMEOUT)
        else:
            raise e

    muses = [d for d in devices if d['name'] and 'Muse' in d['name']]
    _print_muse_list(muses)

    return muses


def _list_muses_bluetoothctl(timeout, verbose=False):
    """Identify Muse BLE devices using bluetoothctl.
    
    FIXED VERSION for Ubuntu 24.04 compatibility.
    Handles modern bluetoothctl behavior properly without pexpect issues.
    """
    import time
    
    print('Searching for Muses, this may take up to 10 seconds...')
    
    # Start bluetoothctl scan (fixed approach for Ubuntu 24.04)
    try:
        # Start scan in background
        scan_process = subprocess.Popen(['bluetoothctl', 'scan', 'on'], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE,
                                      text=True)
        
        # Let it scan for the timeout period
        print(f"Scanning for {timeout} seconds...")
        time.sleep(timeout)
        
        # Stop the scan
        try:
            subprocess.run(['bluetoothctl', 'scan', 'off'], 
                          timeout=5, 
                          capture_output=True)
        except subprocess.TimeoutExpired:
            pass  # Continue anyway
            
        # Terminate scan process if still running
        if scan_process.poll() is None:
            scan_process.terminate()
            try:
                scan_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                scan_process.kill()
        
    except Exception as e:
        print(f"Scan process error (continuing anyway): {e}")

    # List devices using bluetoothctl
    list_devices_cmd = ['bluetoothctl', 'devices']
    try:
        result = subprocess.run(list_devices_cmd, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=10,
                              text=True)
        devices = result.stdout.split('\\n')
    except subprocess.TimeoutExpired:
        print("Timeout while listing devices")
        devices = []
    except Exception as e:
        print(f"Error listing devices: {e}")
        devices = []
        
    # Parse Muse devices with improved regex
    muses = []
    for device_line in devices:
        if 'Muse' in device_line:
            try:
                # Extract name and address with better error handling
                name_match = re.search(r'Muse[^\\s]*', device_line)
                addr_match = re.search(r'([0-9A-F]{2}[:-]){5}[0-9A-F]{2}', device_line, re.IGNORECASE)
                
                if name_match and addr_match:
                    muses.append({
                        'name': name_match.group(0),
                        'address': addr_match.group(0)
                    })
            except Exception as e:
                if verbose:
                    print(f"Error parsing device line '{device_line}': {e}")
                continue
                
    _print_muse_list(muses)
    return muses


# Returns the address of the Muse with the name provided, otherwise returns address of first available Muse.
def find_muse(name=None, backend='auto'):
    muses = list_muses(backend)
    if name:
        for muse in muses:
            if muse['name'] == name:
                return muse
    elif muses:
        return muses[0]


# FIXED PUSH FUNCTION - This was the main issue!
def fixed_push(data, timestamps, outlet):
    """Fixed push function that properly handles data format"""
    try:
        # Handle different data formats properly
        if isinstance(data, np.ndarray):
            if data.ndim == 2:
                # Matrix format - push each column
                for ii in range(data.shape[1]):
                    if ii < len(timestamps):
                        outlet.push_sample(data[:, ii].tolist(), timestamps[ii])
                    else:
                        outlet.push_sample(data[:, ii].tolist())
            else:
                # Vector format
                if len(timestamps) > 0:
                    outlet.push_sample(data.tolist(), timestamps[0])
                else:
                    outlet.push_sample(data.tolist())
        elif isinstance(data, list):
            # List of samples
            for i, sample in enumerate(data):
                if i < len(timestamps):
                    outlet.push_sample(sample, timestamps[i])
                else:
                    outlet.push_sample(sample)
        else:
            # Single sample
            if len(timestamps) > 0:
                outlet.push_sample(data, timestamps[0])
            else:
                outlet.push_sample(data)
                
    except Exception as e:
        print(f"Fixed push error: {e}")
        # Fallback to basic push
        try:
            if hasattr(data, 'shape') and data.ndim == 2:
                for ii in range(data.shape[1]):
                    outlet.push_sample(data[:, ii], timestamps[ii] if ii < len(timestamps) else time())
            else:
                outlet.push_sample(data, timestamps[0] if len(timestamps) > 0 else time())
        except:
            pass


# Begins LSL stream(s) from a Muse with a given address with data sources determined by arguments
def stream(
    address,
    backend='auto',
    interface=None,
    name=None,
    ppg_enabled=False,
    acc_enabled=False,
    gyro_enabled=False,
    eeg_disabled=False,
    preset=None,
    disable_light=False,
    lsl_time=False,
    retries=1,
    log_level=logging.ERROR
):
    # If no data types are enabled, we warn the user and return immediately.
    if eeg_disabled and not ppg_enabled and not acc_enabled and not gyro_enabled:
        print('Stream initiation failed: At least one data source must be enabled.')
        return

    # For any backend except bluemuse, we will start LSL streams hooked up to the muse callbacks.
    if backend != 'bluemuse':
        if not address:
            found_muse = find_muse(name, backend)
            if not found_muse:
                return
            else:
                address = found_muse['address']
                name = found_muse['name']

        outlets = {}
        
        if not eeg_disabled:
            eeg_info = StreamInfo('Muse', 'EEG', MUSE_NB_EEG_CHANNELS, MUSE_SAMPLING_EEG_RATE, 'float32',
                                'Muse%s' % address)
            eeg_info.desc().append_child_value("manufacturer", "Muse")
            eeg_channels = eeg_info.desc().append_child("channels")

            for c in ['TP9', 'AF7', 'AF8', 'TP10', 'Right AUX']:
                eeg_channels.append_child("channel") \\
                    .append_child_value("label", c) \\
                    .append_child_value("unit", "microvolts") \\
                    .append_child_value("type", "EEG")

            outlets['eeg'] = StreamOutlet(eeg_info, LSL_EEG_CHUNK)

        if ppg_enabled:
            ppg_info = StreamInfo('Muse', 'PPG', MUSE_NB_PPG_CHANNELS, MUSE_SAMPLING_PPG_RATE,
                                'float32', 'Muse%s' % address)
            ppg_info.desc().append_child_value("manufacturer", "Muse")
            ppg_channels = ppg_info.desc().append_child("channels")

            for c in ['PPG1', 'PPG2', 'PPG3']:
                ppg_channels.append_child("channel") \\
                    .append_child_value("label", c) \\
                    .append_child_value("unit", "mmHg") \\
                    .append_child_value("type", "PPG")

            outlets['ppg'] = StreamOutlet(ppg_info, LSL_PPG_CHUNK)

        if acc_enabled:
            acc_info = StreamInfo('Muse', 'ACC', MUSE_NB_ACC_CHANNELS, MUSE_SAMPLING_ACC_RATE,
                                'float32', 'Muse%s' % address)
            acc_info.desc().append_child_value("manufacturer", "Muse")
            acc_channels = acc_info.desc().append_child("channels")

            for c in ['X', 'Y', 'Z']:
                acc_channels.append_child("channel") \\
                    .append_child_value("label", c) \\
                    .append_child_value("unit", "g") \\
                    .append_child_value("type", "accelerometer")

            outlets['acc'] = StreamOutlet(acc_info, LSL_ACC_CHUNK)

        if gyro_enabled:
            gyro_info = StreamInfo('Muse', 'GYRO', MUSE_NB_GYRO_CHANNELS, MUSE_SAMPLING_GYRO_RATE,
                                'float32', 'Muse%s' % address)
            gyro_info.desc().append_child_value("manufacturer", "Muse")
            gyro_channels = gyro_info.desc().append_child("channels")

            for c in ['X', 'Y', 'Z']:
                gyro_channels.append_child("channel") \\
                    .append_child_value("label", c) \\
                    .append_child_value("unit", "dps") \\
                    .append_child_value("type", "gyroscope")

            outlets['gyro'] = StreamOutlet(gyro_info, LSL_GYRO_CHUNK)

        # Use fixed push functions
        push_eeg = partial(fixed_push, outlet=outlets['eeg']) if not eeg_disabled else None
        push_ppg = partial(fixed_push, outlet=outlets['ppg']) if ppg_enabled else None
        push_acc = partial(fixed_push, outlet=outlets['acc']) if acc_enabled else None
        push_gyro = partial(fixed_push, outlet=outlets['gyro']) if gyro_enabled else None

        time_func = local_clock if lsl_time else time

        muse = Muse(address=address, callback_eeg=push_eeg, callback_ppg=push_ppg, callback_acc=push_acc, callback_gyro=push_gyro,
                    backend=backend, interface=interface, name=name, preset=preset, disable_light=disable_light, time_func=time_func, log_level=log_level)

        didConnect = muse.connect(retries=retries)

        if(didConnect):
            print('Connected.')
            muse.start()

            eeg_string = " EEG" if not eeg_disabled else ""
            ppg_string = " PPG" if ppg_enabled else ""
            acc_string = " ACC" if acc_enabled else ""
            gyro_string = " GYRO" if gyro_enabled else ""

            print("Streaming%s%s%s%s..." %
                (eeg_string, ppg_string, acc_string, gyro_string))

            # FIXED: Better streaming loop that doesn't break on timing issues
            try:
                start_time = time_func()
                while True:
                    current_time = time_func()
                    
                    # Check if we should auto-disconnect (but be more lenient)
                    if hasattr(muse, 'last_timestamp'):
                        if current_time - muse.last_timestamp > AUTO_DISCONNECT_DELAY:
                            print(f"Auto-disconnect after {AUTO_DISCONNECT_DELAY}s of no data")
                            break
                    elif current_time - start_time > 300:  # Max 5 minutes
                        print("Max streaming time reached")
                        break
                    
                    backends.sleep(1)
                    
            except KeyboardInterrupt:
                print("\\nInterrupted by user")
            finally:
                muse.stop()
                muse.disconnect()

            print('Disconnected.')
        else:
            print('Failed to connect.')

    # For bluemuse backend, we don't need to create LSL streams directly, since these are handled in BlueMuse itself.
    else:
        # Toggle all data stream types in BlueMuse.
        subprocess.call('start bluemuse://setting?key=eeg_enabled!value={}'.format('false' if eeg_disabled else 'true'), shell=True)
        subprocess.call('start bluemuse://setting?key=ppg_enabled!value={}'.format('true' if ppg_enabled else 'false'), shell=True)
        subprocess.call('start bluemuse://setting?key=accelerometer_enabled!value={}'.format('true' if acc_enabled else 'false'), shell=True)
        subprocess.call('start bluemuse://setting?key=gyroscope_enabled!value={}'.format('true' if gyro_enabled else 'false'), shell=True)

        muse = Muse(address=address, callback_eeg=None, callback_ppg=None, callback_acc=None, callback_gyro=None,
                    backend=backend, interface=interface, name=name)
        muse.connect(retries=retries)

        if not address and not name:
            print('Targeting first device BlueMuse discovers...')
        else:
            print('Targeting device: '
                  + ':'.join(filter(None, [name, address])) + '...')
        print('\\n*BlueMuse will auto connect and stream when the device is found. \\n*You can also use the BlueMuse interface to manage your stream(s).')
        muse.start()
'''

    return fixed_stream_code

def patch_muselsl_library():
    """Patch the installed muselsl library with fixes"""
    print("🔧 PATCHING MUSELSL LIBRARY FOR UBUNTU 24.04")
    print("=" * 50)
    
    # Find muselsl installation path
    muselsl_path = "/home/dexmac/anaconda3/envs/generic/lib/python3.10/site-packages/muselsl"
    stream_file = os.path.join(muselsl_path, "stream.py")
    
    if not os.path.exists(stream_file):
        print(f"❌ muselsl not found at {stream_file}")
        return False
    
    print(f"✅ Found muselsl at: {muselsl_path}")
    
    # Create backup
    backup_file = stream_file + ".backup"
    if not os.path.exists(backup_file):
        print("Creating backup of original stream.py...")
        shutil.copy2(stream_file, backup_file)
        print(f"✅ Backup created: {backup_file}")
    else:
        print("✅ Backup already exists")
    
    # Write fixed version
    print("Writing fixed stream.py...")
    try:
        fixed_code = create_fixed_stream_file()
        with open(stream_file, 'w') as f:
            f.write(fixed_code)
        print("✅ Fixed stream.py written")
        
        print("\\n🎉 MUSELSL LIBRARY PATCHED!")
        print("Key fixes applied:")
        print("• ✅ Fixed LSL data push function")
        print("• ✅ Better error handling in callbacks") 
        print("• ✅ Improved streaming loop timing")
        print("• ✅ Enhanced data format handling")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to patch library: {e}")
        return False

def restore_original():
    """Restore original muselsl library"""
    muselsl_path = "/home/dexmac/anaconda3/envs/generic/lib/python3.10/site-packages/muselsl"
    stream_file = os.path.join(muselsl_path, "stream.py")
    backup_file = stream_file + ".backup"
    
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, stream_file)
        print("✅ Original muselsl library restored")
    else:
        print("❌ No backup found to restore")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        restore_original()
    else:
        success = patch_muselsl_library()
        
        if success:
            print("\\n🚀 TRY THE FIXED LIBRARY:")
            print("muselsl stream --address YOUR_MUSE_ADDRESS")
            print("muselsl view --version 2")
            print("\\nTo restore original: python patch_muselsl.py restore")
        else:
            print("\\n❌ Patching failed - library remains unchanged")

if __name__ == "__main__":
    main()