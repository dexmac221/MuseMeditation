#!/usr/bin/env python3
"""
GUI Data Reception Verification Script
This script monitors if the GUI is successfully receiving LSL data
"""

import time
from pylsl import StreamInlet, resolve_stream

def monitor_gui_data():
    print("🔍 Monitoring LSL streams for GUI data reception...")
    print("=" * 50)
    
    try:
        # Look for EEG streams
        print("Searching for EEG streams...")
        streams = resolve_stream('type', 'EEG', timeout=5.0)
        
        if not streams:
            print("❌ No EEG streams found!")
            return
            
        print(f"✅ Found {len(streams)} EEG stream(s)")
        
        # Connect to the first EEG stream
        stream = streams[0]
        inlet = StreamInlet(stream)
        
        print(f"📡 Connected to stream: {stream.name()}")
        print(f"   - Channels: {stream.channel_count()}")
        print(f"   - Sample rate: {stream.nominal_srate()} Hz")
        print(f"   - Type: {stream.type()}")
        print()
        
        # Monitor data for 30 seconds
        print("📊 Monitoring data reception (30 seconds)...")
        start_time = time.time()
        sample_count = 0
        last_report = start_time
        
        while time.time() - start_time < 30:
            try:
                sample, timestamp = inlet.pull_sample(timeout=1.0)
                if sample:
                    sample_count += 1
                    
                    # Report every 5 seconds
                    if time.time() - last_report >= 5:
                        elapsed = time.time() - start_time
                        rate = sample_count / elapsed if elapsed > 0 else 0
                        print(f"   • {elapsed:.1f}s: {sample_count} samples received ({rate:.1f} Hz)")
                        last_report = time.time()
                        
            except Exception as e:
                print(f"   ⚠️ Sample error: {e}")
                
        # Final report
        total_time = time.time() - start_time
        final_rate = sample_count / total_time if total_time > 0 else 0
        
        print()
        print("📈 Final Results:")
        print(f"   • Total samples: {sample_count}")
        print(f"   • Duration: {total_time:.1f} seconds")
        print(f"   • Average rate: {final_rate:.1f} Hz")
        
        if sample_count > 0:
            print("✅ SUCCESS: GUI should be receiving data!")
        else:
            print("❌ WARNING: No data received - GUI may have connection issues")
            
    except Exception as e:
        print(f"❌ Error monitoring streams: {e}")

if __name__ == "__main__":
    monitor_gui_data()
