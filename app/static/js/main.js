
document.addEventListener('DOMContentLoaded', function() {
    const toast = new bootstrap.Toast(document.getElementById('toast'));
    let currentPublicKey = '';
    let currentPrivateKey = '';



    // Initialize auto-resize for all textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        // Set initial height
        autoResizeTextarea(textarea);
        
        // Add input event listener
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    });

    function showToast(message, success = true) {
        const toastElement = document.getElementById('toast');
        toastElement.querySelector('.toast-body').textContent = message;
        toastElement.classList.remove('bg-success', 'bg-danger');
        toastElement.classList.add(success ? 'bg-success' : 'bg-danger');
        toast.show();
    }

    // Generate Keys
    document.getElementById('generateKeys').addEventListener('click', async () => {
        try {
            const response = await fetch('/generate-keys', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (response.ok) {
                currentPublicKey = data.public_key;
                currentPrivateKey = data.secret_key;
                
                const publicKeyTextarea = document.getElementById('publicKey');
                const privateKeyTextarea = document.getElementById('privateKey');
                const keyDisplay = document.getElementById('keyDisplay');
                
                publicKeyTextarea.value = data.public_key;
                privateKeyTextarea.value = data.secret_key;
                
                // Show the key display first
                keyDisplay.style.display = 'block';
                
                // Small delay to ensure the display is visible before resizing
                setTimeout(() => {
                    autoResizeTextarea(publicKeyTextarea);
                    autoResizeTextarea(privateKeyTextarea);
                }, 50);
                
                showToast('Keys generated successfully!');
            } else {
                throw new Error(data.detail || 'Failed to generate keys');
            }
        } catch (error) {
            showToast(error.message, false);
        }
    });

    // Encrypt Message
    document.getElementById('encryptMessage').addEventListener('click', async () => {
        const message = document.getElementById('messageToEncrypt').value;
        if (!message) {
            showToast('Please enter a message to encrypt', false);
            return;
        }
        if (!currentPublicKey) {
            showToast('Please generate keys first', false);
            return;
        }

        try {
            const response = await fetch('/encrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    public_key: currentPublicKey
                })
            });
            const data = await response.json();
            
            if (response.ok) {
                const encryptedDataTextarea = document.getElementById('encryptedData');
                const kemCiphertextTextarea = document.getElementById('kemCiphertext');
                const encryptionResult = document.getElementById('encryptionResult');
                
                encryptedDataTextarea.value = data.iv_ciphertext;
                kemCiphertextTextarea.value = data.ciphertext;
                
                // Show the result first
                encryptionResult.style.display = 'block';
                
                // Small delay to ensure the display is visible before resizing
                setTimeout(() => {
                    autoResizeTextarea(encryptedDataTextarea);
                    autoResizeTextarea(kemCiphertextTextarea);
                }, 50);
                
                showToast('Message encrypted successfully!');
            } else {
                throw new Error(data.detail || 'Failed to encrypt message');
            }
        } catch (error) {
            showToast(error.message, false);
        }
    });

    // Decrypt Message
    document.getElementById('decryptMessage').addEventListener('click', async () => {
        const encryptedData = document.getElementById('dataToDecrypt').value;
        const kemCiphertext = document.getElementById('kemCiphertextToDecrypt').value;
        
        if (!encryptedData || !kemCiphertext) {
            showToast('Please enter both encrypted data and KEM ciphertext', false);
            return;
        }
        if (!currentPrivateKey) {
            showToast('Please generate keys first', false);
            return;
        }

        try {
            const response = await fetch('/decrypt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    iv_ciphertext: encryptedData,
                    ciphertext: kemCiphertext,
                    secret_key: currentPrivateKey
                })
            });
            const data = await response.json();
            
            if (response.ok) {
                const decryptedMessageTextarea = document.getElementById('decryptedMessage');
                const decryptionResult = document.getElementById('decryptionResult');
                
                decryptedMessageTextarea.value = data.message;
                
                // Show the result first
                decryptionResult.style.display = 'block';
                
                // Small delay to ensure the display is visible before resizing
                setTimeout(() => {
                    autoResizeTextarea(decryptedMessageTextarea);
                }, 50);
                
                showToast('Message decrypted successfully!');
            } else {
                throw new Error(data.detail || 'Failed to decrypt message');
            }
        } catch (error) {
            showToast(error.message, false);
        }
    });

    // Copy buttons functionality
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('click', function() {
            if (this.readOnly) {
                this.select();
                navigator.clipboard.writeText(this.value);
                showToast('Copied to clipboard!');
            }
        });
    });
}); 
