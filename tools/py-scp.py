#!/usr/bin/env python3
# py-scp — cross-platform, scp-like file copy over LAN (pure stdlib)
#   - Works on Windows/macOS/Linux; friendly to Git Bash paths (/c/Users/..)
#   - Agent auto-start: Windows Run key / macOS launchd / Linux systemd --user or XDG autostart
#   - Default agent root: ~/Downloads
#   - Remote spec: user@host:/abs/path
#   - UDP discovery (9920) + HTTP transfer (9921)

import argparse, os, sys, re, json, ssl, socket, http.client, http.server, socketserver
import urllib.parse, time, shutil, threading, subprocess, platform, stat
from pathlib import Path, PurePosixPath

APP = "py-scp"
VER = "0.4"
UDP_PORT = 9920
HTTP_PORT = 9921

REMOTE_RE = re.compile(r"^(?:(?P<user>[^@]+)@)?(?P<host>[^:]+):(?P<path>/.*)$")


def is_windows(): return platform.system() == "Windows"


def is_macos():   return platform.system() == "Darwin"


def is_linux():   return platform.system() == "Linux"


def is_remote(x: str) -> bool: return REMOTE_RE.match(x or "") is not None


def parse_remote(x: str):
    m = REMOTE_RE.match(x or "")
    return None if not m else {"user": m.group("user") or "", "host": m.group("host"), "path": m.group("path")}


def human(n):
    u = ["B", "KB", "MB", "GB", "TB", "PB"];
    i = 0;
    n = float(n)
    while n >= 1024 and i < len(u) - 1: n /= 1024; i += 1
    return f"{n:.1f}{u[i]}"


def local_ipv4s():
    ips = set()
    try:
        for fam, _, _, _, sa in socket.getaddrinfo(socket.gethostname(), None):
            if fam == socket.AF_INET:
                ip = sa[0]
                if not (ip.startswith("127.") or ip.startswith("169.254.")):
                    ips.add(ip)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for probe in ["8.8.8.8", "1.1.1.1", "192.168.1.1"]:
            try:
                s.connect((probe, 80));
                ip = s.getsockname()[0]
                if not (ip.startswith("127.") or ip.startswith("169.254.")): ips.add(ip)
            except Exception:
                pass
        s.close()
    except Exception:
        pass
    return sorted(ips)


# --- Git Bash/MSYS path -> Windows NT path ---
MSYS_RE = re.compile(r"^/([a-zA-Z])/(.*)$")


def msys_to_nt(p: str) -> str:
    m = MSYS_RE.match(p)
    if m: return f"{m.group(1).upper()}:\\{m.group(2).replace('/', '\\')}"
    return p


def norm_local_path(p: str) -> Path:
    # Expand ~, env; accept Git Bash /c/... on Windows
    p = os.path.expandvars(os.path.expanduser(p))
    if is_windows(): p = msys_to_nt(p)
    return Path(p).resolve()


def default_root() -> Path:
    d = Path.home() / "Downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def app_state_dir() -> Path:
    # cross-platform writable dir for config
    if is_windows():
        base = Path(os.getenv("APPDATA") or (Path.home() / "AppData/Roaming"))
    elif is_macos():
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_STATE_HOME") or (Path.home() / ".local/state"))
    d = base / APP
    d.mkdir(parents=True, exist_ok=True)
    return d


def cfg_path(): return app_state_dir() / "config.json"


def load_cfg():
    p = cfg_path()
    return json.loads(p.read_text("utf-8")) if p.exists() else {}


def save_cfg(cfg): cfg_path().write_text(json.dumps(cfg, indent=2), encoding="utf-8")


