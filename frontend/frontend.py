import streamlit as st
import requests

# Backend URL (make sure to change it to your actual backend URL when deploying)
BACKEND_URL = "https://context-aware-backend-4ft4.onrender.com"  # Update for production

st.title("📖 Context-Aware Study Assistant")

# File upload section
st.header("Upload Study Material")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])
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
            st.error(f"🔍 Failed to upload study material: {response.json()}")  
    else:
        st.error("🔍 Unsupported file format. Please upload a PDF, DOCX, or TXT file.")  

# Question-answering section
st.header("Ask a Question")
level = st.selectbox("Select Knowledge Level", ["Beginner", "Intermediate", "Advanced"])  # ⬅️ Moved up

# Using form to handle Enter key submit
with st.form(key="qa_form"):
    question = st.text_input("Enter your question:")
    submit = st.form_submit_button("Get Answer")  # Still keeps the button

if submit:
    if not study_material_uploaded:
        st.warning("⚠️ Please upload study material before asking a question.")
    elif not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        payload = {"question": question, "level": level}  # Knowledge level will be ignored as per the backend code
        response = requests.post(f"{BACKEND_URL}/ask", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer found.")
            st.write("### Answer:")
            st.write(answer)

            # New feature: Show suggested topics if RAG fails
            if "suggested_topics" in data and data["suggested_topics"]:
                st.info("Try asking about topics like: " + ", ".join(data["suggested_topics"]))
        else:
            st.error(f"🔍 Error fetching answer: {response.json()}")  # Emoji changed here
