import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_script = os.path.join(root_dir, "backend", "run_server.py")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=================================================================")
    print("  VERITAS AI: Plagiarism Checker & Unlimited AI Humanizer Suite  ")
    print("=================================================================")
    print(f"Starting Backend on http://127.0.0.1:8001 ...")
    backend_proc = subprocess.Popen([sys.executable, backend_script], cwd=root_dir)

    time.sleep(2)

    print(f"Starting Frontend on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(["npm.cmd", "run", "dev"], cwd=frontend_dir, shell=True)

    print("\n✓ Both services are booting!")
    print("  - Backend API: http://127.0.0.1:8001/docs")
    print("  - Frontend UI: http://localhost:5173")
    print("\nPress Ctrl+C to terminate both servers.")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
