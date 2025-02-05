import psutil
import shutil
import subprocess
import platform

def validate_thresholds(threshold_str):
    """Validate and parse threshold string"""
    thresholds = {}
    try:
        for pair in threshold_str.split(','):
            key, value = pair.split(':')
            key = key.lower().strip()
            if key in ['cpu', 'mem', 'disk', 'temp']:
                thresholds[key] = float(value)
        return thresholds
    except ValueError:
        raise ValueError("Invalid threshold format. Use 'cpu:X,mem:Y,disk:Z'")

def kill_process(pid):
    """Terminate process by PID"""
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True
    except psutil.NoSuchProcess:
        return False

def get_gpu_info():
    """Get GPU information (cross-platform)"""
    try:
        if platform.system() == 'Windows':
            return subprocess.check_output(
                ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            ).strip()
        elif platform.system() == 'Linux' and shutil.which('nvidia-smi'):
            return subprocess.check_output(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                text=True
            ).strip()
        elif platform.system() == 'Darwin':
            return subprocess.check_output(
                ['system_profiler', 'SPDisplaysDataType'],
                text=True
            ).strip()
        return "GPU information unavailable"
    except Exception:
        return "GPU information unavailable"