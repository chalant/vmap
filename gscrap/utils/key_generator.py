import hashlib

def generate_key(ipt):
    return int(hashlib.md5(ipt.encode('utf-8')).hexdigest(), 16)