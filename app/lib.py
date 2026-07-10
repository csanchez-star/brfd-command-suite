"""Shared helpers for the BRFD Command Suite Streamlit app."""
import os, sys, subprocess
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
ANALYSIS = ROOT / "analysis"
OUTPUT = ANALYSIS / "output"
for p in (str(ROOT), str(ANALYSIS)):     # import firstdue_mcp, brla, reference, analyses
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass  # no .env on hosted deploys; secrets come from st.secrets / env vars

# Bridge Streamlit Cloud secrets -> env vars so the First Due client (reads os.environ) works
# on hosted deploys where you set secrets in the platform UI instead of committing a .env.
try:
    for _k, _v in st.secrets.items():
        os.environ.setdefault(_k, str(_v))
except Exception:
    pass


def require_auth():
    """Password gate. Active only when APP_PASSWORD is set (env or st.secrets) — so local/LAN
    runs stay open, but any hosted deploy is protected. Call at the top of every page."""
    pw = os.environ.get("APP_PASSWORD")
    if not pw:
        return
    if st.session_state.get("_authed"):
        return
    st.markdown("## 🔒 BRFD Command Suite")
    st.caption("Restricted — internal fire-department data.")
    entered = st.text_input("Password", type="password")
    if entered:
        if entered == pw:
            st.session_state["_authed"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


@st.cache_resource
def get_client():
    from firstdue_mcp.client import FirstDueClient
    return FirstDueClient(timeout=90)


def embed(filename, height=620):
    """Embed a generated self-contained HTML report/map from analysis/output/."""
    p = OUTPUT / filename
    if p.exists():
        components.html(p.read_text(encoding="utf-8"), height=height, scrolling=True)
        st.caption(f"Source: analysis/output/{filename}")
    else:
        st.info(f"Not generated yet ({filename}). Use the button below to build it.")


def regenerate(script, args=None, label=None, slow=False):
    """Button that runs an analysis script (in analysis/) as a subprocess, streaming its
    output live so you can watch it work (a real progress meter)."""
    if slow:
        st.caption("⏳ This one pulls a lot of data / heavy compute — give it a minute.")
    if not st.button(label or f"Regenerate ({script})", key=f"regen_{script}"):
        return
    lines, rc = [], None
    with st.status(f"Running {script} …", expanded=True) as status:
        log = st.empty()
        proc = subprocess.Popen(
            [sys.executable, "-u", str(ANALYSIS / script)] + (args or []),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            cwd=str(ANALYSIS), bufsize=1,
        )
        for line in proc.stdout:                 # live stream
            lines.append(line.rstrip("\n"))
            log.code("\n".join(lines[-18:]) or "…")
        rc = proc.wait()
        if rc == 0:
            status.update(label=f"{script} — done ✅", state="complete", expanded=False)
        else:
            status.update(label=f"{script} — failed ❌", state="error")
    if rc == 0:
        st.rerun()   # reload so the freshly-built map/report embeds below
