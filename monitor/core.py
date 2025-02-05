import psutil
import platform
import socket
import subprocess
from threading import Thread, Event
from datetime import datetime
from collections import deque
import time
from colorama import Fore, Style

class SystemMonitor:
    def __init__(self):
        self.history = {
            'cpu': deque(maxlen=60),
            'mem': deque(maxlen=60),
            'disk': deque(maxlen=60),
            'temp': deque(maxlen=60)
        }
        self.alerts = []
        self.running = Event()
        self.config = {
            'thresholds': {
                'cpu': 90,
                'mem': 85,
                'disk': 90,
                'temp': 80
            },
            'poll_interval': 2
        }
        
    def get_system_status(self):
        """Get current system metrics"""
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'mem': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent,
            'temp': self._get_cpu_temp(),
            'processes': self._get_top_processes(),
            'network': self._get_network_status()
        }

    def _get_cpu_temp(self):
        """Get CPU temperature (cross-platform)"""
        try:
            if platform.system() == 'Linux':
                temps = psutil.sensors_temperatures()
                return temps['coretemp'][0].current if 'coretemp' in temps else None
            elif platform.system() == 'Windows':
                from ctypes import windll, Structure, byref, c_ulong, c_uint
                class TempInfo(Structure):
                    _fields_ = [('thermalTemp', c_ulong)]
                temp_info = TempInfo()
                windll.thermal.GetThermalTemp.restype = c_uint
                if windll.thermal.GetThermalTemp(0, byref(temp_info)) == 0:
                    return temp_info.thermalTemp / 10.0
                return None
            elif platform.system() == 'Darwin':
                return float(subprocess.check_output(['osx-cpu-temp']))
        except Exception:
            return None

    def _get_top_processes(self, n=5):
        """Get top resource-consuming processes"""
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                procs.append(proc.info)
            except psutil.NoSuchProcess:
                pass
        procs.sort(key=lambda p: p['cpu_percent'], reverse=True)
        return procs[:n]

    def _get_network_status(self):
        """Get detailed network statistics"""
        net = psutil.net_io_counters()
        return {
            'sent': net.bytes_sent,
            'recv': net.bytes_recv,
            'latency': self._ping_test()
        }

    def _ping_test(self, host="8.8.8.8"):
        """Measure network latency (Windows compatible)"""
        try:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', param, '1', host]
            
            # Windows-specific settings to hide console window
            kwargs = {}
            if platform.system() == 'Windows':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
                
            output = subprocess.check_output(
                command,
                stderr=subprocess.STDOUT,
                **kwargs
            )
            return float(output.decode().split('time=')[-1].split(' ')[0])
        except Exception:
            return None

    def check_thresholds(self, metrics):
        """Check metrics against configured thresholds"""
        alerts = []
        for metric, value in metrics.items():
            if metric in self.config['thresholds'] and value is not None:
                if value > self.config['thresholds'][metric]:
                    alerts.append(f"{metric.upper()} threshold exceeded: {value}%")
        return alerts

    def update_thresholds(self, new_thresholds):
        """Update monitoring thresholds"""
        self.config['thresholds'].update(new_thresholds)

    def run_continuous(self, interval):
        """Run continuous monitoring"""
        self.running.set()
        try:
            while self.running.is_set():
                metrics = self.get_system_status()
                self._update_history(metrics)
                new_alerts = self.check_thresholds(metrics)
                self.alerts.extend(new_alerts)
                self._display_status(metrics)
                time.sleep(interval)
        except KeyboardInterrupt:
            self.running.clear()

    def _update_history(self, metrics):
        """Update historical data"""
        for metric in ['cpu', 'mem', 'disk', 'temp']:
            self.history[metric].append(metrics.get(metric, 0))

    def _display_status(self, metrics):
        """Display status with color coding"""
        status = []
        status.append(f"\n{Fore.CYAN}==== System Status [{datetime.now().strftime('%H:%M:%S')}] ===={Style.RESET_ALL}")
        
        # CPU
        cpu_color = Fore.RED if metrics['cpu'] > 90 else Fore.YELLOW if metrics['cpu'] > 70 else Fore.GREEN
        status.append(f"{Fore.WHITE}CPU: {cpu_color}{metrics['cpu']}%{Style.RESET_ALL}")
        
        # Memory
        mem_color = Fore.RED if metrics['mem'] > 90 else Fore.YELLOW if metrics['mem'] > 70 else Fore.GREEN
        status.append(f"{Fore.WHITE}Memory: {mem_color}{metrics['mem']}%{Style.RESET_ALL}")
        
        # Disk
        disk_color = Fore.RED if metrics['disk'] > 90 else Fore.YELLOW if metrics['disk'] > 70 else Fore.GREEN
        status.append(f"{Fore.WHITE}Disk: {disk_color}{metrics['disk']}%{Style.RESET_ALL}")
        
        # Temperature
        if metrics['temp']:
            temp_color = Fore.RED if metrics['temp'] > 80 else Fore.YELLOW if metrics['temp'] > 60 else Fore.GREEN
            status.append(f"{Fore.WHITE}Temp: {temp_color}{metrics['temp']}°C{Style.RESET_ALL}")
        
        print("\n".join(status))

    def start_interactive(self):
        """Start interactive monitoring dashboard (Unix/Mac only)"""
        if platform.system() == 'Windows':
            print("Interactive mode not available on Windows. Using continuous mode.")
            self.run_continuous(self.config['poll_interval'])
            return

        try:
            import curses
            curses.wrapper(self._interactive_loop)
        except ImportError:
            print("Curses not available, falling back to simple mode")
            self.run_continuous(self.config['poll_interval'])

    def _interactive_loop(self, stdscr):
        """Curses-based interactive display (Unix/Mac only)"""
        if platform.system() == 'Windows':
            return

        import curses
        curses.curs_set(0)
        stdscr.nodelay(1)
        self.running.set()
        
        while self.running.is_set():
            metrics = self.get_system_status()
            self._update_history(metrics)
            
            stdscr.clear()
            self._draw_curses(stdscr, metrics)
            stdscr.refresh()
            
            time.sleep(self.config['poll_interval'])
            
            # Check for quit key
            c = stdscr.getch()
            if c == ord('q'):
                self.running.clear()

    def _draw_curses(self, stdscr, metrics):
        """Draw curses interface (Unix/Mac only)"""
        if platform.system() == 'Windows':
            return

        import curses
        stdscr.addstr(0, 0, "System Monitor (q to quit)", curses.A_BOLD)
        row = 2
        
        # Basic metrics
        for metric, value in metrics.items():
            if value is None:
                continue
            if isinstance(value, float):
                display_value = f"{value:.1f}"
            else:
                display_value = str(value)
            stdscr.addstr(row, 0, f"{metric.upper():<10}: {display_value}")
            row += 1

        # History graphs
        self._draw_history(stdscr, 10, 0)

    def _draw_history(self, stdscr, start_row, start_col):
        """Draw ASCII history graphs (Unix/Mac only)"""
        if platform.system() == 'Windows':
            return

        # CPU History
        stdscr.addstr(start_row, start_col, "CPU History:")
        max_val = max(self.history['cpu']) if self.history['cpu'] else 100
        for i, val in enumerate(self.history['cpu']):
            height = int((val / max_val) * 10) if max_val > 0 else 0
            stdscr.addstr(start_row + 1 + i, start_col, "█" * height)