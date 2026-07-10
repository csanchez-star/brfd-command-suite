import streamlit as st
from lib import embed, regenerate, require_auth, OUTPUT

require_auth()
st.title("⏱️ Response & Dispatch")
st.caption("Dispatch-center alarm handling (NFPA 1710) and station drive-time coverage.")

tab1, tab2 = st.tabs(["Dispatch center", "Station coverage"])

with tab1:
    st.markdown("Call processing (alarm → first unit dispatched), benchmarked to NFPA 1710 — "
                "with year-over-year, by-hour, call-type, and concurrent-call cuts.")
    embed("BRFD_Dispatch_Center_Analysis.html", height=680)
    regenerate("dispatch_center_report.py", label="Regenerate dispatch analysis (YTD vs prior year)", slow=True)

with tab2:
    st.markdown("NFPA 4- and 8-minute drive-time isochrones per station.")
    a, b, c = st.columns(3)
    a.metric("Within 4-min drive", "61%")
    b.metric("Within 8-min drive", "63%")
    c.metric("Outside 8-min (gaps)", "37%")
    st.caption("Pre-rendered snapshot — of a recent 999-incident sample, **61% fell within a "
               "4-minute drive** of a station. The full interactive map is large (2 MB), so it's a "
               "download rather than an inline embed (embedding it crashed the hosted app):")
    _cov = OUTPUT / "BRFD_Station_Coverage.html"
    if _cov.exists():
        st.download_button("⬇ Download the interactive coverage map (HTML)",
                           _cov.read_bytes(), file_name="BRFD_Station_Coverage.html",
                           mime="text/html")
    else:
        st.info("Coverage map not generated yet — run `python analysis/station_coverage.py` locally.")
