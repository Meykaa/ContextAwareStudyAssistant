import streamlit as st
import requests

# Backend URL
BACKEND_URL = "https://context-aware-backend-4ft4.onrender.com"  # Change this when deploying

st.set_page_config(page_title="Context-Aware Study Assistant", layout="centered")
st.title("📖 Context-Aware Study Assistant")

# =========================
# Upload Section
# =========================
st.header("Upload Study Material")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

# Maintain upload state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

if uploaded_file is not None:
    file_type = None
    if uploaded_file.name.endswith(".pdf"):
        file_type = "application/pdf"
    elif uploaded_file.name.endswith(".docx"):
        file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    if file_type:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), file_type)}
        try:
            response = requests.post(f"{BACKEND_URL}/upload", files=files)
            if response.status_code in (200, 202):
                st.success("✅ Study material uploaded successfully!")
                st.session_state.uploaded = True
            else:
                st.error(f"🔍 Failed to upload study material: {response.json()}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Upload failed: {e}")
    else:
        st.error("🔍 Unsupported file format. Please upload a PDF or DOCX file.")

# =========================
# Ask a Question Section
# =========================
st.header("Ask a Question")
level = st.selectbox("Select Knowledge Level", ["Beginner", "Intermediate", "Advanced"])

# Initialize question text in session state
if "question" not in st.session_state:
    st.session_state.question = ""

# Handle question input
with st.form(key="qa_form"):
    question = st.text_input("Enter your question:", value=st.session_state.question)
    submit = st.form_submit_button("Get Answer")

# Handle submit
if submit or question.strip():
    if not st.session_state.uploaded:
        st.warning("⚠️ Please upload study material before asking a question.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question.")
    else:
        payload = {"question": question, "level": level}
        try:
            response = requests.post(f"{BACKEND_URL}/ask", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "answer" in data:
                    st.subheader("Answer:")
                    st.write(data["answer"])
                elif "message" in data:
                    st.warning(data["message"])
                else:
                    st.info("ℹ️ No clear answer found.")
            else:
                st.error(f"🔍 Error fetching answer: {response.json()}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {e}")
