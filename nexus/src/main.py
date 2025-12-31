import subprocess
import threading
import time
import os
import socket

ip = socket.gethostbyname(socket.gethostname())

class Main:
    def __init__(self):
        os.makedirs('data', exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        self.server_process = None
    
    def start_server(self):
        print("Starting Nexus Server...")
        self.server_process = subprocess.Popen(['python3', 'server.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        time.sleep(3)
        print(f"Server is OK: {ip}:5000")
    
    def run(self):
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()
        
        time.sleep(5)
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nServer stopped!")
            if self.server_process:
                self.server_process.terminate()
            exit()

if __name__ == "__main__":
    app = Main()
    app.run()