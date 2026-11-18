"""Small helpers to drive headless Edge over the DevTools protocol."""
import json, random, subprocess, tempfile, time, urllib.request, base64
import websocket
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

class Browser:
    def __init__(self, width=1400, height=1000, dark=False):
        self.port = random.randint(9300, 9399)
        work = tempfile.mkdtemp(prefix="cdp-")
        self.process = subprocess.Popen([EDGE, "--headless=new", "--disable-gpu", f"--remote-debugging-port={self.port}",
            f"--user-data-dir={work}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                pages = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json", timeout=1).read()); break
            except OSError: time.sleep(0.3)
        page = next(t for t in pages if t["type"] == "page")
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"]); self.n = 0
        self.cdp("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=1, mobile=False)
        self.cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])
    def cdp(self, method, **params):
        self.n += 1; self.ws.send(json.dumps({"id": self.n, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.n:
                if "error" in m: raise RuntimeError(m["error"])
                return m.get("result", {})
    def js(self, expression):
        r = self.cdp("Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r: raise RuntimeError(r["exceptionDetails"])
        return r["result"].get("value")
    def wait(self, expression, tries=60):
        for _ in range(tries):
            if self.js(expression): return True
            time.sleep(0.2)
        return False
    def shot(self, path):
        open(path, "wb").write(base64.b64decode(self.cdp("Page.captureScreenshot", format="png")["data"]))
    def mouse(self, kind, x, y, clicks=1):
        self.cdp("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left", clickCount=clicks, buttons=0 if kind == "mouseReleased" else 1)
    def close(self):
        self.ws.close(); self.process.kill()
