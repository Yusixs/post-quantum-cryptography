from pqcrypto.kem.ml_kem_512 import generate_keypair, encrypt, decrypt
# from pqcrypto.kem.mceliece8192128 import generate_keypair, encrypt, decrypt


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from secrets import compare_digest
import os

# --- KEM key operations ---
def generate_keys():
    public_key, secret_key = generate_keypair()
    return public_key, secret_key

def encapsulate(public_key: bytes):
    ciphertext, shared_secret = encrypt(public_key)
    return ciphertext, shared_secret

def decapsulate(secret_key: bytes, ciphertext: bytes):
    shared_secret = decrypt(secret_key, ciphertext)
    return shared_secret

# --- AES encryption using shared secret ---
def aes_encrypt(shared_secret: bytes, message: str):
    key = shared_secret[:32]  # Use first 256 bits
    iv = os.urandom(16)
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return iv + encrypted  # IV + ciphertext

def aes_decrypt(shared_secret: bytes, iv_ciphertext: bytes):
    key = shared_secret[:32]  # Use first 256 bits
    iv = iv_ciphertext[:16]
    ciphertext = iv_ciphertext[16:]

    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)

    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext.decode()

# --- Test KEM + AES functionality ---
if __name__ == "__main__":
    # Generate keypair
    public_key, secret_key = generate_keys()

    print(f"Keypair generated successfully: {len(public_key)} {len(secret_key)}")

    # Encapsulate shared secret
    ciphertext, shared_secret_enc = encapsulate(public_key)
    print(f"Encapsulation done: {len(ciphertext)} {len(shared_secret_enc)}")

    # Decapsulate shared secret
    shared_secret_dec = decapsulate(secret_key, ciphertext)
    print(f"Decapsulation done.")

    # Assert shared secrets match
    assert compare_digest(shared_secret_enc, shared_secret_dec), "Shared secrets do not match!"
    print(f"Shared secrets match successfully.")

    # Test AES encryption/decryption
    test_message = "This is a secret message."
    encrypted_message = aes_encrypt(shared_secret_enc, test_message)
    decrypted_message = aes_decrypt(shared_secret_dec, encrypted_message)

    assert test_message == decrypted_message, "Decrypted message does not match original!"
    print("AES encryption/decryption successful.")
    print(encrypted_message)
    print(decrypted_message)
