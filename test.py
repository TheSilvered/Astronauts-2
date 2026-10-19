import hashlib
import encrypter

data = encrypter.decrypt("assets/levels/level0.level")

print(hashlib.sha256(data).hexdigest())
