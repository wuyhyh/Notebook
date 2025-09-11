#!/usr/bin/env python3
# pyscp_web.py — Browser UI for LAN file transfers (pure Python stdlib)
# - Cross-platform (Windows/macOS/Linux). Git Bash paths like /c/Users/... supported.
# - Agent: UDP discovery (9920) + HTTP transfer (9921), root default ~/Downloads, token auth.
# - Web UI: http://127.0.0.1:9922/  (local FS left panel, remote FS right panel)
# - No external deps.

import os, sys, re, json, time, ssl, socket, urllib.parse, threading, shutil
import http.server, socketserver, http.client, cgi, platform, subprocess
from pathlib import Path, PurePosixPath

APP = "pyscp"
VER = "0.5"
UDP_PORT = 9920
HTTP_PORT = 9921
WEB_PORT  = 9922

# ---------------------- cross-platform helpers ----------------------

def is_windows(): return platform.system() == "Windows"
def is_macos():   return platform.system() == "Darwin"
def is_linux():   return platform.system() == "Linux"

MSYS_RE = re.compile(r"^/([a-zA-Z])/(.*)$")
def msys_to_nt(p: str) -> str:
    m = MSYS_RE.match(p)
    if m: return f"{m.group(1).upper()}:\\{m.group(2).replace('/', '\\')}"
    return p

def norm_local_path(p: str) -> Path:
    p = os.path.expandvars(os.path.expanduser(p or ""))
    if is_windows(): p = msys_to_nt(p)
    return Path(p).resolve()

def default_root() -> Path:
    d = Path.home() / "Downloads"
    d.mkdir(parents=True, exist_ok=True)
    return d

def app_state_dir() -> Path:
    if is_windows():
        base = Path(os.getenv("APPDATA") or (Path.home()/"AppData/Roaming"))
    elif is_macos():
        base = Path.home()/ "Library"/ "Application Support"
    else:
        base = Path(os.getenv("XDG_STATE_HOME") or (Path.home()/".local/state"))
    d = base / APP
    d.mkdir(parents=True, exist_ok=True)
    return d

def cfg_file(): return app_state_dir()/ "config.json"
def agents_file(): return app_state_dir()/ "agents.json"

def load_cfg():
    p = cfg_file()
    return json.loads(p.read_text("utf-8")) if p.exists() else {}
def save_cfg(cfg): cfg_file().write_text(json.dumps(cfg, indent=2), encoding="utf-8")

def load_agents():
    p = agents_file()
    return json.loads(p.read_text("utf-8")) if p.exists() else {"seq":0,"items":[]}
def save_agents(data): agents_file().write_text(json.dumps(data, indent=2), encoding="utf-8")

def local_ipv4s():
    ips=set()
    try:
        for fam,_,_,_,sa in socket.getaddrinfo(socket.gethostname(), None):
            if fam == socket.AF_INET:
                ip = sa[0]
                if not (ip.startswith("127.") or ip.startswith("169.254.")): ips.add(ip)
    except Exception: pass
    try:
        s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for probe in ["8.8.8.8","1.1.1.1","192.168.1.1"]:
            try:
                s.connect((probe,80)); ip=s.getsockname()[0]
                if not (ip.startswith("127.") or ip.startswith("169.254.")): ips.add(ip)
            except Exception: pass
        s.close()
    except Exception: pass
    return sorted(ips)

# ---------------------- Agent (HTTP + UDP) ----------------------

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

