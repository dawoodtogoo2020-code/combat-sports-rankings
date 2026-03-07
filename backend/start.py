import sys
import os
import site

# Debug: print environment
print(f"Python: {sys.executable}", flush=True)
print(f"sys.path: {sys.path}", flush=True)
print(f"site-packages: {site.getusersitepackages()}", flush=True)

# Force add all possible site-packages
for p in [
    site.getusersitepackages(),
    os.path.join(sys.prefix, "lib", "site-packages"),
    r"C:\Python310\lib\site-packages",
    os.path.expanduser(r"~\AppData\Roaming\Python\Python310\site-packages"),
]:
    if isinstance(p, str) and p not in sys.path and os.path.isdir(p):
        sys.path.insert(0, p)
        print(f"Added: {p}", flush=True)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
