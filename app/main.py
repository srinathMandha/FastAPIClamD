import os
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from .utils import scan_with_clamd, delete, expand_if_large_archive
from .exceptions import ClamAVException, ArchiveException, FileTooBigException
import clamd

app = FastAPI(title="ClamAV Scanning API", version="1.0")

EFS_MOUNT_PATH = os.getenv("EFS_MOUNT_PATH", "/clamav")
EFS_DEF_PATH = os.getenv("EFS_DEF_PATH", "defs")
CLAMD_HOST = os.getenv("CLAMD_HOST", "localhost")
CLAMD_PORT = int(os.getenv("CLAMD_PORT", "3310"))


@app.get("/health")
def health_check():
    try:
        cd = clamd.ClamdNetworkSocket(host=CLAMD_HOST, port=CLAMD_PORT)
        ping = cd.ping()
        if ping == "PONG":
            return {"status": "HEALTHY", "clamd": "RUNNING"}
        return {"status": "UNHEALTHY", "clamd": "NOT RESPONDING"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/scan")
def scan_file(file: UploadFile = File(...)):
    try:
        mount_path = EFS_MOUNT_PATH
        definitions_path = f"{mount_path}/{EFS_DEF_PATH}"
        payload_path = f"{mount_path}/{file.filename}"

        os.makedirs(payload_path, exist_ok=True)
        os.makedirs(definitions_path, exist_ok=True)

        file_path = os.path.join(payload_path, file.filename)
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)

        expand_if_large_archive(file_path, payload_path)

        status = scan_with_clamd(file_path, CLAMD_HOST, CLAMD_PORT)

        delete(payload_path)
        return {"file_name": file.filename, "status": status, "message": f"File {status}"}

    except (ClamAVException, ArchiveException, FileTooBigException) as e:
        delete(payload_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        delete(payload_path)
        raise HTTPException(status_code=500, detail=str(e))
