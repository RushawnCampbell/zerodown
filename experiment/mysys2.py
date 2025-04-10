import requests
import subprocess
import os, time

msys2_url = "https://github.com/msys2/msys2-installer/releases/download/2025-02-21/msys2-x86_64-20250221.exe"
msys2_installer = "msys2-installer.exe"
msys2_install_path = "C:\\msys64"  # Default installation path

def add_to_path(path):
    """Adds a path to the system's PATH environment variable."""
    try:
        subprocess.run(["setx", "PATH", f"{os.environ['PATH']};{path}"], shell=True)
        return True
    except Exception as e:
        print(f"Error adding to PATH: {e}")
        return False

def install_msys2_and_rsync():
    """Downloads, installs MSYS2, and installs rsync."""
    try:
        # Download MSYS2 installer
        print("Downloading MSYS2 installer...")
        response = requests.get(msys2_url)
        response.raise_for_status()

        with open(msys2_installer, "wb") as f:
            f.write(response.content)

        # Install MSYS2
        print("Installing MSYS2...")
        subprocess.run([msys2_installer, "/SILENT", f"/DIR={msys2_install_path}"])
        os.remove(msys2_installer)

        # Add MSYS2 bin to PATH
        msys2_bin_path = os.path.join(msys2_install_path, "usr", "bin")
        print(f"Adding {msys2_bin_path} to PATH...")
        if not add_to_path(msys2_bin_path):
            print("Warning: Failed to add MSYS2 to PATH. You may need to add it manually.")

        #Install rsync
        print("Installing rsync...")
        subprocess.run([os.path.join(msys2_install_path, "usr", "bin", "pacman.exe"), "-S", "--noconfirm", "rsync"])

        print("MSYS2 and rsync installed successfully.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading installer: {e}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error during installation: {e}")
        return False
    except FileNotFoundError as e:
        print(f"File Not Found Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    install_msys2_and_rsync()
    time.sleep(20)