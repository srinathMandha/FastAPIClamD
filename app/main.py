from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.utils import scan_file, delete_temp_file
from app.config import settings
from app.logger import get_logger
import clamd
import tempfile
import os
import time

app = FastAPI(title="ClamAV FastAPI Scanner", version="1.0")
logger = get_logger()

clamd_client = clamd.ClamdUnixSocket(path=settings.CLAMD_SOCKET)

@app.get("/health")
def health_check():
    logger.info("Health check initiated")
    try:
        pong = clamd_client.ping()
        if pong == "PONG":
            logger.info("Health check successful — ClamAV is running")
            return JSONResponse({"status": "healthy", "clamd_status": "running"})
    except Exception as e:
        logger.error(f"Health check failed — ClamAV not reachable: {str(e)}")
        raise HTTPException(status_code=503, detail="ClamAV daemon not reachable")
    return JSONResponse({"status": "unhealthy"})

@app.post("/scan")
def scan_uploaded_file(file: UploadFile = File(...)):
    start_time = time.time()
    logger.info(f"Received file '{file.filename}' for scanning")

    try:
        os.makedirs(settings.CLAMAV_SCAN_PATH, exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=settings.CLAMAV_SCAN_PATH) as tmp:
            content = file.file.read()
            tmp.write(content)
            temp_path = tmp.name
            file_size = os.path.getsize(temp_path)
            logger.info(f"File saved temporarily: {temp_path} ({file_size} bytes)")

        logger.info(f"Started ClamAV scan for: {temp_path}")
        scan_result = scan_file(clamd_client, temp_path)
        status = scan_result["scan_status"].upper()
        logger.info(f"Scan result for '{file.filename}': {status}")

        delete_temp_file(temp_path)
        logger.info(f"Temporary file deleted: {temp_path}")

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Scan completed in {elapsed}s for file: {file.filename}")

        return {"file_name": file.filename, "status": status, "message": scan_result["clamav_response"]}
    except Exception as e:
        logger.error(f"Error scanning {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during scan")
    finally:
        file.file.close()
