# Security Audit of the FROST Network Scanner

This document summarizes the security audit of the FROST network scanner.

## Nonce Logging

The `network-scanner.js` file does not contain any code that logs raw nonces. The `probe` method makes a GET request to the `/api/frost/info` endpoint, which does not involve a handshake. The `handshake` method is not implemented in the `network-scanner.js` file, so there is no risk of logging raw nonces.

## Secure Random Generator

The `network-scanner.js` file does not use a random number generator. The `server.js` file does not use a random number generator. Therefore, there is no risk of using an insecure random number generator.

## Conclusion

The FROST network scanner is secure with respect to the two items audited.