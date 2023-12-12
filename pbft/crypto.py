from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import hashes

import base64

# Création d'une paire de clés privée/publique
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

print(public_key)

# Message à signer
message = b"Hello, world!"

# Signature du message avec la clé privée
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

signature_base64 = base64.b64encode(signature).decode()

# Revenir en binaire à partir de la chaîne base64
signature_binary = base64.b64decode(signature_base64)

# Vérification de la signature avec la clé publique
try:
    public_key.verify(
        signature_binary,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    print("La signature est valide.")
except utils.InvalidSignature:
    print("La signature n'est pas valide.")
