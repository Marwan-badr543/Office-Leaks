"""
Office Leaks - Full Project Runner
===================================
Launches all 3 processes needed to run the project:
  1. Django Backend Server     (port 8000)
  2. Huey Task Queue Consumer  (periodic flush of Redis likes → DB)
  3. Vite Frontend Dev Server  (port 5173)

Usage:
  cd /home/marwan/Programming/office_leaks
  python run.py
  
  Press Ctrl+C once to gracefully stop all processes.

Prerequisites:
  - Redis server must be running (redis-server)
  - Python venv at ./venv with Django + dependencies installed
  - Frontend node_modules installed (cd office_leaks_frontend && npm install)
"""

import subprocess
import signal
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, "venv", "bin", "python")
BACKEND_DIR = os.path.join(BASE_DIR, "office_leaks")
FRONTEND_DIR = os.path.join(BASE_DIR, "office_leaks_frontend")

processes = []


def start_process(name, cmd, cwd, env=None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    print(f"  ▸ Starting {name}...")
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=merged_env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    processes.append((name, proc))
    return proc


def shutdown(signum=None, frame=None):
    print("\n⏹  Shutting down all processes...")
    for name, proc in reversed(processes):
        if proc.poll() is None:
            print(f"  ▸ Stopping {name} (PID {proc.pid})...")
            proc.terminate()
    for name, proc in processes:
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print(f"  ▸ Force killing {name} (PID {proc.pid})...")
            proc.kill()
    print("✔  All processes stopped.")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 55)
    print("  Office Leaks - Full Stack Runner")
    print("=" * 55)
    print()

    # 1. Django Backend
    start_process(
        name="Django Backend (port 8000)",
        cmd=[VENV_PYTHON, "manage.py", "runserver", "0.0.0.0:8000"],
        cwd=BACKEND_DIR,
    )

    # 2. Huey Consumer (runs periodic tasks like flushing likes)
    start_process(
        name="Huey Task Consumer",
        cmd=[VENV_PYTHON, "manage.py", "run_huey"],
        cwd=BACKEND_DIR,
    )

    # 3. Vite Frontend Dev Server
    start_process(
        name="Vite Frontend (port 5173)",
        cmd=["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
    )

    print()
    print("✔  All processes started! Press Ctrl+C to stop.")
    print()

    # Wait for any process to exit
    while True:
        for name, proc in processes:
            ret = proc.poll()
            if ret is not None:
                print(f"\n⚠  {name} exited with code {ret}. Shutting down...")
                shutdown()
        try:
            signal.pause()
        except AttributeError:
            # signal.pause() not available on Windows
            import time
            time.sleep(1)


if __name__ == "__main__":
    main()
