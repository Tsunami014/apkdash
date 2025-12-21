from pyapktool import pyapktool as pat

def extract(file):
    pat.print_ok(f"Unpacking {file}...")
    pat.unpack_apk(file)

def pack(folder):
    pat.print_ok(f"Packing and signing {folder}...")
    pat.pack_and_sign_apk(folder)

