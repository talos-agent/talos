# Cryptography Commands

The Talos CLI provides cryptographic operations for secure key management, encryption, and decryption using industry-standard RSA encryption.

## Overview

The cryptography commands enable:
- RSA key pair generation
- Public key retrieval and sharing
- Data encryption using public keys
- Data decryption using private keys
- Secure key storage and management

## Commands

### `generate-keys` - Generate RSA Key Pair

Generate a new RSA key pair for encryption and decryption operations.

**Usage:**
```bash
uv run talos generate-keys
```

**Options:**
- `--key-size`: RSA key size in bits (default: 2048, options: 1024, 2048, 4096)
- `--output-dir`: Directory to store keys (default: `.keys/`)
- `--overwrite`: Overwrite existing keys if they exist

**Examples:**
```bash
# Generate default 2048-bit keys
uv run talos generate-keys

# Generate high-security 4096-bit keys
uv run talos generate-keys --key-size 4096

# Generate keys in custom directory
uv run talos generate-keys --output-dir /secure/keys/

# Overwrite existing keys
uv run talos generate-keys --overwrite
```

**Output:**
```
=== RSA Key Generation ===

Key Size: 2048 bits
Output Directory: .keys/

✅ Private key generated: .keys/private_key.pem
✅ Public key generated: .keys/public_key.pem

Key fingerprint: SHA256:abc123def456...

⚠️  Security Notice:
- Keep your private key secure and never share it
- The public key can be safely shared with others
- Back up your keys in a secure location
```

**Generated Files:**
- `private_key.pem` - Private key (keep secure)
- `public_key.pem` - Public key (can be shared)

### `get-public-key` - Retrieve Public Key

Display the current public key for sharing with others.

**Usage:**
```bash
uv run talos get-public-key
```

**Options:**
- `--format`: Output format (pem, der, base64)
- `--key-dir`: Directory containing keys (default: `.keys/`)
- `--fingerprint`: Show key fingerprint

**Examples:**
```bash
# Display public key in PEM format
uv run talos get-public-key

# Show key with fingerprint
uv run talos get-public-key --fingerprint

# Export in base64 format
uv run talos get-public-key --format base64

# Use keys from custom directory
uv run talos get-public-key --key-dir /secure/keys/
```

**Output:**
```
=== Public Key ===

-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1234567890abcdef...
...
-----END PUBLIC KEY-----

Fingerprint: SHA256:abc123def456789...
Key Size: 2048 bits
Created: 2024-01-15 10:30:00 UTC
```

### `encrypt` - Encrypt Data