# ---------------- HTTP Agent ----------------
class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = f"{APP}/{VER}"

    def _auth(self):
        tok = getattr(self.server, "token", "")
        return True if not tok else self.headers.get("X-Token") == tok

    def _bad(self, code, msg=""):
        self.send_response(code);
        self.end_headers()
        if msg: self.wfile.write(msg.encode())

    def _map(self, prefix, allow_dir=True):
        raw = urllib.parse.unquote(self.path)
        if not raw.startswith(prefix): return None, "bad route"
        rel = raw[len(prefix):]
        parts = PurePosixPath(rel).parts
        if any(p in ("", "..") for p in parts): return None, "illegal path"
        root = Path(self.server.root).resolve()
        tgt = (root / Path(*parts)).resolve()
        try:
            tgt.relative_to(root)
        except Exception:
            return None, "escape root"
        if not allow_dir and tgt.is_dir(): return None, "expect file"
        return tgt, None

    def log_message(self, fmt, *args):
        # quiet default; comment out if you want logs
        pass

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200);
            self.end_headers();
            self.wfile.write(b"ok");
            return
        if not self._auth(): return self._bad(401, "bad token")
        if self.path.startswith("/download/"):
            tgt, err = self._map("/download/", allow_dir=False)
            if err: return self._bad(400, err)
            if not tgt.exists() or not tgt.is_file(): return self._bad(404, "not found")
            self.send_response(200);
            self.send_header("Content-Length", str(tgt.stat().st_size))
            self.end_headers()
            with open(tgt, "rb") as f:
                shutil.copyfileobj(f, self.wfile, 65536)
            return
        if self.path.startswith("/list/"):
            tgt, err = self._map("/list/", allow_dir=True)
            if err: return self._bad(400, err)
            if not tgt.exists(): return self._bad(404, "not found")
            if tgt.is_file():
                info = {"type": "file", "name": tgt.name, "size": tgt.stat().st_size}
            else:
                info = {"type": "dir", "name": tgt.name, "entries": sorted(p.name for p in tgt.iterdir())}
            data = json.dumps(info).encode()
            self.send_response(200);
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)));
            self.end_headers();
            self.wfile.write(data);
            return
        return self._bad(404, "not found")

    def do_PUT(self):
        if not self._auth(): return self._bad(401, "bad token")
        tgt, err = self._map("/upload/", allow_dir=True)
        if err: return self._bad(400, err)
        clen = self.headers.get("Content-Length")
        if clen is None: return self._bad(411, "length required")
        n = int(clen)
        tgt.parent.mkdir(parents=True, exist_ok=True)
        tmp = tgt.with_suffix(tgt.suffix + ".part")
        left = n
        with open(tmp, "wb") as f:
            while left > 0:
                chunk = self.rfile.read(min(65536, left))
                if not chunk: break
                f.write(chunk);
                left -= len(chunk)
        if left != 0:
            try:
                os.remove(tmp)
            except OSError:
                pass
            return self._bad(400, "incomplete body")
        os.replace(tmp, tgt)
        self.send_response(201);
        self.end_headers();
        self.wfile.write(b"stored")


def run_http(root, port, token):
    httpd = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    httpd.root = str(Path(root).resolve());
    httpd.token = token or ""
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


# ---------------- Discovery UDP ----------------
def agent_discovery_loop(cfg):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", int(cfg.get("udp_port", UDP_PORT))))
    while True:
        data, addr = s.recvfrom(4096)
        try:
            req = json.loads(data.decode("utf-8"))
            if req.get("op") == "ping" and req.get("who") == APP:
                resp = {"ok": True, "who": APP, "ver": VER, "port": int(cfg.get("port", HTTP_PORT)),
                        "host": socket.gethostname()}
                s.sendto(json.dumps(resp).encode("utf-8"), addr)
        except Exception:
            continue