class AgentHandler(http.server.BaseHTTPRequestHandler):
    server_version = f"{APP}-agent/{VER}"

    def _auth(self):
        tok = getattr(self.server, "token", "")
        return True if not tok else self.headers.get("X-Token") == tok

    def _bad(self, code, msg=""):
        self.send_response(code); self.end_headers()
        if msg: self.wfile.write(msg.encode())

    def _map(self, prefix, allow_dir=True):
        raw = urllib.parse.unquote(self.path)
        if not raw.startswith(prefix): return None, "bad route"
        rel = raw[len(prefix):]
        parts = PurePosixPath(rel).parts
        if any(p in ("", "..") for p in parts): return None, "illegal path"
        root = Path(self.server.root).resolve()
        tgt = (root / Path(*parts)).resolve()
        try: tgt.relative_to(root)
        except Exception: return None, "escape root"
        if not allow_dir and tgt.is_dir(): return None, "expect file"
        return tgt, None

    def log_message(self, fmt, *args):
        # keep quiet
        pass

    def do_GET(self):
        if self.path == "/ping":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        if not self._auth(): return self._bad(401, "bad token")

        if self.path.startswith("/download/"):
            tgt, err = self._map("/download/", allow_dir=False)
            if err: return self._bad(400, err)
            if not tgt.exists() or not tgt.is_file(): return self._bad(404, "not found")
            self.send_response(200); self.send_header("Content-Length", str(tgt.stat().st_size))
            self.end_headers()
            with open(tgt, "rb") as f:
                shutil.copyfileobj(f, self.wfile, 65536)
            return

        if self.path.startswith("/list/"):
            tgt, err = self._map("/list/", allow_dir=True)
            if err: return self._bad(400, err)
            if not tgt.exists(): return self._bad(404, "not found")
            if tgt.is_file():
                info = {"type":"file","name":tgt.name,"size":tgt.stat().st_size}
            else:
                entries=[]
                for p in tgt.iterdir():
                    try:
                        t="dir" if p.is_dir() else "file"
                        s=(p.stat().st_size if p.is_file() else 0)
                        entries.append({"name":p.name,"type":t,"size":s})
                    except Exception:
                        continue
                info={"type":"dir","name":tgt.name,"entries":sorted(entries,key=lambda x:(x['type']!="dir",x['name'].lower()))}
            b=json.dumps(info).encode()
            self.send_response(200); self.send_header("Content-Type","application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return

        self._bad(404,"not found")

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
                f.write(chunk); left -= len(chunk)
        if left != 0:
            try: os.remove(tmp)
            except OSError: pass
            return self._bad(400, "incomplete body")
        os.replace(tmp, tgt)
        self.send_response(201); self.end_headers(); self.wfile.write(b"stored")

def run_agent_http(root, port, token):
    httpd = ThreadingHTTPServer(("0.0.0.0", int(port)), AgentHandler)
    httpd.root = str(Path(root).resolve())
    httpd.token = token or ""
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass

def agent_discovery_loop(cfg):
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("0.0.0.0", int(cfg.get("udp_port", UDP_PORT))))
    while True:
        data, addr = s.recvfrom(4096)
        try:
            req=json.loads(data.decode())
            if req.get("op")=="ping" and req.get("who")==APP:
                resp={"ok":True,"who":APP,"ver":VER,"port":int(cfg.get("port", HTTP_PORT)),"host":socket.gethostname()}
                s.sendto(json.dumps(resp).encode(), addr)
        except Exception:
            continue

def ping_agent(host, udp_port=UDP_PORT, timeout=1.0):
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.settimeout(timeout)
    try:
        s.sendto(json.dumps({"op":"ping","who":APP}).encode(), (host,int(udp_port)))
        data,_=s.recvfrom(4096); return json.loads(data.decode())
    except Exception:
        return None
    finally:
        s.close()

# ---------------------- Agent lifecycle installers ----------------------

