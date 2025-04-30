import sys
import platform
import pkg_resources

def main():
    # Print Python version information
    print(f"Python version: {platform.python_version()}")
    print(f"Python executable: {sys.executable}")
    
    # Print installed packages
    print("\nInstalled packages:")
    installed_packages = sorted([f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set])
    for package in installed_packages:
        print(f"  {package}")

if __name__ == "__main__":
    main()