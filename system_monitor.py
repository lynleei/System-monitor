# Author @ Lynlee Hong
#!/usr/bin/env python3

#!/usr/bin/env python3
import argparse
from monitor.core import SystemMonitor
from monitor.reporting import ReportGenerator
from monitor.utils import validate_thresholds

def main():
    parser = argparse.ArgumentParser(description="Advanced System Health Monitor")
    parser.add_argument('--interval', type=int, default=2, 
                       help="Polling interval in seconds")
    parser.add_argument('--report', choices=['text', 'json', 'html'], 
                       help="Generate report in specified format")
    parser.add_argument('--thresholds', type=str,
                       help="Custom thresholds in format cpu:X,mem:Y,disk:Z")
    parser.add_argument('--interactive', action='store_true',
                       help="Start interactive monitoring dashboard")
    args = parser.parse_args()

    monitor = SystemMonitor()
    
    if args.thresholds:
        thresholds = validate_thresholds(args.thresholds)
        monitor.update_thresholds(thresholds)
    
    if args.interactive:
        monitor.start_interactive()
    elif args.report:
        report = ReportGenerator(monitor).generate(args.report)
        print(report)
    else:
        monitor.run_continuous(args.interval)

if __name__ == "__main__":
    main()