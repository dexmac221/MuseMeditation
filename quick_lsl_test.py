#!/usr/bin/env python3
"""
Quick LSL Test - No user input required
"""

from pylsl import resolve_streams

print("Quick LSL Stream Detection Test...")

try:
    streams = resolve_streams(wait_time=3.0)
    print(f"Found {len(streams)} streams:")
    
    for stream in streams:
        print(f"  - {stream.name()} ({stream.type()}) - {stream.channel_count()} channels")
    
    eeg_streams = [s for s in streams if s.type() == 'EEG']
    print(f"\nEEG streams: {len(eeg_streams)}")
    
    if eeg_streams:
        print("SUCCESS: Patched muselsl is creating LSL streams!")
    else:
        print("PROBLEM: No EEG streams found - patch may not be working")
        
except Exception as e:
    print(f"Error: {e}")
