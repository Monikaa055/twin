import os
import shutil
import zipfile
import subprocess
import sys


def check_docker_available():
    """Check if Docker is available and running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def install_dependencies_docker():
    """Install dependencies using Docker with Lambda runtime image."""
    print("Installing dependencies for Lambda runtime using Docker...")
    
    # Use the official AWS Lambda Python 3.12 image
    # This ensures compatibility with Lambda's runtime environment
    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{os.getcwd()}:/var/task",
            "--platform",
            "linux/amd64",  # Force x86_64 architecture
            "--entrypoint",
            "",  # Override the default entrypoint
            "public.ecr.aws/lambda/python:3.12",
            "/bin/sh",
            "-c",
            "pip install --target /var/task/lambda-package -r /var/task/requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: --upgrade",
        ],
        check=True,
    )


def check_uv_available():
    """Check if uv is available."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def install_dependencies_local():
    """Install dependencies using local pip (fallback method)."""
    print("Installing dependencies using local pip (fallback method)...")
    print("⚠️  WARNING: This may not guarantee Lambda runtime compatibility.")
    print("   For best results, use Docker when available.\n")
    
    # Try uv pip first (since this project uses uv)
    if check_uv_available():
        print("Using uv pip...")
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "--target",
                "lambda-package",
                "-r",
                "requirements.txt",
                "--upgrade",
            ],
            check=True,
        )
    else:
        # Fall back to regular pip
        print("Using system pip...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--target",
                "lambda-package",
                "-r",
                "requirements.txt",
                "--upgrade",
            ],
            check=True,
        )


def main():
    print("Creating Lambda deployment package...")

    # Clean up
    if os.path.exists("lambda-package"):
        shutil.rmtree("lambda-package")
    if os.path.exists("lambda-deployment.zip"):
        os.remove("lambda-deployment.zip")

    # Create package directory
    os.makedirs("lambda-package")

    # Install dependencies
    if check_docker_available():
        try:
            install_dependencies_docker()
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Docker command failed: {e}")
            print("\nFalling back to local pip installation...")
            install_dependencies_local()
    else:
        print("⚠️  Docker is not available or not running.")
        print("   Attempting to use local pip installation instead...")
        print("   Note: For best Lambda compatibility, please start Docker and try again.\n")
        install_dependencies_local()

    # Copy application files
    print("Copying application files...")
    for file in ["server.py", "lambda_handler.py", "context.py", "resources.py"]:
        if os.path.exists(file):
            shutil.copy2(file, "lambda-package/")
    
    # Copy data directory
    if os.path.exists("data"):
        shutil.copytree("data", "lambda-package/data")

    # Create zip
    print("Creating zip file...")
    with zipfile.ZipFile("lambda-deployment.zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk("lambda-package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "lambda-package")
                zipf.write(file_path, arcname)

    # Show package size
    size_mb = os.path.getsize("lambda-deployment.zip") / (1024 * 1024)
    print(f"✓ Created lambda-deployment.zip ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()