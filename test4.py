import subprocess
import sys

def enable_ps_remoting():
    """Enables PowerShell Remoting and sets execution policy to RemoteSigned."""

    try:
        # Enable PSRemoting
        subprocess.run(["Enable-PSRemoting", "-Force"], shell=True, check=True, text=True)
        print("PowerShell Remoting enabled successfully.")

        # Set Execution Policy to RemoteSigned
        subprocess.run(["Set-ExecutionPolicy", "RemoteSigned", "-Scope", "LocalMachine", "-Force"], shell=True, check=True, text=True)
        print("Execution Policy set to RemoteSigned successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error enabling remoting or setting execution policy: {e}")
        print(f"Stdout: {e.stdout}") # Print stdout for debugging
        print(f"Stderr: {e.stderr}") # Print stderr for debugging
        return 1  # Indicate an error

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return 1 # Indicate an error

    return 0  # Indicate success


if __name__ == "__main__":
    result = enable_ps_remoting()
    sys.exit(result)  # Exit with the return code from the function