"""
Script to add batch selector to App.jsx
"""
import re

# Read the file
with open('src/frontend/src/App.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the month filter section
old_section = '''          {/* Month Filter & Batch Navigation */}
          <div className="flex items-center justify-between mb-6 px-1">
            <h2 className="text-sm font-bold text-indigo-900/60 uppercase tracking-widest flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              October 2025
            </h2>
          </div>'''

new_section = '''          {/* Batch Selector */}
          <div className="flex items-center justify-between mb-6 px-1">
            <h2 className="text-sm font-bold text-indigo-900/60 uppercase tracking-widest flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Select Batch
            </h2>
            <div className="flex gap-3">
              <button
                onClick={() => setSelectedBatch('oct2025')}
                className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 shadow-md ${selectedBatch === 'oct2025'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-indigo-500/30 scale-105'
                  : 'bg-white text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'
                  }`}
              >
                October 2025
              </button>
              <button
                onClick={() => setSelectedBatch('dec2025')}
                className={`px-5 py-2.5 rounded-full text-sm font-semibold transition-all duration-300 shadow-md ${selectedBatch === 'dec2025'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-indigo-500/30 scale-105'
                  : 'bg-white text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'
                  }`}
              >
                December 2025
              </button>
            </div>
          </div>'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✓ Replaced batch selector section")
else:
    print("✗ Could not find the section to replace")
    print("Searching for partial match...")
    if "October 2025" in content:
        print("Found 'October 2025' in file")
    else:
        print("'October 2025' not found")

# Write back
with open('src/frontend/src/App.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Updated App.jsx")