def ping_agent(host, udp_port=UDP_PORT, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
    s.settimeout(timeout)
    try:
        s.sendto(json.dumps({"op": "ping", "who": APP}).encode(), (host, int(udp_port)))
        data, _ = s.recvfrom(4096);
        return json.loads(data.decode())
    except Exception:
        return None
    finally:
        s.close()


# ---------------- HTTP client ----------------
def http_conn(host, port): return http.client.HTTPConnection(host, int(port), timeout=60)


def put_file(host, port, token, rel_url, fpath: Path):
    conn = http.client.HTTPConnection(host, int(port), timeout=60)
    try:
        size = fpath.stat().st_size
        conn.putrequest("PUT", rel_url)
        if token:
            conn.putheader("X-Token", token)
        conn.putheader("Content-Length", str(size))
        conn.endheaders()

        with open(fpath, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                conn.send(chunk)

        resp = conn.getresponse()
        _ = resp.read()
        if resp.status not in (200, 201):
            raise RuntimeError(f"{resp.status} {resp.reason}")
    finally:
        conn.close()


def get_json(host, port, token, rel_url):
    conn = http_conn(host, port)
    try:
        conn.putrequest("GET", rel_url)
        if token: conn.putheader("X-Token", token)
        conn.endheaders()
        r = conn.getresponse();
        data = r.read()
        if r.status != 200: raise RuntimeError(f"{r.status} {r.reason}: {data[:200]!r}")
        return json.loads(data.decode())
    finally:
        conn.close()


def download_file(host, port, token, rel_url, out_path: Path):
    conn = http_conn(host, port)
    try:
        conn.putrequest("GET", rel_url)
        if token: conn.putheader("X-Token", token)
        conn.endheaders()
        r = conn.getresponse()
        if r.status != 200:
            data = r.read();
            raise RuntimeError(f"{r.status} {r.reason}: {data[:200]!r}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk: break
                f.write(chunk)
    finally:
        conn.close()


# ---------------- copy ops ----------------
def iter_files(p: Path):
    if p.is_dir():
        for root, _dirs, files in os.walk(p):
            for n in files: yield Path(root) / n
    else:
        yield p


def send_local_to_remote(args, src: Path, dst_remote, cfg):
    info = ping_agent(dst_remote["host"], cfg.get("udp_port", UDP_PORT), timeout=2.0)
    if not info or not info.get("ok"):
        sys.exit(f"无法联系远端代理 {dst_remote['host']}（对方未安装/未运行）")
    port = info["port"];
    token = cfg.get("token", "");
    rpath = dst_remote["path"]
    many = args.r or src.is_dir()
    files = list(iter_files(src))
    base = src if src.is_dir() else src.parent
    t0 = time.time();
    total = 0;
    cnt = 0
    for f in files:
        rel = f.relative_to(base).as_posix()
        if many:
            url = "/upload/" + urllib.parse.quote((rpath.rstrip("/") + "/" + rel).lstrip("/"))
        else:
            # 单文件：若远端路径以 / 结尾，用源文件名；否则按给定文件名
            final = (rpath.rstrip("/") + "/" + f.name) if rpath.endswith("/") else rpath
            url = "/upload/" + urllib.parse.quote(final.lstrip("/"))
        put_file(dst_remote["host"], port, token, url, f)
        sz = f.stat().st_size;
        total += sz;
        cnt += 1
        print(f"UP  {f} -> {dst_remote['host']}:{rpath}  ({human(sz)})")
    dt = time.time() - t0
    print(
        f"Done UP: files={cnt} total={human(total)} time={dt:.2f}s avg={human(total / dt) + '/s' if dt > 0 else 'n/a'}")


def fetch_remote_to_local(args, src_remote, dst: Path, cfg):
    info = ping_agent(src_remote["host"], cfg.get("udp_port", UDP_PORT), timeout=2.0)
    if not info or not info.get("ok"):
        sys.exit(f"无法联系远端代理 {src_remote['host']}（对方未安装/未运行）")
    port = info["port"];
    token = cfg.get("token", "");
    rpath = src_remote["path"]
    dst_is_dir = dst.is_dir() or str(dst).endswith(os.sep) or args.r
    if args.r:
        if not dst.exists(): dst.mkdir(parents=True, exist_ok=True)

        def walk(prefix):
            j = get_json(src_remote["host"], port, token, "/list/" + urllib.parse.quote(prefix.lstrip("/")))
            if j["type"] == "file":
                yield prefix
            else:
                for name in j["entries"]:
                    yield from walk(prefix.rstrip("/") + "/" + name)

        t0 = time.time();
        total = 0;
        cnt = 0
        base = PurePosixPath(rpath.rstrip("/"))
        for rel in walk(rpath):
            sub = PurePosixPath(rel).relative_to(base)
            out = (dst / sub.as_posix())
            download_file(src_remote["host"], port, token, "/download/" + urllib.parse.quote(rel.lstrip("/")), out)
            sz = out.stat().st_size;
            total += sz;
            cnt += 1
            print(f"DL  {src_remote['host']}:{rel} -> {out}  ({human(sz)})")
        dt = time.time() - t0
        print(
            f"Done DL: files={cnt} total={human(total)} time={dt:.2f}s avg={human(total / dt) + '/s' if dt > 0 else 'n/a'}")
    else:
        out = dst / PurePosixPath(rpath).name if dst_is_dir else dst
        download_file(src_remote["host"], port, token, "/download/" + urllib.parse.quote(rpath.lstrip("/")), out)
        print(f"DL  {src_remote['host']}:{rpath} -> {out}  ({human(out.stat().st_size)})")


# ---------------- installers ----------------
def install_agent(root: Path, token: str, udp_port: int, http_port: int):
    cfg = load_cfg()
    cfg.update({"root": str(root), "token": token or "", "udp_port": int(udp_port), "port": int(http_port)})
    save_cfg(cfg)
    script = Path(__file__).resolve()
    cmd = f'"{sys.executable}" "{script}" --agent --quiet'
    # platform-specific autostart
    if is_windows():
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as k:
                # use pythonw if available
                exe = Path(sys.executable)
                if exe.name.lower() == "python.exe": exe = exe.with_name("pythonw.exe")
                run_cmd = f'"{exe}" "{script}" --agent --quiet'
                winreg.SetValueEx(k, f"{APP}-agent", 0, winreg.REG_SZ, run_cmd)
        except Exception as e:
            print(f"[warn] 注册自启失败：{e}")
        # start now
        subprocess.Popen(run_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[ok] 已安装并启动后台代理（Windows）。root={root}")
        return

    if is_macos():
        la_dir = Path.home() / "Library" / "LaunchAgents"
        la_dir.mkdir(parents=True, exist_ok=True)
        plist = la_dir / f"{APP}.agent.plist"
        content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>{APP}.agent</string>
<key>ProgramArguments</key>
<array><string>{sys.executable}</string><string>{script}</string><string>--agent</string><string>--quiet</string></array>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>{app_state_dir() / 'agent.out'}</string>
<key>StandardErrorPath</key><string>{app_state_dir() / 'agent.err'}</string>
</dict></plist>
"""
        plist.write_text(content, encoding="utf-8")
        subprocess.run(["launchctl", "load", "-w", str(plist)], check=False)
        print(f"[ok] 已安装并加载后台代理（macOS）。root={root}")
        return

    if is_linux():
        # prefer systemd --user
        try:
            unit_dir = Path.home() / ".config" / "systemd" / "user"
            unit_dir.mkdir(parents=True, exist_ok=True)
            unit = unit_dir / f"{APP}.service"
            unit.write_text(f"""[Unit]
Description={APP} agent

[Service]
ExecStart={sys.executable} {script} --agent --quiet
Restart=always

[Install]
WantedBy=default.target
""", encoding="utf-8")
            subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
            subprocess.run(["systemctl", "--user", "enable", "--now", f"{APP}.service"], check=False)
            print(f"[ok] 已安装并启动后台代理（Linux systemd --user）。root={root}")
            return
        except Exception as e:
            print(f"[warn] systemd 配置失败：{e}; 尝试 XDG autostart")
        # XDG autostart fallback
        ad = Path.home() / ".config" / "autostart"
        ad.mkdir(parents=True, exist_ok=True)
        desk = ad / f"{APP}.desktop"
        desk.write_text(f"""[Desktop Entry]
Type=Application
Name={APP} agent
Exec={sys.executable} {script} --agent --quiet
X-GNOME-Autostart-enabled=true
""", encoding="utf-8")
        print(f"[ok] 已安装后台代理（XDG autostart）。root={root}")
        # start now
        subprocess.Popen([sys.executable, str(script), "--agent", "--quiet"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        return


def uninstall_agent():
    # try disable all variants, ignore errors
    if is_windows():
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as k:
                try:
                    winreg.DeleteValue(k, f"{APP}-agent")
                except FileNotFoundError:
                    pass
        except Exception:
            pass
        print("[ok] 已卸载自启（Windows）。若需立刻退出，请在任务管理器结束 pythonw/python。")
        return

    if is_macos():
        plist = Path.home() / "Library" / "LaunchAgents" / f"{APP}.agent.plist"
        subprocess.run(["launchctl", "unload", "-w", str(plist)], check=False)
        try:
            plist.unlink()
        except FileNotFoundError:
            pass
        print("[ok] 已卸载自启（macOS）。")
        return

    if is_linux():
        unit = Path.home() / ".config" / "systemd" / "user" / f"{APP}.service"
        subprocess.run(["systemctl", "--user", "disable", "--now", f"{APP}.service"], check=False)
        try:
            unit.unlink()
        except FileNotFoundError:
            pass
        desk = Path.home() / ".config" / "autostart" / f"{APP}.desktop"
        try:
            desk.unlink()
        except FileNotFoundError:
            pass
        print("[ok] 已卸载自启（Linux）。")
        return


# ---------------- CLI ----------------
def build_parser():
    ips = ", ".join(local_ipv4s()) or "（未探测到）"
    examples = f"""
示例：
  # 1) 两台机器各自安装一次后台代理（根目录默认 ~/Downloads；也可自定）
  py-scp --install-agent
  py-scp --install-agent --root ~/Downloads/peer --token 123456

  # 2) 之后即可互传（像 scp 一样）
  py-scp file.txt user@192.168.1.23:/inbox/
  py-scp -r ./project  user@192.168.1.23:/backup/project/
  py-scp user@192.168.1.23:/inbox/a.txt  ./recv/
  py-scp -r user@192.168.1.23:/inbox/  ./recv/

  # 3) 卸载代理
  py-scp --uninstall-agent

本机 IPv4： {ips}
"""
    p = argparse.ArgumentParser(
        prog="py-scp",
        description=f"py-scp v{VER} — 局域网 scp 风格互传（跨平台、纯 Python）。\n"
                    "远端路径写法：user@host:/abs/path\n"
                    "代理默认根目录为 ~/Downloads，可用 --root 更改。",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=examples)
    p.add_argument("SRC", nargs="?", help="源（本地路径 或 user@host:/abs）")
    p.add_argument("DST", nargs="?", help="目的（本地路径 或 user@host:/abs）")
    p.add_argument("-r", action="store_true", help="递归目录")

    # agent lifecycle
    p.add_argument("--install-agent", action="store_true", help="安装并启动后台代理（登录自启）")
    p.add_argument("--uninstall-agent", action="store_true", help="卸载后台代理")
    p.add_argument("--agent", action="store_true", help="（内部）运行后台代理")
    p.add_argument("--root", help="安装/运行代理的根目录（默认 ~/Downloads）")
    p.add_argument("--token", help="安装/运行代理的 Token（可选）")
    p.add_argument("--udp-port", type=int, default=UDP_PORT, help=f"发现端口（默认 {UDP_PORT}）")
    p.add_argument("--port", type=int, default=HTTP_PORT, help=f"传输端口（默认 {HTTP_PORT}）")
    p.add_argument("--quiet", action="store_true", help="代理静默运行")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    # install/uninstall
    if args.install_agent:
        root = norm_local_path(args.root) if args.root else default_root()
        install_agent(root, args.token or "", args.udp_port, args.port)
        print(f"agent root={root}  port={args.port}  token={'<none>' if not args.token else args.token}")
        return
    if args.uninstall_agent:
        uninstall_agent();
        return
    if args.agent:
        cfg = load_cfg()
        if args.root: cfg["root"] = str(norm_local_path(args.root))
        if args.token is not None: cfg["token"] = args.token or ""
        if args.udp_port: cfg["udp_port"] = int(args.udp_port)
        if args.port: cfg["port"] = int(args.port)
        save_cfg(cfg)
        # start discovery + http
        threading.Thread(target=agent_discovery_loop, args=(cfg,), daemon=True).start()
        run_http(Path(cfg.get("root") or default_root()), int(cfg.get("port", HTTP_PORT)), cfg.get("token", ""))
        return

    # copy mode
    if not (args.SRC and args.DST):
        parser.print_help();
        sys.exit(2)

    src_is_remote = is_remote(args.SRC)
    dst_is_remote = is_remote(args.DST)

    if src_is_remote and dst_is_remote:
        sys.exit("暂不支持 远端->远端 直传（先拉到本地再推过去）。")

    if not src_is_remote and dst_is_remote:
        src = norm_local_path(args.SRC)
        send_local_to_remote(args, src, parse_remote(args.DST), load_cfg());
        return

    if src_is_remote and not dst_is_remote:
        dst = norm_local_path(args.DST)
        fetch_remote_to_local(args, parse_remote(args.SRC), dst, load_cfg());
        return

    # local->local 也顺手支持
    s = norm_local_path(args.SRC);
    d = norm_local_path(args.DST)
    if s.is_dir():
        if not args.r: sys.exit("目录拷贝请加 -r")
        shutil.copytree(s, d, dirs_exist_ok=True)
    else:
        d.parent.mkdir(parents=True, exist_ok=True)
        if d.is_dir(): d = d / s.name
        shutil.copy2(s, d)
    print(f"LOCAL COPY: {s} -> {d}")


if __name__ == "__main__":
    main()
