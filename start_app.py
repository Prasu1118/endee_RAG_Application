import os
import sys
import subprocess
import shutil
import time
import webbrowser
import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def run_command(command, cwd=None):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        cwd=cwd
    )
    for line in process.stdout:
        print(line, end='')
    process.wait()
    return process.returncode

def main():
    print("==========================================")
    print("   🚀 ENTERPRISE RAG PLATFORM LAUNCHER   ")
    print("==========================================")
    print("\n[1/4] Checking Environment...")

    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(project_root, "venv")
    
    # 1. Create VENV if missing
    if not os.path.exists(venv_path):
        print("💡 Virtual environment missing. Creating one now...")
        run_command(f"{sys.executable} -m venv venv", cwd=project_root)
    
    # Determine python and pip path in venv
    if os.name == "nt":  # Windows
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    else:  # Linux/Mac
        python_exe = os.path.join(venv_path, "bin", "python")
        pip_exe = os.path.join(venv_path, "bin", "pip")

    # 2. Install dependencies
    print("\n[2/4] Syncing Dependencies...")
    if not os.path.exists(pip_exe) or not os.path.exists(uvicorn_exe := os.path.join(venv_path, "Scripts", "uvicorn.exe") if os.name == "nt" else os.path.join(venv_path, "bin", "uvicorn")):
        req_file = os.path.join(project_root, "requirements.txt")
        if os.path.exists(req_file):
            print("📦 Installing required packages (first time setup)...")
            run_command(f'"{pip_exe}" install -r requirements.txt', cwd=project_root)
        else:
            print("❌ Error: requirements.txt not found!")
            sys.exit(1)
    else:
        print("✅ Dependencies already synced.")

    # 3. Check for .env
    env_file = os.path.join(project_root, ".env")
    if not os.path.exists(env_file):
        print("\n⚠️ Warning: .env file missing. Copying from .env.example...")
        shutil.copy(os.path.join(project_root, ".env.example"), env_file)
        print("👉 Please edit the .env file and add your OPENAI_API_KEY.")

    # 4. Start Server
    print("\n[3/4] Starting Application Server...")
    port = 5000
    if is_port_in_use(port):
        print(f"❌ Error: Port {port} is already in use!")
        sys.exit(1)

    # Start uvicorn in a separate process
    print(f"\n✅ Server starting at http://localhost:{port}")
    print("--- SERVER LOGS ---")
    
    # Browser opener thread simulation
    def open_browser():
        time.sleep(3)
        print("\n🌍 Opening browser...")
        webbrowser.open(f"http://localhost:{port}")

    # Start the server
    try:
        # Import and run here to keep it simple, but use subprocess to ensure venv is used
        server_process = subprocess.Popen(
            [python_exe, "run.py"],
            cwd=project_root
        )
        
        # Open browser after a short delay
        open_browser()
        
        # Wait for server process
        server_process.wait()
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server_process.terminate()

if __name__ == "__main__":
    main()
