import winshell
import os
import servicemanager
import win32serviceutil
import win32service

class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MyStartupService"  # Service name
    _svc_display_name_ = "My Startup Service"  # Service display name
    _svc_description_ = "This service runs my_program.exe at startup." # Service description

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True
        self.exe_path = r"C:\path\to\your\my_program.exe"  # Path to your .exe
        self.log_file = r"C:\path\to\your\log_file.txt" # Path to log file

    def SvcDoRun(self):
        self.log("Service started.")
        try:
            # Check if the .exe exists
            if not os.path.exists(self.exe_path):
                self.log(f"Error: Executable not found at {self.exe_path}")
                self.SvcStop()  # Stop the service if the executable is missing
                return

            # Run the executable
            self.log(f"Running: {self.exe_path}")
            os.startfile(self.exe_path)  # Or subprocess.Popen for more control

            while self.is_running: #keep the service running to prevent it from stopping
                time.sleep(1) #sleep for 1 sec
        except Exception as e:
            self.log(f"Error running executable: {e}")
            self.SvcStop()

    def SvcStop(self):
        self.log("Service stopping.")
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)
        self.log("Service stopped.")

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp}: {message}\n")


if __name__ == '__main__':
    import win32event
    import time
    import datetime

    # Handle service installation/removal
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.StartServiceCtrlDispatcher([MyService._svc_name_, MyService])
    else:
        win32serviceutil.HandleCommandLine(MyService)