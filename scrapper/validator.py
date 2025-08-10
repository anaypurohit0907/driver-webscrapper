import hashlib

def validate_file_integrity(file_path, expected_hash):
    """
    Validate the integrity of a file using its hash.

    Args:
        file_path (str): Path to the file.
        expected_hash (str): Expected hash value.

    Returns:
        bool: True if the file's hash matches the expected hash, False otherwise.
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash
