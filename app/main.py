from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic
from pydantic import BaseModel
import base64
import logging
from . import crypto_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quantum-Safe Encryption Demo")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")



# Models
class EncryptRequest(BaseModel):
    message: str
    public_key: str

class DecryptRequest(BaseModel):
    ciphertext: str
    iv_ciphertext: str
    secret_key: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-keys")
async def generate_keys():
    try:
        logger.info("Starting key generation process...")
        public_key, secret_key = crypto_utils.generate_keys()
        logger.info(f"Generated public key length: {len(public_key)} bytes")
        logger.info(f"Generated secret key length: {len(secret_key)} bytes")
        logger.info("Key generation completed successfully")
        return {
            "public_key": base64.b64encode(public_key).decode(),
            "secret_key": base64.b64encode(secret_key).decode()
        }
    except Exception as e:
        logger.error(f"Key generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/encrypt")
async def encrypt(request: EncryptRequest):
    try:
        logger.info("Starting encryption process...")
        logger.info(f"Original message: {request.message}")
        logger.info(f"Message length: {len(request.message)} bytes")
        
        public_key = base64.b64decode(request.public_key)
        logger.info(f"Using public key of length: {len(public_key)} bytes")
        
        # Encapsulate shared secret
        logger.info("Performing KEM encapsulation...")
        ciphertext, shared_secret = crypto_utils.encapsulate(public_key)
        logger.info(f"Generated ciphertext length: {len(ciphertext)} bytes")
        logger.info(f"Generated shared secret length: {len(shared_secret)} bytes")
        
        # Encrypt the message using AES
        logger.info("Encrypting message with AES using shared secret...")
        encrypted_message = crypto_utils.aes_encrypt(shared_secret, request.message)
        logger.info(f"Encrypted message length: {len(encrypted_message)} bytes")
        logger.info("Encryption process completed successfully")
        
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "iv_ciphertext": base64.b64encode(encrypted_message).decode()
        }
    except Exception as e:
        logger.error(f"Encryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/decrypt")
async def decrypt(request: DecryptRequest):
    try:
        logger.info("Starting decryption process...")
        
        secret_key = base64.b64decode(request.secret_key)
        ciphertext = base64.b64decode(request.ciphertext)
        iv_ciphertext = base64.b64decode(request.iv_ciphertext)
        
        logger.info(f"Using secret key of length: {len(secret_key)} bytes")
        logger.info(f"Received ciphertext length: {len(ciphertext)} bytes")
        logger.info(f"Received encrypted message length: {len(iv_ciphertext)} bytes")
        
        # Decapsulate shared secret
        logger.info("Performing KEM decapsulation...")
        shared_secret = crypto_utils.decapsulate(secret_key, ciphertext)
        logger.info(f"Recovered shared secret length: {len(shared_secret)} bytes")
        
        # Decrypt the message using AES
        logger.info("Decrypting message with AES using shared secret...")
        decrypted_message = crypto_utils.aes_decrypt(shared_secret, iv_ciphertext)
        logger.info(f"Decrypted message: {decrypted_message}")
        logger.info(f"Decrypted message length: {len(decrypted_message)} bytes")
        logger.info("Decryption process completed successfully")
        
        return {"message": decrypted_message}
    except Exception as e:
        logger.error(f"Decryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
