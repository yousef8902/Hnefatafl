import subprocess
import threading


class PrologBridge:
    def __init__(self, prolog_file, swipl_path="swipl"):
        self._lock = threading.Lock()
        # Launch SWI-Prolog and enter the stdin/stdout main_loop.
        self._process = subprocess.Popen(
            [swipl_path, "-q", "-f", prolog_file, "-g", "main_loop"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def close(self):
        if self._process and self._process.poll() is None:
            try:
                self.query_lines("quit")
            except Exception:
                pass
            self._process.terminate()

    def query_lines(self, query):
        with self._lock:
            self._send_query(query)
            return self._read_until_result()

    def query_single_line(self, query):
        lines = self.query_lines(query)
        return lines[0] if lines else ""

    def _send_query(self, query):
        safe_query = query.strip()
        if not safe_query.endswith("."):
            safe_query += "."
        # Each Prolog term is sent as a full line ending in a period.
        self._process.stdin.write(safe_query + "\n")
        self._process.stdin.flush()

    def _read_until_result(self):
        lines = []
        while True:
            line = self._process.stdout.readline()
            if line == "":
                raise RuntimeError("Prolog process ended unexpectedly")
            clean = line.strip()
            # main_loop terminates each query with SUCCESS/FAILED.
            if clean in ("SUCCESS", "FAILED"):
                if clean == "FAILED":
                    raise RuntimeError("Prolog query failed")
                return lines
            if clean != "":
                lines.append(clean)
