import os
from fastapi import HTTPException
from app.logger import get_logger

logger = get_logger()

def scan_file(clamd_client, file_path: str):
    try:
        result = clamd_client.scan(file_path)
        logger.info(f"Raw ClamAV result: {result}")
        if not result:
            return {"scan_status": "unknown", "clamav_response": "no response"}
        status = list(result.values())[0][0]
        return {"scan_status": status.lower(), "clamav_response": str(result)}
    except Exception as e:
        logger.error(f"ClamAV scan failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="ClamAV scan failed")

def delete_temp_file(file_path: str):
    try:
        os.remove(file_path)
    except Exception as e:
        logger.warning(f"Failed to delete temp file {file_path}: {e}")
