import hashlib
import json

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash

    def to_dict(self):
        # Convertissez les attributs du bloc en un dictionnaire
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash
        }
    
    @property
    def current_hash(self):
        # Calculer et renvoyer le hash actuel à chaque accès
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def __str__(self):
        return f"================\n" \
               f"prev_hash:\t {self.previous_hash}\n" \
               f"Data:\t\t {self.data}\n" \
               f"Hash:\t\t {self.current_hash}\n"
    
    def to_dict(self):
        # Convertissez les attributs du bloc en un dictionnaire
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash
        }

if __name__ == "__main__": 
    block_instance = Block(index=1, timestamp="1234567890", data="Sample Data", previous_hash="0")
    block_dict = block_instance.to_dict()
    print(block_dict)