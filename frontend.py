import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000"

st.title("📖 Context-Aware Study Assistant")

# File upload section
st.header("Upload Study Material")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

study_material_uploaded = False  # Track if a file has been uploaded

if uploaded_file is not None:
    file_type = "application/pdf" if uploaded_file.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), file_type)}
    response = requests.post(f"{BACKEND_URL}/upload", files=files)

    if response.status_code == 200:
        st.success("✅ Study material uploaded and indexed successfully!")
        study_material_uploaded = True
    else:
        st.error(f"❌ Failed to upload study material: {response.json()}")

# Question-answering section
st.header("Ask a Question")
question = st.text_input("Enter your question:")
level = st.selectbox("Select Knowledge Level", ["Beginner", "Intermediate", "Advanced"])

if st.button("Get Answer"):
    if not study_material_uploaded:
        st.warning("⚠️ Please upload study material before asking a question.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        payload = {"question": question, "level": level}
        response = requests.post(f"{BACKEND_URL}/ask", json=payload)

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            st.write("### Answer:")
            st.write(answer)
        else:
            st.error(f"❌ Error fetching answer: {response.json()}")
