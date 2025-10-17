#!/usr/bin/env python3
import hashlib
import os
import sys
import argparse
from ecdsa import SECP256k1, SigningKey, VerifyingKey, util

def main():
    parser = argparse.ArgumentParser(description="Gera um endereço Taproot com um script de 'reencarnação'.")
    parser.add_argument(
        "-s", "--secret-key",
        type=str,
        help="A chave secreta em hexadecimal. Se não for fornecida, uma nova será gerada."
    )
    parser.add_argument(
        "-m", "--message",
        type=str,
        default="Eu reencarnei na blockchain",
        help="A mensagem secreta a ser usada no script leaf."
    )
    args = parser.parse_args()

    # ---------- 1. Parâmetros da curva ----------
curve = SECP256k1
G = curve.generator
p = curve.curve.p()
n = curve.order

def int_to_bytes(i, length):
    return i.to_bytes(length, 'big')

def bytes_to_int(b):
    return int.from_bytes(b, 'big')

    # ---------- 2. Chave interna (simulada ou gerada) ----------
    if args.secret_key:
        sk_int_hex = args.secret_key
        print("🔑 Usando chave secreta fornecida.")
    else:
        sk_int_bytes = os.urandom(32)
        sk_int_hex = sk_int_bytes.hex()
        print("🔑 Gerando nova chave secreta.")

    print("   Secret Key (hex):", sk_int_hex)
    sk_int = int(sk_int_hex, 16)

    vk_int = SigningKey.from_secret_exponent(sk_int, curve=curve).verifying_key
    Q_int_bytes = b'\x02' + int_to_bytes(vk_int.pubkey.point.x(), 32) if vk_int.pubkey.point.y() % 2 == 0 else b'\x03' + int_to_bytes(vk_int.pubkey.point.x(), 32)
    print("   Public Key (compressa):", Q_int_bytes.hex())

    # ---------- 3. Mensagem e hash ----------
    M = args.message.encode('utf-8')
    hM = hashlib.sha256(M).digest()
    print("\n🗒️  Mensagem:", args.message)
    print("   Hash (SHA256):", hM.hex())

    # ---------- 4. Script leaf ----------
# Estrutura: <pubkey_int> OP_CHECKSIGVERIFY OP_PUSH32 <hash(M)> OP_EQUAL
# Opcodes:
OP_CHECKSIGVERIFY = b'\xac'   # 0xac
OP_EQUAL          = b'\x87'   # 0x87
OP_PUSH32         = b'\x20'   # 0x20 (push next 32 bytes)

leaf = (
    Q_int_bytes +               # 33 bytes (pubkey)
    OP_CHECKSIGVERIFY +        # 1 byte
    OP_PUSH32 + hM +            # 1 + 32 bytes
    OP_EQUAL                    # 1 byte
)
print("\n📜 Script leaf (hex) :", leaf.hex())

# ---------- 5. Hash da leaf (TapLeaf) ----------
# TapLeaf = 0x00 || varint(len(leaf)) || leaf
def varint_encode(i):
    if i < 0xfd:
        return i.to_bytes(1, 'little')
    elif i <= 0xffff:
        return b'\xfd' + i.to_bytes(2, 'little')
    elif i <= 0xffffffff:
        return b'\xfe' + i.to_bytes(4, 'little')
    else:
        return b'\xff' + i.to_bytes(8, 'little')

leaf_hash = hashlib.sha256(
    b'\xc0' +                     # 0xc0 = leaf version (BIP‑342)
    varint_encode(len(leaf)) +
    leaf
).digest()
print("\n🔎 TapLeaf hash (SHA256) :", leaf_hash.hex())

# ---------- 6. Taproot tweak ----------
# t = SHA256( tapTweak || X || leaf_hash )  where tapTweak = b'\x01'
tap_tweak_prefix = b'\x01'
tweak = hashlib.sha256(
    tap_tweak_prefix +
    Q_int_bytes +
    leaf_hash
).digest()
t_int = bytes_to_int(tweak) % n
print("\n🛠️ Tweak (int) :", t_int)

# ---------- 7. Chave de saída (taproot) ----------
# Q_out = Q_int + t·G  (point addition)
Q_int_point = vk_int.pubkey.point
Q_out_point = Q_int_point + t_int * G

# Codifica ponto comprimido
Q_out_bytes = (b'\x02' if Q_out_point.y() % 2 == 0 else b'\x03') + int_to_bytes(Q_out_point.x(), 32)
print("\n🔐 Chave de saída taproot (compressa) :", Q_out_bytes.hex())

# ---------- 8. Endereço bech32m ----------
# Bech32m encoding (BIP‑350).  We'll implement a minimal encoder.
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    """Internal function that computes the Bech32 checksum."""
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = (chk >> 25)
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data, spec='bech32m'):
    values = bech32_hrp_expand(hrp) + data
    const = 0x2bc830a3 if spec == 'bech32m' else 1
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ const
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data, spec='bech32m'):
    combined = data + bech32_create_checksum(hrp, data, spec)
    return hrp + '1' + ''.join([CHARSET[d] for d in combined])

def convertbits(data, frombits, tobits, pad=True):
    """General power-of-2 base conversion."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        if value < 0 or (value >> frombits):
            raise ValueError("Invalid data range")
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        raise ValueError("Invalid padding")
    return ret

# Witness program: version 1 (0x01) + 32‑byte x‑coordinate
witver = 0x01
witprog = Q_out_bytes[1:]   # only x‑coordinate (32 bytes)
bech32_data = [witver] + convertbits(witprog, 8, 5)
address = bech32_encode('bc', bech32_data, spec='bech32m')
print("\n🏁 Endereço Taproot (bech32m) :", address)

# ---------- 9. Exemplo de witness (gasto) ----------
# Para fins de demonstração vamos gerar uma assinatura válida da chave interna.
# Em produção você usaria a chave privada real que controla Q_int.
msg_hash = hashlib.sha256(b"dummy tx for sighash").digest()   # placeholder
# SIGHASH_ALL (0x01) – para o exemplo
sighash = int.from_bytes(msg_hash, 'big')
sig_obj = SigningKey.from_secret_exponent(sk_int, curve=curve).sign_digest(
    msg_hash,
    sigencode=util.sigencode_der_canonize
) + b'\x01'          # append SIGHASH_ALL

# Montagem do witness stack:
# 1) assinatura
# 2) mensagem original (raw, não hash)
# 3) script leaf (as above)
# 4) control block (leaf_version || internal_key || merkle_path)
leaf_version = b'\xc0'          # 0xc0 = leaf version (BIP‑342)
control_block = leaf_version + Q_int_bytes   # sem merkle_path porque só há um leaf
witness = [
    sig_obj.hex(),
    M.hex(),
    leaf.hex(),
    control_block.hex()
]
print("\n📦 Exemplo de witness (hex strings):")
for i, w in enumerate(witness, 1):
    print(f"  [{i}] {w}")

print("\n✅ Pronto! O endereço acima aceita o output Taproot. Quando quiser gastá‑lo, envie um transaction que contenha o witness acima.")

if __name__ == "__main__":
    main()