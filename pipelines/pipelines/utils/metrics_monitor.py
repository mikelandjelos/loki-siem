from threading import Thread
from time import perf_counter, sleep

import pandas as pd
import psutil


class MetricsMonitor:
    def __init__(self):
        self._start_time = None
        self._end_time = None
        self._log_count = 0
        self._max_memory = 0  # in MB
        self._max_cpu = 0  # in %
        self._monitoring = False
        self._monitor_thread = None
        self._process = psutil.Process()

    def _monitor(self):
        while self._monitoring:
            mem = self._process.memory_info().rss / (1024 * 1024)  # Convert to MB
            cpu = self._process.cpu_percent(interval=0.1)
            self._max_memory = max(self._max_memory, mem)
            self._max_cpu = max(self._max_cpu, cpu)
            sleep(0.1)

    def start(self):
        self._monitoring = True
        self._start_time = perf_counter()
        self._end_time = None
        self._log_count = 0
        self._max_memory = 0
        self._max_cpu = 0
        self._monitor_thread = Thread(target=self._monitor)
        self._monitor_thread.start()

    def stop(self, log_count: int) -> pd.DataFrame:
        assert (
            self._monitoring and self._start_time is not None and self._monitor_thread
        ), (
            "Monitoring must be started, before being stopped."
            " You called `stop` before the `start`."
        )
        self._monitoring = False

        self._monitor_thread.join()

        self._end_time = perf_counter()
        self._log_count = log_count

        elapsed_time = self._end_time - self._start_time
        self._start_time = None
        logs_per_second = self._log_count / elapsed_time if elapsed_time > 0 else 0

        metrics = {
            "Processing Time [s]": round(elapsed_time, 4),
            "Logs Processed": self._log_count,
            "Logs/sec": round(logs_per_second, 4),
            "Max CPU %": round(self._max_cpu, 4),
            "Max Memory (MB)": round(self._max_memory, 4),
        }

        return pd.DataFrame([metrics])
