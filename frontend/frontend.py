import streamlit as st
import requests

# Backend URL (make sure to change it to your actual backend URL when deploying)
BACKEND_URL = "http://127.0.0.1:5000"  # Update for production

st.title("📖 Context-Aware Study Assistant")

# File upload section
st.header("Upload Study Material")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])
study_material_uploaded = False  # Track if a file has been uploaded

if uploaded_file is not None:
    file_type = None
    if uploaded_file.name.endswith(".pdf"):
        file_type = "application/pdf"
    elif uploaded_file.name.endswith(".docx"):
        file_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif uploaded_file.name.endswith(".txt"):
        file_type = "text/plain"
    
    if file_type:  # If it's one of the supported file types
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), file_type)}
        response = requests.post(f"{BACKEND_URL}/upload", files=files)
        
        if response.status_code == 200:
            st.success("✅ Study material uploaded and indexed successfully!")
            study_material_uploaded = True
        else:
            st.error(f"❌ Failed to upload study material: {response.json()}")
    else:
        st.error("❌ Unsupported file format. Please upload a PDF, DOCX, or TXT file.")

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
        payload = {"question": question}  # Knowledge level will be ignored as per the backend code
        response = requests.post(f"{BACKEND_URL}/ask", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            st.write("### Answer:")
            st.write(answer)
        else:
            st.error(f"❌ Error fetching answer: {response.json()}")


