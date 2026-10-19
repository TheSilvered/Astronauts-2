from hashlib import sha256
from bcrypt import gensalt

def encrypt(src, dst=None, src_is_file=True, src_encoding="UTF8"):
    if src_is_file:
        with open(src, "rb", encoding=src_encoding) as f:
            b = f.read()
    else:
        b = src.encode("UTF8")
    salt = gensalt(31)
    m = sha256(salt)
    hashed_salt = m.digest()
    mul = sum(hashed_salt)
    bytes_list = []

    for i in salt:
        bytes_list.append((i + 50) % 128)

    for i in range(len(b)):
        bytes_list.append((b[i] + i*mul) % 256)

    if dst is not None:
        with open(dst, "wb") as f:
            for i in bytes_list:
                f.write(i.to_bytes(1, "big"))
    else:
        return bytes(bytes_list)


def decrypt(src, dst=None):
    with open(src, "rb") as f:
        b = f.read()

    salt = bytes([(i - 50) % 128 for i in b[:29]])
    m = sha256(salt)
    mul = sum(m.digest())
    new_bytes = bytes()
    for i in range(len(b) - 29):
        new_bytes += ((b[i+29] - i*mul) % 256).to_bytes(1, "big")

    if dst is not None:
        with open(dst, "wb") as f:
            f.write(new_bytes)
    else:
        return new_bytes


def main():
    encrypt("test.txt", "test2.txt")
    # decrypt("main.yp", "main.yy")


if __name__ == "__main__":
    main()