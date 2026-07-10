import streamlit as st
from lib import embed, regenerate, require_auth

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
    st.markdown("NFPA 4- and 8-minute drive-time isochrones per station, with incidents that fall "
                "outside coverage highlighted.")
    st.caption("⏳ Heavy map — it downloads the parish street network and computes drive-time "
               "isochrones, so it can take a few minutes (and a lot of memory) to rebuild.")
    embed("BRFD_Station_Coverage.html", height=620)
    regenerate("station_coverage.py", label="Regenerate coverage map", slow=True)
