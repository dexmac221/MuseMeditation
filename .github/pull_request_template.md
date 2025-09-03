## 📝 Description
Brief description of the changes and the motivation behind them.

Fixes #(issue number) [if applicable]

## 🔧 Type of Change
Please delete options that are not relevant:

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update (changes to documentation only)
- [ ] 🎨 Code style/refactoring (formatting, renaming, etc., no functional changes)
- [ ] ⚡ Performance improvement (changes that improve performance)
- [ ] 🧪 Tests (adding missing tests or correcting existing tests)

## 🧠 EEG/Neuroscience Impact
If applicable, describe how this change affects EEG processing or brain monitoring:

- [ ] Improves meditation analysis accuracy
- [ ] Enhances signal processing capabilities
- [ ] Affects hardware communication
- [ ] Changes user meditation feedback
- [ ] N/A - No direct EEG impact

## ✅ Testing Checklist
Please confirm that you have completed the following:

### 🔍 System Testing
- [ ] Ran system diagnostic: `python system_check.py` 
- [ ] Applied/tested muselsl patch functionality
- [ ] Verified GUI launches without errors
- [ ] Tested with Muse 2 hardware (if available)
- [ ] Confirmed LSL streaming works: `python test_lsl_working.py`

### 💻 Code Quality  
- [ ] Code follows the project's Python style guidelines
- [ ] Self-review of the code completed
- [ ] Added comments for complex algorithms, particularly EEG processing
- [ ] Added docstrings for new functions/classes
- [ ] No unused imports or variables (ran refactoring check if possible)

### 📚 Documentation
- [ ] Updated README.md if user-facing changes were made
- [ ] Updated docstrings for any modified functions
- [ ] Added/updated comments for EEG analysis algorithms
- [ ] Updated CHANGELOG.md with new features or fixes

### ⚖️ Compatibility
- [ ] Tested on Ubuntu 24.04 (primary target platform)
- [ ] Verified Python 3.8+ compatibility
- [ ] Confirmed no new dependency conflicts
- [ ] Backward compatibility maintained (or breaking changes documented)

## 📊 Performance Impact
Does this change affect system performance?

- [ ] ✅ Improves performance
- [ ] ➡️ No performance impact  
- [ ] ⚠️ May decrease performance (justified by benefits)
- [ ] ❓ Performance impact unknown/needs testing

If performance is affected, please describe:

## 🖼️ Screenshots/Demos
If applicable, add screenshots or describe the visual changes:

## 📋 Additional Testing Notes
Describe any specific testing scenarios or edge cases you've covered:

## 🤝 Dependencies
List any new dependencies or version changes:

- [ ] No new dependencies
- [ ] Added new dependencies (listed in requirements.txt)
- [ ] Updated existing dependency versions
- [ ] Removed dependencies

## 🔗 Related Issues
Link any related issues or pull requests:

## 🧪 Test Configuration
**System used for testing:**
- OS: [e.g. Ubuntu 24.04]
- Python: [e.g. 3.10.12]
- Hardware: [e.g. Muse 2, or tested without hardware]
- Environment: [e.g. conda, venv, system Python]

## ⚠️ Breaking Changes
If this is a breaking change, please describe what users need to do to adapt:

## 📝 Additional Notes
Add any other context about the pull request here:

---

**By submitting this pull request, I confirm that:**
- [ ] My contributions are licensed under the project's MIT License
- [ ] I have the right to submit this code
- [ ] I understand this will be reviewed before merging
- [ ] I'm available to address feedback and make necessary changes
