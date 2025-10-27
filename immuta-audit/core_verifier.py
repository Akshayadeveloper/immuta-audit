
import json
import hashlib
from typing import Any, Union, Dict, List

def deep_hash(data: Any) -> str:
    """
    Recursively generates an SHA-256 hash for any arbitrary complex data structure
    (dictionaries, lists, primitives), guaranteeing structural immutability check.
    """
    data_type = type(data)
    
    if data_type in (int, float, str, bool, type(None)):
        # Primitives are hashed directly after conversion to string
        return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

    if data_type is list:
        # Sorts list contents by their hash to ensure list order doesn't change hash
        # unless elements themselves change.
        item_hashes = [deep_hash(item) for item in data]
        # Hash the concatenated, sorted hashes
        return hashlib.sha256("".join(sorted(item_hashes)).encode('utf-8')).hexdigest()

    if data_type is dict:
        # Dictionaries are canonicalized (sorted by key) before hashing
        sorted_items = []
        for key in sorted(data.keys()):
            # Hash key and value separately, then combine
            key_hash = deep_hash(key)
            value_hash = deep_hash(data[key])
            sorted_items.append(f"{key_hash}:{value_hash}")
        
        return hashlib.sha256("".join(sorted_items).encode('utf-8')).hexdigest()

    if hasattr(data, '__dict__'):
        # Handle custom objects by hashing their dictionary representation
        return deep_hash(data.__dict__)

    # Fallback for unexpected types (like sets)
    return hashlib.sha256(repr(data).encode('utf-8')).hexdigest()


class StateAuditor:
    def __init__(self, initial_state: Any):
        """Initializes with the desired immutable state and calculates its signature."""
        self.initial_state = initial_state
        self.initial_signature = deep_hash(initial_state)

    def verify(self, current_state: Any) -> bool:
        """Verifies if the current state structurally matches the initial signature."""
        current_signature = deep_hash(current_state)
        if current_signature == self.initial_signature:
            print("✅ State integrity verified. Object remains immutable.")
            return True
        else:
            print("❌ IMMUTABILITY BREACH DETECTED. State signature mismatch.")
            return False

# --- Demonstration ---

# 1. Define a complex initial state (e.g., a microservice config object)
user_data = {
    "id": 101,
    "settings": {"mode": "stable", "version": 1.0},
    "history": [1640995200, 1640995200]
}

auditor = StateAuditor(user_data)
print(f"Initial Signature: {auditor.initial_signature}")

# 2. Simulate a read operation that shouldn't mutate the data
copied_data = json.loads(json.dumps(user_data)) 
auditor.verify(copied_data)

# 3. Simulate an illegal mutation (e.g., side effect in a thread)
user_data["settings"]["mode"] = "unstable"
auditor.verify(user_data)
