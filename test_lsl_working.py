#!/usr/bin/env python3
"""
Clean LSL Stream Test
"""

import time
from pylsl import resolve_streams, StreamInlet

def test_lsl_streams():
    print("=== LSL Stream Detection Test ===")
    print("Looking for LSL streams (5 second timeout)...")
    
    try:
        streams = resolve_streams(wait_time=5.0)
        print(f"✓ Found {len(streams)} total streams")
        
        if not streams:
            print("✗ No LSL streams detected")
            print("  This means the muselsl patch is not working correctly")
            return False
        
        print("\nStream details:")
        eeg_stream = None
        for i, stream in enumerate(streams):
            name = stream.name()
            stream_type = stream.type()
            channels = stream.channel_count()
            rate = stream.nominal_srate()
            
            print(f"  {i+1}. {name} ({stream_type}) - {channels} channels @ {rate}Hz")
            
            if stream_type == 'EEG':
                eeg_stream = stream
        
        if not eeg_stream:
            print("✗ No EEG stream found among available streams")
            return False
            
        print(f"\n✓ Found EEG stream: {eeg_stream.name()}")
        
        # Test data reception
        print("Testing data reception for 5 seconds...")
        inlet = StreamInlet(eeg_stream)
        
        samples_received = 0
        start_time = time.time()
        
        while time.time() - start_time < 5:
            sample, timestamp = inlet.pull_sample(timeout=1.0)
            if sample:
                samples_received += 1
                if samples_received <= 3:
                    print(f"  Sample {samples_received}: {[f'{x:.1f}' for x in sample[:4]]} µV")
        
        elapsed = time.time() - start_time
        rate = samples_received / elapsed if elapsed > 0 else 0
        
        print(f"\nResults:")
        print(f"  Samples received: {samples_received}")
        print(f"  Sample rate: {rate:.1f} Hz")
        
        if samples_received > 10:
            print("✓ SUCCESS: LSL streaming is working!")
            return True
        elif samples_received > 0:
            print("⚠ PARTIAL: Some data received but low rate")
            return False
        else:
            print("✗ FAILED: No data received")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_lsl_streams()
    
    if success:
        print("\n🎉 The muselsl patch is working correctly!")
        print("   You can now use the GUI successfully.")
    else:
        print("\n❌ The muselsl patch has issues.")
        print("   The GUI will not receive data until this is fixed.")