Encrypt data using a public key (yours or someone else's).

**Usage:**
```bash
uv run talos encrypt "<data>" <public_key_file>
```

**Arguments:**
- `data`: Text data to encrypt
- `public_key_file`: Path to public key file

**Options:**
- `--output`: Output file for encrypted data
- `--format`: Output format (base64, hex, binary)

**Examples:**
```bash
# Encrypt a message using your own public key
uv run talos encrypt "Secret message" .keys/public_key.pem

# Encrypt using someone else's public key
uv run talos encrypt "Confidential data" /path/to/their/public_key.pem

# Save encrypted data to file
uv run talos encrypt "Important info" public_key.pem --output encrypted.txt

# Output in hex format
uv run talos encrypt "Data" public_key.pem --format hex
```

**Output:**
```
=== Encryption Complete ===

Original Data: "Secret message"
Public Key: .keys/public_key.pem
Encrypted Data (Base64):
gAAAAABhZ1234567890abcdef...

✅ Data encrypted successfully
📋 Copy the encrypted data above to share securely
```

### `decrypt` - Decrypt Data

Decrypt data using your private key.

**Usage:**
```bash
uv run talos decrypt "<encrypted_data>"
```

**Arguments:**
- `encrypted_data`: Base64-encoded encrypted data

**Options:**
- `--key-dir`: Directory containing private key (default: `.keys/`)
- `--input-file`: Read encrypted data from file
- `--format`: Input format (base64, hex, binary)

**Examples:**
```bash
# Decrypt base64-encoded data
uv run talos decrypt "gAAAAABhZ1234567890abcdef..."

# Decrypt from file
uv run talos decrypt --input-file encrypted.txt

# Decrypt hex-encoded data
uv run talos decrypt "48656c6c6f20576f726c64" --format hex

# Use private key from custom directory
uv run talos decrypt "encrypted_data" --key-dir /secure/keys/
```

**Output:**
```
=== Decryption Complete ===

Encrypted Data: gAAAAABhZ1234567890abcdef...
Private Key: .keys/private_key.pem

✅ Decryption successful
Decrypted Data: "Secret message"
```

## Security Features

### Key Storage

**Default Location:**
- Keys stored in `.keys/` directory
- Private key permissions set to 600 (owner read/write only)
- Public key permissions set to 644 (world readable)

**Security Measures:**
- Private keys never transmitted or logged
- Secure random number generation
- Industry-standard RSA implementation
- Automatic permission setting

### Encryption Standards

**RSA Configuration:**
- PKCS#1 OAEP padding
- SHA-256 hash function
- MGF1 mask generation
- Secure random padding

**Key Sizes:**
- 1024-bit: Legacy support (not recommended)
- 2048-bit: Standard security (recommended)
- 4096-bit: High security (slower performance)

## Advanced Usage

### Secure Communication Workflow

**Setup (one time):**
```bash
# Generate your key pair
uv run talos generate-keys --key-size 2048

# Share your public key
uv run talos get-public-key > my_public_key.pem
```

**Sending encrypted messages:**
```bash
# Encrypt message for recipient
uv run talos encrypt "Confidential message" recipient_public_key.pem

# Send the encrypted output to recipient
```

**Receiving encrypted messages:**
```bash
# Decrypt received message
uv run talos decrypt "received_encrypted_data"
```

### Batch Operations

**Encrypt multiple files:**
```bash
#!/bin/bash
# encrypt-files.sh

public_key="recipient_public_key.pem"

for file in *.txt; do
  echo "Encrypting $file..."
  content=$(cat "$file")
  encrypted=$(uv run talos encrypt "$content" "$public_key")
  echo "$encrypted" > "$file.encrypted"
done
```

**Decrypt multiple messages:**
```bash
#!/bin/bash
# decrypt-messages.sh

for encrypted_file in *.encrypted; do
  echo "Decrypting $encrypted_file..."
  encrypted_data=$(cat "$encrypted_file")
  decrypted=$(uv run talos decrypt "$encrypted_data")
  echo "$decrypted" > "${encrypted_file%.encrypted}.decrypted"
done
```

### Integration with Other Commands

**Secure GitHub token storage:**
```bash
# Encrypt your GitHub token
encrypted_token=$(uv run talos encrypt "$GITHUB_API_TOKEN" public_key.pem)

# Store encrypted token safely
echo "$encrypted_token" > github_token.encrypted

# Later, decrypt when needed
GITHUB_API_TOKEN=$(uv run talos decrypt "$(cat github_token.encrypted)")
```

## Configuration

### Key Management Settings

```yaml
cryptography:
  key_storage:
    directory: ".keys"
    private_key_permissions: "600"
    public_key_permissions: "644"
    backup_enabled: true
    backup_directory: ".keys/backup"
  
  encryption:
    default_key_size: 2048
    padding: "OAEP"
    hash_algorithm: "SHA256"
    mgf: "MGF1"
  
  security:
    secure_delete: true
    audit_operations: true
    require_confirmation: ["generate-keys --overwrite"]
```

### Backup Configuration

```yaml
cryptography:
  backup:
    enabled: true
    schedule: "daily"
    retention_days: 30
    encryption: true
    remote_backup:
      enabled: false
      provider: "s3"
      bucket: "secure-key-backup"
```

## Error Handling

### Common Issues

**Missing Keys:**
```
Error: Private key not found at .keys/private_key.pem
Solution: Run 'uv run talos generate-keys' to create keys
```

**Invalid Encrypted Data:**
```
Error: Failed to decrypt data - invalid format
Solution: Verify encrypted data is complete and in correct format
```

**Permission Denied:**
```
Error: Permission denied accessing private key
Solution: Check file permissions or run with appropriate privileges
```

**Key Size Mismatch:**
```
Error: Data too large for key size
Solution: Use larger key size or encrypt smaller data chunks
```

### Security Warnings

**Weak Key Size:**
```
Warning: 1024-bit keys are not recommended for new applications
Recommendation: Use 2048-bit or larger keys
```

**Insecure Storage:**
```
Warning: Private key has insecure permissions
Action: Automatically fixing permissions to 600
```

## Best Practices

### Key Management

**Generation:**
- Use 2048-bit keys minimum for new applications
- Generate keys on secure, trusted systems
- Use hardware security modules for high-value keys

**Storage:**
- Keep private keys secure and never share them
- Back up keys in multiple secure locations
- Use encrypted storage for key backups
- Regularly rotate keys for long-term use

**Distribution:**
- Public keys can be shared freely
- Verify public key authenticity through secure channels
- Use key fingerprints to verify key integrity

### Operational Security

**Data Handling:**
- Encrypt sensitive data before storage or transmission
- Use secure channels for sharing encrypted data
- Verify decryption results before acting on them
- Clear sensitive data from memory after use

**Access Control:**
- Limit access to private keys
- Use principle of least privilege
- Monitor key usage and access
- Implement key escrow for critical applications

**Compliance:**
- Follow organizational security policies
- Meet regulatory requirements for data protection
- Document key management procedures
- Regular security audits and reviews

The cryptography commands provide enterprise-grade security for protecting sensitive data and communications within the Talos ecosystem.