def install_agent(root: Path, token: str, udp_port: int, http_port: int):
    cfg = load_cfg()
    cfg.update({"root": str(root), "token": token or "", "udp_port": int(udp_port), "port": int(http_port)})
    save_cfg(cfg)
    script = Path(__file__).resolve()
    # start cmd
    exe = Path(sys.executable)
    if is_windows() and exe.name.lower()=="python.exe":
        exe = exe.with_name("pythonw.exe")
    run_cmd = f'"{exe}" "{script}" --agent --quiet'
    # auto-start
    if is_windows():
        try:
            import winreg
            key=r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key,0,winreg.KEY_ALL_ACCESS) as k:
                winreg.SetValueEx(k,f"{APP}-agent",0,winreg.REG_SZ,run_cmd)
        except Exception as e:
            print(f"[warn] Windows 注册自启失败：{e}")
        subprocess.Popen(run_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[ok] agent installed (Windows) root={root}")
        return
    if is_macos():
        la_dir=Path.home()/ "Library"/ "LaunchAgents"; la_dir.mkdir(parents=True, exist_ok=True)
        plist=la_dir/ f"{APP}.agent.plist"
        plist.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>{APP}.agent</string>
<key>ProgramArguments</key><array>
<string>{sys.executable}</string><string>{script}</string><string>--agent</string><string>--quiet</string>
</array>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>{app_state_dir()/ 'agent.out'}</string>
<key>StandardErrorPath</key><string>{app_state_dir()/ 'agent.err'}</string>
</dict></plist>""","utf-8")
        subprocess.run(["launchctl","load","-w",str(plist)], check=False)
        print(f"[ok] agent installed (macOS) root={root}")
        return
    # Linux
    try:
        unit_dir=Path.home()/ ".config"/ "systemd"/ "user"; unit_dir.mkdir(parents=True, exist_ok=True)
        unit=unit_dir/ f"{APP}.service"
        unit.write_text(f"""[Unit]
Description={APP} agent
[Service]
ExecStart={sys.executable} {script} --agent --quiet
Restart=always
[Install]
WantedBy=default.target
""","utf-8")
        subprocess.run(["systemctl","--user","daemon-reload"], check=False)
        subprocess.run(["systemctl","--user","enable","--now",f"{APP}.service"], check=False)
        print(f"[ok] agent installed (Linux systemd --user) root={root}")
        return
    except Exception as e:
        print(f"[warn] systemd failed: {e}; fallback XDG autostart")
    ad=Path.home()/ ".config"/ "autostart"; ad.mkdir(parents=True, exist_ok=True)
    desk=ad/ f"{APP}.desktop"
    desk.write_text(f"""[Desktop Entry]
Type=Application
Name={APP} agent
Exec={sys.executable} {script} --agent --quiet
X-GNOME-Autostart-enabled=true
""","utf-8")
    subprocess.Popen([sys.executable, str(script), "--agent","--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[ok] agent installed (XDG autostart) root={root}")

def uninstall_agent():
    if is_windows():
        try:
            import winreg
            key=r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key,0,winreg.KEY_ALL_ACCESS) as k:
                try: winreg.DeleteValue(k,f"{APP}-agent")
                except FileNotFoundError: pass
        except Exception: pass
        print("[ok] 自启已卸载（Windows）。如需立即退出，请结束 pythonw/python 进程。")
        return
    if is_macos():
        plist=Path.home()/ "Library"/ "LaunchAgents"/ f"{APP}.agent.plist"
        subprocess.run(["launchctl","unload","-w",str(plist)], check=False)
        try: plist.unlink()
        except FileNotFoundError: pass
        print("[ok] 自启已卸载（macOS）。"); return
    # Linux
    unit=Path.home()/ ".config"/ "systemd"/ "user"/ f"{APP}.service"
    subprocess.run(["systemctl","--user","disable","--now",f"{APP}.service"], check=False)
    try: unit.unlink()
    except FileNotFoundError: pass
    desk=Path.home()/ ".config"/ "autostart"/ f"{APP}.desktop"
    try: desk.unlink()
    except FileNotFoundError: pass
    print("[ok] 自启已卸载（Linux）。")

# ---------------------- HTTP client helpers to agent ----------------------

def http_conn(host, port): return http.client.HTTPConnection(host, int(port), timeout=60)

def agent_put_file(host, port, token, rel_url, fobj, size):
    conn=http_conn(host, port)
    try:
        conn.putrequest("PUT", rel_url)
        if token: conn.putheader("X-Token", token)
        conn.putheader("Content-Length", str(size))
        conn.endheaders()
        sent=0
        while True:
            chunk=fobj.read(65536)
            if not chunk: break
            conn.send(chunk); sent += len(chunk)
        resp=conn.getresponse(); _=resp.read()
        if resp.status not in (200,201): raise RuntimeError(f"{resp.status} {resp.reason}")
    finally:
        conn.close()

def agent_get_json(host, port, token, rel_url):
    conn=http_conn(host, port)
    try:
        conn.putrequest("GET", rel_url)
        if token: conn.putheader("X-Token", token)
        conn.endheaders()
        r=conn.getresponse(); data=r.read()
        if r.status!=200: raise RuntimeError(f"{r.status} {r.reason}: {data[:200]!r}")
        return json.loads(data.decode())
    finally:
        conn.close()

def agent_download_to_file(host, port, token, rel_url, out_path: Path):
    conn=http_conn(host, port)
    try:
        conn.putrequest("GET", rel_url)
        if token: conn.putheader("X-Token", token)
        conn.endheaders()
        r=conn.getresponse()
        if r.status!=200:
            data=r.read(); raise RuntimeError(f"{r.status} {r.reason}: {data[:200]!r}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path,"wb") as f:
            while True:
                chunk=r.read(65536)
                if not chunk: break
                f.write(chunk)
    finally:
        conn.close()

# ---------------------- Web UI server ----------------------

INDEX_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title>py-scp Web</title>
<style>
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:#0b1220;color:#e6edf3}
header{padding:12px 16px;background:#111827;border-bottom:1px solid #243040;display:flex;align-items:center;gap:12px}
h1{font-size:18px;margin:0}
small{opacity:.7}
main{display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:12px}
.panel{background:#0f172a;border:1px solid #243040;border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
.panel header{background:#111827;border-bottom:1px solid #243040}
.panel h2{font-size:14px;margin:0}
.toolbar{padding:8px 12px;display:flex;gap:8px;align-items:center;border-bottom:1px dashed #243040}
input,button,select{background:#0b1220;color:#e6edf3;border:1px solid #243040;border-radius:8px;padding:6px 8px}
button{cursor:pointer}
button.primary{background:#1f6feb;border-color:#1f6feb}
.list{flex:1;overflow:auto}
table{width:100%;border-collapse:collapse}
th,td{padding:6px 8px;border-bottom:1px solid #1e293b}
tr:hover{background:#0b1b2e}
.badge{background:#1f6feb22;border:1px solid #1f6feb55;padding:2px 6px;border-radius:999px;font-size:12px}
footer{padding:8px 12px;border-top:1px dashed #243040;display:flex;justify-content:space-between;align-items:center}
.row{display:flex;gap:8px;align-items:center}
hr{border:none;border-top:1px solid #243040;margin:8px 0}
kbd{background:#111827;border:1px solid #243040;border-radius:4px;padding:0 6px}
label{font-size:12px;opacity:.8}
a{color:#8ab4ff;text-decoration:none}
</style>
</head>
<body>
<header>
  <h1>py-scp <small>浏览器版</small></h1>
  <span class="badge" id="ips">IP…</span>
  <button onclick="openAdd()" class="primary">添加远端</button>
  <span style="flex:1"></span>
  <a href="#" onclick="location.reload()">刷新</a>
</header>
<main>
  <section class="panel" id="local">
    <header><h2>本机</h2></header>
    <div class="toolbar">
      <label>当前目录：</label>
      <input id="localPath" style="flex:1" value="~/Downloads"/>
      <button onclick="gotoLocal()">打开</button>
      <button onclick="mkdirLocal()">新建文件夹</button>
    </div>
    <div class="list">
      <table id="localTable"><thead><tr><th>名称</th><th>类型</th><th>大小</th></tr></thead><tbody></tbody></table>
    </div>
    <footer>
      <div class="row">
        <label>选择文件上传到右侧目录：</label>
        <input type="file" id="uploadFiles" multiple/>
        <button class="primary" onclick="uploadSelected()">上传</button>
      </div>
    </footer>
  </section>

  <section class="panel" id="remote">
    <header><h2>远端</h2></header>
    <div class="toolbar">
      <select id="agentSel"></select>
      <label>目录：</label>
      <input id="remotePath" style="flex:1" value="/"/>
      <button onclick="gotoRemote()">打开</button>
    </div>
    <div class="list">
      <table id="remoteTable"><thead><tr><th></th><th>名称</th><th>类型</th><th>大小</th></tr></thead><tbody></tbody></table>
    </div>
    <footer>
      <div class="row">
        <button onclick="downloadSelected()">下载选中到左侧目录</button>
      </div>
    </footer>
  </section>
</main>

<!-- 添加远端弹窗 -->
<div id="dlg" style="display:none; position:fixed; inset:0; background:#0008; align-items:center; justify-content:center;">
  <div class="panel" style="width:520px">
    <header><h2>添加远端</h2></header>
    <div style="padding:12px; display:flex; flex-direction:column; gap:8px">
      <div class="row"><label style="width:120px">昵称（可选）</label><input id="fNick" style="flex:1"></div>
      <div class="row"><label style="width:120px">IP/主机名</label><input id="fHost" style="flex:1" placeholder="192.168.1.23"></div>
      <div class="row"><label style="width:120px">端口</label><input id="fPort" style="width:120px" value="9921"></div>
      <div class="row"><label style="width:120px">密码/Token</label><input id="fToken" style="flex:1" placeholder="可留空"></div>
      <small>说明：远端需要已安装 <kbd>代理</kbd>（由 <kbd>pyscp_web.py --install-agent</kbd> 安装），根目录默认为 <kbd>~/Downloads</kbd>。</small>
    </div>
    <footer>
      <div class="row">
        <button onclick="closeAdd()">取消</button>
        <button class="primary" onclick="saveAgent()">保存</button>
      </div>
    </footer>
  </div>
</div>

<script>
const qs = s=>document.querySelector(s);
const qsa = s=>document.querySelectorAll(s);
const fmtSize = n => {
  n = Number(n||0);
  const u = ["B","KB","MB","GB","TB"]; let i=0;
  while (n>=1024 && i<u.length-1){ n/=1024; i++; }
  return n.toFixed(1)+u[i];
};
const toast = msg => alert(msg);

function openAdd(){ qs('#dlg').style.display='flex'; }
function closeAdd(){ qs('#dlg').style.display='none'; }

async function api(path, opts={}){
  const r = await fetch(path, Object.assign({headers:{'Content-Type':'application/json'}}, opts));
  if(!r.ok){ throw new Error(await r.text()); }
  const ct = r.headers.get('Content-Type')||'';
  if(ct.includes('application/json')) return r.json();
  return r.text();
}

async function loadAgents(){
  const agents = await api('/api/agents');
  const sel = qs('#agentSel');
  sel.innerHTML = '';
  agents.items.forEach(a=>{
    const o = document.createElement('option');
    o.value = a.id;
    o.textContent = (a.nick||a.host)+' @ '+a.host+':'+a.port;
    sel.appendChild(o);
  });
}

async function saveAgent(){
  const body = {
    nick: qs('#fNick').value.trim(),
    host: qs('#fHost').value.trim(),
    port: parseInt(qs('#fPort').value.trim()||'9921'),
   token: qs('#fToken').value
  };
  if(!body.host){ toast('请填写主机'); return; }
  await api('/api/agents', {method:'POST', body: JSON.stringify(body)});
  closeAdd();
  await loadAgents();
}

async function gotoLocal(){
  const p = qs('#localPath').value.trim();
  const j = await api('/api/local/list?path='+encodeURIComponent(p));
  qs('#localPath').value = j.path;
  const tb = qs('#localTable tbody'); tb.innerHTML='';
  if(j.path !== '/') {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>..</td><td>dir</td><td></td>`;
    tr.onclick=()=>{ qs('#localPath').value = j.parent; gotoLocal(); };
    tb.appendChild(tr);
  }
  j.entries.forEach(e=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${e.name}</td><td>${e.type}</td><td>${e.type==='file'?fmtSize(e.size):''}</td>`;
    tr.onclick=()=>{
      if(e.type==='dir'){ qs('#localPath').value = j.path.replace(/\/$/,'') + '/' + e.name; gotoLocal(); }
    };
    tb.appendChild(tr);
  });
}

async function mkdirLocal(){
  const name = prompt('新建文件夹名：');
  if(!name) return;
  await api('/api/local/mkdir', {method:'POST', body: JSON.stringify({path:qs('#localPath').value, name})});
  gotoLocal();
}

async function gotoRemote(){
  const id = qs('#agentSel').value; if(!id){ toast('先添加/选择远端'); return; }
  const p  = qs('#remotePath').value.trim() || '/';
  const j = await api(`/api/remote/list?id=${id}&path=${encodeURIComponent(p)}`);
  qs('#remotePath').value = j.path;
  const tb = qs('#remoteTable tbody'); tb.innerHTML='';
  if(j.path !== '/') {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td></td><td>..</td><td>dir</td><td></td>`;
    tr.onclick=()=>{ qs('#remotePath').value = j.parent; gotoRemote(); };
    tb.appendChild(tr);
  }
  j.entries.forEach(e=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `<td><input type="checkbox" data-name="${e.name}" data-type="${e.type}"></td>
                    <td>${e.name}</td><td>${e.type}</td><td>${e.type==='file'?fmtSize(e.size):''}</td>`;
    tr.ondblclick=()=>{
      if(e.type==='dir'){
        qs('#remotePath').value = j.path.replace(/\/$/,'') + '/' + e.name; gotoRemote();
      }
    };
    tb.appendChild(tr);
  });
}

async function uploadSelected(){
  const id = qs('#agentSel').value; if(!id){ toast('先选择远端'); return; }
  const dest = qs('#remotePath').value.trim() || '/';
  const inp = qs('#uploadFiles');
  if(!inp.files.length){ toast('先选择要上传的本地文件'); return; }
  const fd = new FormData();
  fd.append('id', id); fd.append('dest', dest);
  for(const f of inp.files) fd.append('files', f, f.name);
  const r = await fetch('/api/remote/upload', {method:'POST', body: fd});
  if(!r.ok){ toast(await r.text()); return; }
  toast('上传完成'); gotoRemote();
}

async function downloadSelected(){
  const id = qs('#agentSel').value; if(!id){ toast('先选择远端'); return; }
  const items = Array.from(qsa('#remoteTable tbody input[type=checkbox]:checked')).map(x=>({name:x.dataset.name, type:x.dataset.type}));
  if(!items.length){ toast('勾选要下载的文件/目录'); return; }
  const local = qs('#localPath').value.trim();
  const body = {id, base: qs('#remotePath').value.trim()||'/', items, local};
  const r = await fetch('/api/remote/download', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  if(!r.ok){ toast(await r.text()); return; }
  const j = await r.json();
  toast('已下载：'+j.count+' 个；总量 '+j.total_h);
  gotoLocal();
}

async function boot(){
  qs('#ips').textContent = '本机 IPv4: ' + (await api('/api/ips')).join(', ');
  await loadAgents();
  await gotoLocal();
}
boot();
</script>
</body></html>
"""

class WebHandler(http.server.BaseHTTPRequestHandler):
    server_version = f"{APP}-web/{VER}"

    def log_message(self, fmt, *args): pass

    def send_json(self, obj, code=200):
        b=json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/":
            b=INDEX_HTML.encode("utf-8")
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return

        if parsed.path == "/api/ips":
            return self.send_json(local_ipv4s())

        if parsed.path == "/api/agents":
            return self.send_json(load_agents())

        if parsed.path == "/api/local/list":
            q=urllib.parse.parse_qs(parsed.query)
            req_path = q.get("path",["~/Downloads"])[0]
            p = norm_local_path(req_path)
            if not p.exists(): return self.send_json({"path":str(p), "exists":False, "entries":[]})
            base = Path("/")
            parent = str(p.parent) if p.parent != p else str(p)
            entries=[]
            if p.is_dir():
                for child in p.iterdir():
                    try:
                        t="dir" if child.is_dir() else "file"
                        s=(child.stat().st_size if child.is_file() else 0)
                        entries.append({"name":child.name,"type":t,"size":s})
                    except Exception: continue
                entries=sorted(entries,key=lambda x:(x['type']!="dir", x['name'].lower()))
            else:
                entries=[{"name":p.name,"type":"file","size":p.stat().st_size}]
            return self.send_json({"path":str(p), "parent":str(parent), "entries":entries})

        if parsed.path == "/api/remote/list":
            q=urllib.parse.parse_qs(parsed.query)
            aid=q.get("id",[None])[0]; path=q.get("path",["/"])[0] or "/"
            if not aid: return self.send_json({"error":"missing id"}, 400)
            agd=load_agents()
            item=next((x for x in agd["items"] if str(x["id"])==str(aid)), None)
            if not item: return self.send_json({"error":"unknown id"},400)
            j = agent_get_json(item["host"], item["port"], item.get("token",""), "/list/" + urllib.parse.quote(path.lstrip("/")))
            # ensure entry types include type for children (agent已返回)
            parent = str(PurePosixPath(path).parent) if path!="/" else "/"
            if j.get("type")=="file":
                ent=[{"name":PurePosixPath(path).name,"type":"file","size":j.get("size",0)}]
                return self.send_json({"path":path,"parent":parent,"entries":ent})
            return self.send_json({"path":path,"parent":parent,"entries":j.get("entries",[])})

        self.send_response(404); self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/agents":
            length=int(self.headers.get("Content-Length","0")); data=self.rfile.read(length)
            body=json.loads(data.decode() or "{}")
            host=body.get("host"); port=int(body.get("port",HTTP_PORT)); token=body.get("token",""); nick=body.get("nick","")
            if not host: return self.send_json({"error":"host required"},400)
            # test reachability (optional)
            _=ping_agent(host, UDP_PORT, 1.0)
            ag=load_agents(); ag["seq"] += 1
            ag["items"].append({"id":ag["seq"],"host":host,"port":port,"token":token,"nick":nick})
            save_agents(ag)
            return self.send_json({"ok":True,"id":ag["seq"]})

        if parsed.path == "/api/local/mkdir":
            length=int(self.headers.get("Content-Length","0")); data=self.rfile.read(length)
            body=json.loads(data.decode() or "{}")
            base=norm_local_path(body.get("path") or str(default_root()))
            name=body.get("name","")
            if not name: return self.send_json({"error":"name required"},400)
            (base / name).mkdir(parents=True, exist_ok=True)
            return self.send_json({"ok":True})

        if parsed.path == "/api/remote/upload":
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype != 'multipart/form-data':
                return self.send_json({"error":"multipart/form-data required"},400)
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'})
            aid = form.getfirst("id")
            dest= form.getfirst("dest","/") or "/"
            agd=load_agents()
            item=next((x for x in agd["items"] if str(x["id"])==str(aid)), None)
            if not item: return self.send_json({"error":"unknown id"},400)
            files = form['files']
            if not isinstance(files, list): files=[files]
            count=0; total=0
            for f in files:
                if not f.filename: continue
                size=len(f.file.read())  # peek to get size
                f.file.seek(0)
                final = (dest.rstrip("/") + "/" + f.filename)
                url = "/upload/" + urllib.parse.quote(final.lstrip("/"))
                agent_put_file(item["host"], item["port"], item.get("token",""), url, f.file, size)
                count += 1; total += size
            return self.send_json({"ok":True,"count":count,"total":total})

        if parsed.path == "/api/remote/download":
            length=int(self.headers.get("Content-Length","0")); data=self.rfile.read(length)
            body=json.loads(data.decode() or "{}")
            aid=str(body.get("id")); base=body.get("base","/") or "/"; items=body.get("items",[]); local = norm_local_path(body.get("local") or str(default_root()))
            agd=load_agents(); item=next((x for x in agd["items"] if str(x["id"])==aid), None)
            if not item: return self.send_json({"error":"unknown id"},400)
            port=item["port"]; token=item.get("token","")
            total=0; count=0
            def walk(path):
                j=agent_get_json(item["host"], port, token, "/list/" + urllib.parse.quote(path.lstrip("/")))
                if j.get("type")=="file":
                    yield path, j.get("size",0)
                else:
                    for e in j.get("entries",[]):
                        yield from walk((path.rstrip("/") + "/" + e["name"]))
            for it in items:
                p = (base.rstrip("/") + "/" + it["name"])
                if it.get("type")=="file":
                    out = local / PurePosixPath(p).name
                    agent_download_to_file(item["host"], port, token, "/download/" + urllib.parse.quote(p.lstrip("/")), out)
                    total += out.stat().st_size; count += 1
                else:
                    # dir: recursive
                    basepos = PurePosixPath(p.rstrip("/"))
                    for rp, _sz in walk(p):
                        rel = PurePosixPath(rp).relative_to(basepos)
                        out = (local / rel.as_posix())
                        agent_download_to_file(item["host"], port, token, "/download/" + urllib.parse.quote(rp.lstrip("/")), out)
                        total += out.stat().st_size; count += 1
            return self.send_json({"ok":True,"count":count,"total":total,"total_h":human(total)})

        self.send_response(404); self.end_headers()

# tiny human size
def human(n):
    u=["B","KB","MB","GB","TB"]; i=0; n=float(n)
    while n>=1024 and i<len(u)-1: n/=1024; i+=1
    return f"{n:.1f}{u[i]}"

# ---------------------- CLI ----------------------

def run_agent_mode(quiet=False):
    cfg = load_cfg()
    threading.Thread(target=agent_discovery_loop, args=(cfg,), daemon=True).start()
    if not quiet:
        print(f"[agent] root={cfg.get('root', str(default_root()))} port={cfg.get('port',HTTP_PORT)} token={'<none>' if not cfg.get('token') else '***'}")
    run_agent_http(Path(cfg.get("root") or default_root()), int(cfg.get("port",HTTP_PORT)), cfg.get("token",""))

def run_web():
    httpd = ThreadingHTTPServer(("0.0.0.0", WEB_PORT), WebHandler)
    print(f"[web] open http://127.0.0.1:{WEB_PORT}/   本机 IPv4: {', '.join(local_ipv4s())}")
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass

def main():
    import argparse
    ips = ", ".join(local_ipv4s()) or "（未探测到）"
    examples = f"""
示例：
  # 安装/卸载后台代理（根目录默认 ~/Downloads；也可自定）
  python pyscp_web.py --install-agent
  python pyscp_web.py --install-agent --root ~/Downloads/peer --token 123456
  python pyscp_web.py --uninstall-agent

  # 启动本地 Web 控制台（浏览器打开 http://127.0.0.1:{WEB_PORT}/）
  python pyscp_web.py --web

  # 直接以代理方式运行（一般不手动执行，安装后会随登录自启）
  python pyscp_web.py --agent
本机 IPv4： {ips}
"""
    p = argparse.ArgumentParser(
        description=f"pyscp v{VER} — 浏览器可视化的局域网文件传输器（跨平台、纯 Python）。",
        formatter_class=argparse.RawTextHelpFormatter, epilog=examples)
    p.add_argument("--install-agent", action="store_true", help="安装并启动后台代理（登录自启）")
    p.add_argument("--uninstall-agent", action="store_true", help="卸载后台代理")
    p.add_argument("--agent", action="store_true", help="以代理模式运行（内部使用）")
    p.add_argument("--web", action="store_true", help="启动 Web 控制台")
    p.add_argument("--root", help="安装/运行代理的根目录（默认 ~/Downloads）")
    p.add_argument("--token", help="代理的 Token（可留空）")
    p.add_argument("--udp-port", type=int, default=UDP_PORT, help=f"发现端口（默认 {UDP_PORT}）")
    p.add_argument("--port", type=int, default=HTTP_PORT, help=f"传输端口（默认 {HTTP_PORT}）")
    p.add_argument("--quiet", action="store_true", help="代理静默运行")
    args = p.parse_args()

    if args.install_agent:
        root = norm_local_path(args.root) if args.root else default_root()
        install_agent(root, args.token or "", args.udp_port, args.port)
        print(f"agent root={root}  UDP={args.udp_port}  HTTP={args.port}  token={'<none>' if not args.token else args.token}")
        return
    if args.uninstall_agent:
        uninstall_agent(); return
    if args.agent:
        cfg = load_cfg()
        if args.root:  cfg["root"]  = str(norm_local_path(args.root))
        if args.token is not None: cfg["token"] = args.token or ""
        if args.udp_port: cfg["udp_port"] = int(args.udp_port)
        if args.port:     cfg["port"]     = int(args.port)
        save_cfg(cfg)
        run_agent_mode(quiet=args.quiet); return
    if args.web:
        run_web(); return

    p.print_help()

if __name__ == "__main__":
    main()
