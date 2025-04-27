import streamlit as st
import requests

# Backend URL (ensure this points to your live backend)
BACKEND_URL = "https://context-aware-backend.onrender.com"

# Streamlit page configuration
st.set_page_config(page_title="Context-Aware Study Assistant", page_icon="📖")
st.title("📖 Context-Aware Study Assistant")

# File upload section
st.header("Upload Study Material (Optional)")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

# Variable to track if the study material is uploaded successfully
study_material_uploaded = False

# Handle file upload
if uploaded_file is not None:
    file_type = "application/pdf" if uploaded_file.name.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), file_type)}

    with st.spinner("🔄 Uploading and indexing study material..."):
        try:
            # Make POST request to backend for file upload
            response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=30)

            # Check for successful upload and indexing
            if response.status_code in [200, 202]:
                st.success("✅ Study material uploaded and indexed successfully!")
                study_material_uploaded = True
            else:
                st.error(f"❌ Failed to upload study material: {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Backend upload failed: {e}")

# Question-answering section
st.header("Ask a Question")
question = st.text_input("Enter your question:")
level = st.selectbox("Select Knowledge Level", ["Beginner", "Intermediate", "Advanced"])

# Handle question submission
if st.button("Get Answer"):
    if not question.strip():
        st.warning("⚠️ Please enter a question before submitting.")
    else:
        payload = {
            "question": question,
            "level": level
        }

        with st.spinner("🔍 Thinking..."):
            try:
                # Make POST request to backend to get an answer
                response = requests.post(f"{BACKEND_URL}/ask", json=payload, timeout=60)

                if response.status_code == 200:
                    # Get the answer from the response
                    data = response.json()
                    answer = data.get("answer", data.get("message", "No answer found."))
                    st.success("✅ Here's the answer:")
                    st.markdown(f"> {answer}")
                else:
                    st.error(f"❌ Error fetching answer: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Failed to connect to backend: {e}")
