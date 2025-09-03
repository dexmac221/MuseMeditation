#!/usr/bin/env python3
"""
🔍 Muse 2 System Diagnostic & Health Check
Comprehensive system verification for the EEG monitoring system
"""

import sys
import os
import subprocess
import importlib

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Python Version Check")
    print(f"   Current: Python {sys.version}")
    
    if sys.version_info >= (3, 8):
        print("   ✅ Python version is compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def check_system_packages():
    """Check essential system packages"""
    print("\n🔧 System Packages Check")
    
    packages_ok = True
    
    # Check Bluetooth
    try:
        result = subprocess.run(['bluetoothctl', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ bluetoothctl available")
        else:
            print("   ❌ bluetoothctl not working properly")
            packages_ok = False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("   ❌ bluetoothctl not found")
        print("      Install with: sudo apt install bluetooth bluez")
        packages_ok = False
    
    return packages_ok

def check_python_packages():
    """Check required Python packages"""
    print("\n📦 Python Packages Check")
    
    required_packages = {
        'muselsl': 'Muse headband interface',
        'pylsl': 'Lab Streaming Layer', 
        'numpy': 'Numerical computing',
        'PyQt5': 'GUI framework',
        'pyqtgraph': 'Real-time plotting',
        'scipy': 'Signal processing',
        'matplotlib': 'Plotting support',
        'bleak': 'Bluetooth Low Energy'
    }
    
    packages_ok = True
    
    for package, description in required_packages.items():
        try:
            importlib.import_module(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ❌ {package} - {description} [MISSING]")
            packages_ok = False
    
    return packages_ok

def check_muselsl_patch():
    """Check if muselsl patch has been applied"""
    print("\n🔨 muselsl Patch Check")
    
    try:
        # Try to find muselsl installation
        import muselsl
        muselsl_path = os.path.dirname(muselsl.__file__)
        stream_file = os.path.join(muselsl_path, "stream.py")
        
        if not os.path.exists(stream_file):
            print("   ❌ muselsl stream.py not found")
            return False
        
        # Check if backup exists (indicates patch was applied)
        backup_file = stream_file + ".backup"
        if os.path.exists(backup_file):
            print("   ✅ muselsl patch has been applied")
            print(f"      Location: {muselsl_path}")
            return True
        else:
            print("   ⚠️  muselsl patch may not be applied")
            print("      Run: python patch_muselsl.py")
            return False
            
    except ImportError:
        print("   ❌ muselsl not installed")
        return False
    except Exception as e:
        print(f"   ❌ Error checking patch: {e}")
        return False

def check_bluetooth_service():
    """Check Bluetooth service status"""
    print("\n📡 Bluetooth Service Check")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'bluetooth'],
                              capture_output=True, text=True, timeout=5)
        
        if result.stdout.strip() == 'active':
            print("   ✅ Bluetooth service is running")
            return True
        else:
            print("   ❌ Bluetooth service not active")
            print("      Start with: sudo systemctl start bluetooth")
            return False
            
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("   ⚠️  Cannot check Bluetooth service status")
        return False

def check_display_server():
    """Check display server for GUI"""
    print("\n🖥️  Display Server Check")
    
    if 'DISPLAY' in os.environ:
        print(f"   ✅ X11 display available: {os.environ['DISPLAY']}")
        return True
    elif 'WAYLAND_DISPLAY' in os.environ:
        print(f"   ✅ Wayland display available: {os.environ['WAYLAND_DISPLAY']}")
        return True
    else:
        print("   ❌ No display server detected")
        print("      GUI may not work properly")
        return False

def check_permissions():
    """Check user permissions"""
    print("\n👤 User Permissions Check")
    
    permissions_ok = True
    
    # Check if user can access Bluetooth
    try:
        result = subprocess.run(['groups'], capture_output=True, text=True)
        groups = result.stdout.strip().split()
        
        if 'bluetooth' in groups or 'dialout' in groups:
            print("   ✅ User has Bluetooth access permissions")
        else:
            print("   ⚠️  User may need Bluetooth permissions")
            print("      Add to group: sudo usermod -a -G dialout $USER")
            
    except Exception:
        print("   ⚠️  Cannot check user permissions")
    
    return permissions_ok

def run_comprehensive_check():
    """Run all system checks"""
    print("🧠 Muse 2 EEG System Diagnostic")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("System Packages", check_system_packages),
        ("Python Packages", check_python_packages),
        ("muselsl Patch", check_muselsl_patch),
        ("Bluetooth Service", check_bluetooth_service),
        ("Display Server", check_display_server),
        ("User Permissions", check_permissions)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ Error during {check_name} check: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {check_name}")
    
    print(f"\n🎯 Overall Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 SYSTEM READY! All checks passed.")
        print("   You can run: python working_muse_gui.py")
    elif passed >= total - 1:
        print("⚠️  MOSTLY READY: Minor issues detected.")
        print("   System should work but may have limitations.")
    else:
        print("❌ SYSTEM NOT READY: Multiple issues detected.")
        print("   Please address the failed checks before proceeding.")
    
    print("\n💡 Quick Start Commands:")
    print("   Apply patch: python patch_muselsl.py")
    print("   Test LSL:    python test_lsl_working.py")
    print("   Run GUI:     python working_muse_gui.py")
    
    return passed == total

if __name__ == "__main__":
    try:
        system_ready = run_comprehensive_check()
        sys.exit(0 if system_ready else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Diagnostic interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        sys.exit(1)
