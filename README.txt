system-monitor/
├── system_monitor.py        # Main entry point
├── monitor/
│   ├── __init__.py
│   ├── core.py             # Core monitoring functionality
│   ├── reporting.py        # Report generation
│   └── utils.py            # Helper functions
└── requirements.txt

Windows usage:

# Install dependencies
pip install psutil colorama

# Run in continuous mode
python system_monitor.py --interval 1

# Generate report
python system_monitor.py --report html > report.html