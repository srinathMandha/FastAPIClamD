import os
import glob
import shutil
import subprocess
import clamd
from .exceptions import ClamAVException, ArchiveException, FileTooBigException

# Load max scan size (default 4 GB)
MAX_BYTES = int(os.getenv("MAX_BYTES", "4000000000"))

CLEAN = "CLEAN"
INFECTED = "INFECTED"
ERROR = "ERROR"


def delete(path: str):
    """Delete file or folder recursively."""
    if os.path.exists(path):
        for obj in glob.glob(os.path.join(path, "*")):
            if os.path.isdir(obj):
                shutil.rmtree(obj, ignore_errors=True)
            else:
                try:
                    os.remove(obj)
                except OSError:
                    pass
        shutil.rmtree(path, ignore_errors=True)


def expand_if_large_archive(file_path: str, download_path: str):
    """
    If the file is an archive and exceeds MAX_BYTES, extract it.
    Uses 7zip for expansion.
    """
    size = os.path.getsize(file_path)
    if size > MAX_BYTES:
        command = ["7za", "x", "-y", f"{file_path}", f"-o{download_path}"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode not in [0, 1]:
            raise ArchiveException(f"7za exited with code {result.returncode}")
        os.remove(file_path)
        for root, _, files in os.walk(download_path):
            for name in files:
                path = os.path.join(root, name)
                if os.path.getsize(path) > MAX_BYTES:
                    raise FileTooBigException(f"File {name} exceeds {MAX_BYTES} bytes")


def scan_with_clamd(file_path: str, host: str, port: int):
    """
    Scan the given file using clamd daemon.
    Returns CLEAN or INFECTED based on clamd response.
    """
    try:
        cd = clamd.ClamdNetworkSocket(host=host, port=port)
        with open(file_path, "rb") as f:
            result = cd.instream(f)
        status = result.get("stream")[0]
        return CLEAN if status == "OK" else INFECTED
    except Exception as e:
        raise ClamAVException(str(e))
