import os

class Settings:
    CLAMAV_DB_DIR = os.getenv("CLAMAV_DB_DIR", "/defs")
    CLAMAV_SCAN_PATH = os.getenv("CLAMAV_SCAN_PATH", "/clamav")
    MAX_BYTES = int(os.getenv("MAX_BYTES", "4000000000"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    CLAMD_SOCKET = os.getenv("CLAMD_SOCKET", "/tmp/clamd.socket")

settings = Settings()
