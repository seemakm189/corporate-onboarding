import time
import random
import streamlit as st

st.set_page_config(page_title="Onboarding Extract Agent Demo", layout="wide")

# ---------- MOCK DATA / HELPERS ----------

def init_state():
    if "clients" not in st.session_state:
        st.session_state.clients = [
            {
                "id": "C001",
                "name": "Acme Manufacturing Ltd",
                "status": "Docs pending",
                "progress": 5,
                "has_profile": False,
                "fields": {
                    "Registered Name": "",
                    "Registration Number": "",
                    "Country of Incorporation": "",
                    "Address": "",
                    "Industry": ""
                }
            },
            {
                "id": "C002",
                "name": "Brightside Retail Group",
                "status": "In review",
                "progress": 20,
                "has_profile": True,
                "fields": {
                    "Registered Name": "Brightside Retail Group Plc",
                    "Registration Number": "BRG-84291",
                    "Country of Incorporation": "United Kingdom",
                    "Address": "10 High Street, London",
                    "Industry": "Retail"
                }
            },
        ]

    if "selected_client_id" not in st.session_state:
        st.session_state.selected_client_id = None

    if "upload_in_progress" not in st.session_state:
        st.session_state.upload_in_progress = False

    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None

    if "confirmed" not in st.session_state:
        st.session_state.confirmed = False

    if "kyc_started" not in st.session_state:
        st.session_state.kyc_started = False


def get_selected_client():
    if st.session_state.selected_client_id is None:
        return None
    for c in st.session_state.clients:
        if c["id"] == st.session_state.selected_client_id:
            return c
    return None


def simulate_extraction(client):
    # mock extracted fields
    base = {
        "Registered Name": client["name"],
        "Registration Number": f"{client['id']}-REG-{random.randint(100,999)}",
        "Country of Incorporation": "United Kingdom",
        "Address": f"{random.randint(1,99)} Example Street, London",
        "Industry": "Manufacturing" if "Acme" in client["name"] else "Retail",
    }
    return base


init_state()

# ---------- LAYOUT: HEADER ----------
st.title("Colleague Portal – Onboarding Agent Demo")

st.caption(
    "Flow: dashboard → select client with missing data → upload docs → agent extraction "
    "→ colleague review & edit → confirm → KYC next steps."
)

# ---------- STEP 1: CLIENT DASHBOARD ----------
st.subheader("Client Dashboard")

cols = st.columns([1, 3, 2, 2])
with cols[0]:
    st.markdown("**Client ID**")
with cols[1]:
    st.markdown("**Client Name**")
with cols[2]:
    st.markdown("**Status**")
with cols[3]:
    st.markdown("**Progress**")

for client in st.session_state.clients:
    c1, c2, c3, c4 = st.columns([1, 3, 2, 2])
    with c1:
        if st.button(client["id"], key=f"select_{client['id']}"):
            st.session_state.selected_client_id = client["id"]
            st.session_state.upload_in_progress = False
            st.session_state.extracted_data = None
            st.session_state.confirmed = False
            st.session_state.kyc_started = False
    with c2:
        st.write(client["name"])
    with c3:
        # highlight missing data
        if client["progress"] < 20:
            st.markdown(f":red[{client['status']}]")
        else:
            st.write(client["status"])
    with c4:
        st.progress(client["progress"] / 100)
        st.write(f"{client['progress']}%")

st.markdown("---")

client = get_selected_client()
if client is None:
    st.info("Select a client record (preferably one in red) to start the demo.")
    st.stop()

# ---------- STEP 2: CLIENT DOC UPLOAD ----------
st.subheader(f"Client Workspace – {client['name']} ({client['id']})")

left, right = st.columns([2, 1])

with left:
    st.markdown("**1. Upload onboarding documents**")
    uploaded_files = st.file_uploader(
        "Upload one or more documents (PDF, images, etc.)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        key="uploader",
    )

    if uploaded_files and not st.session_state.upload_in_progress and st.button("Start extraction with Agent"):
        st.session_state.upload_in_progress = True
        st.session_state.confirmed = False
        st.session_state.kyc_started = False
        with st.spinner("Agent in progress – extracting key fields from documents..."):
            time.sleep(2)  # short wait just for demo feel
            st.session_state.extracted_data = simulate_extraction(client)
            st.session_state.upload_in_progress = False
        st.success("Document upload completed and extraction finished.")

    if st.session_state.upload_in_progress:
        st.info("Agent is extracting data. This panel mimics the agent progress on the dashboard.")
        st.progress(60)

    if st.session_state.extracted_data:
        st.success("Extraction complete. Click the same customer row to review details in a side panel (below).")

with right:
    st.markdown("**Agent Status**")
    if st.session_state.upload_in_progress:
        st.write("Running")
    elif st.session_state.extracted_data:
        st.write("Completed")
    else:
        st.write("Idle")

    st.markdown("**Next milestone**")
    if st.session_state.confirmed:
        st.write("KYC checks")
    else:
        st.write("Profile confirmation")

st.markdown("---")

# ---------- STEP 3: SIDE PANEL REVIEW / EDIT ----------
st.subheader("Extracted Data – Review & Edit")

if st.session_state.extracted_data is None:
    st.info("Upload documents and run the agent to see extracted data.")
else:
    with st.form("review_form"):
        edited = {}
        for field, value in st.session_state.extracted_data.items():
            edited[field] = st.text_input(field, value=value)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            reject = st.form_submit_button("Reject & Re‑upload")
        with col_b:
            confirm = st.form_submit_button("Confirm – create client profile")
        with col_c:
            st.form_submit_button("Save draft", disabled=True)

    if reject:
        st.warning("Correction captured. In a full build, this would be fed back as agent learning.")
        # emulate "learning"
        st.session_state.extracted_data = edited

    if confirm:
        st.session_state.confirmed = True
        # persist edited fields into client record
        client["fields"] = edited
        client["has_profile"] = True
        # update dashboard progress to 20%
        client["progress"] = max(client["progress"], 20)
        client["status"] = "Profile created – KYC pending"
        st.success("Client profile created. Progress increased to 20% and next steps generated.")

# ---------- STEP 4: CLIENT PROFILE & NEXT STEPS ----------
if client["has_profile"]:
    st.markdown("---")
    st.subheader("Client Profile Snapshot")

    prof_left, prof_right = st.columns([2, 2])
    with prof_left:
        for k, v in client["fields"].items():
            st.write(f"**{k}:** {v}")

    with prof_right:
        st.markdown("**Pending next steps**")
        kyc_tasks = [
            "KYC / KYB questionnaire",
            "PEP / sanctions screening",
            "Adverse media checks",
            "Ownership & control verification",
        ]
        for t in kyc_tasks:
            st.checkbox(t, key=f"{client['id']}_{t.replace(' ', '_')}", value=False, disabled=True)

        if st.session_state.confirmed and st.button("Show start of next step – KYC checks"):
            st.session_state.kyc_started = True

        if st.session_state.kyc_started:
            st.info("KYC checks initiated. In a full solution this would segue to the data aggregator / screening agent.")

# Footer
st.markdown("---")
st.caption("This is a non-functional demo to showcase the colleague journey and agent interaction.")
