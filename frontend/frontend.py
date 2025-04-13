import streamlit as st
import requests

BACKEND_URL = "https://context-aware-backend.onrender.com"

st.title("📖 Context-Aware Study Assistant")

# File upload section
st.header("Upload Study Material")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

study_material_uploaded = False  # Track if a file has been uploaded

if uploaded_file is not None:
    file_type = "application/pdf" if uploaded_file.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), file_type)}
    response = requests.post(f"{BACKEND_URL}/upload", files=files)

    if response.status_code == 200 or response.status_code == 202:
        st.success("✅ Study material uploaded and indexed successfully!")
        study_material_uploaded = True
    else:
        st.error(f"❌ Failed to upload study material: {response.json()}")

# Question-answering section
st.header("Ask a Question")
question = st.text_input("Enter your question:")
level = st.selectbox("Select Knowledge Level", ["Beginner", "Intermediate", "Advanced"])

# ✅ New toggle to allow general questions
allow_general = st.checkbox("🤖 Allow General Questions (if not in study material)")

if st.button("Get Answer"):
    if not uploaded_file:
        st.warning("⚠️ Please upload study material before asking a question.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        payload = {
            "question": question,
            "level": level,
            "allow_general": allow_general  # ✅ Include toggle value
        }

        try:
            response = requests.post(f"{BACKEND_URL}/ask", json=payload)

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", data.get("message", "No answer found."))
                st.write("### ✅ Answer:")
                st.markdown(f"> {answer}")
            else:
                st.error(f"❌ Error fetching answer: {response.json()}")
        except Exception as e:
            st.error(f"⚠️ Request failed: {e}")
