import streamlit as st
import requests
import os
from datetime import datetime
from typing import Optional

# Page configuration
st.set_page_config(
    page_title="Storage Web",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_URL = "http://localhost:8000/api"

# ==================== Session State ====================

if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None


# ==================== Utility Functions ====================

def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Registration successful! Please login.")
            return True
        else:
            st.error(response.json().get("detail", "Registration failed"))
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def login_user(username: str, password: str) -> bool:
    """Login user"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.user_id = data["user_id"]
            st.session_state.username = data["username"]
            st.success(f"Welcome {username}!")
            return True
        else:
            st.error("Invalid credentials")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def logout_user():
    """Logout user"""
    st.session_state.token = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.success("Logged out successfully!")


def upload_file(uploaded_file, token: str) -> bool:
    """Upload file to server"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        headers = {"Authorization": f"Bearer {token}"}
        params = {"token": token}
        
        response = requests.post(
            f"{API_URL}/files/upload",
            files=files,
            params=params
        )
        
        if response.status_code == 200:
            st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
            return True
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def get_user_files(token: str, file_type: Optional[str] = None) -> list:
    """Get list of files for current user"""
    try:
        if file_type:
            url = f"{API_URL}/files/by-type/{file_type}"
        else:
            url = f"{API_URL}/files"
        
        params = {"token": token}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("files", [])
        else:
            st.error("Failed to fetch files")
            return []
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []


def delete_file(file_id: str, token: str) -> bool:
    """Delete a file"""
    try:
        params = {"token": token}
        response = requests.delete(
            f"{API_URL}/files/{file_id}",
            params=params
        )
        
        if response.status_code == 204:
            st.success("File deleted successfully!")
            return True
        else:
            st.error("Failed to delete file")
            return False
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False


def download_file(file_id: str, token: str):
    """Download a file"""
    try:
        params = {"token": token}
        response = requests.get(
            f"{API_URL}/files/download/{file_id}",
            params=params
        )
        
        if response.status_code == 200:
            return response.content
        else:
            st.error("Failed to download file")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


# ==================== UI Rendering ====================

def render_auth_page():
    """Render authentication page"""
    st.title("🔐 Storage Web")
    st.subheader("Secure File Management System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Register")
        with st.form("register_form"):
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.form_submit_button("Register"):
                if not reg_username or not reg_email or not reg_password:
                    st.error("Please fill all fields")
                elif reg_password != reg_confirm:
                    st.error("Passwords don't match")
                elif register_user(reg_username, reg_email, reg_password):
                    st.rerun()
    
    with col2:
        st.markdown("### Login")
        with st.form("login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.form_submit_button("Login"):
                if login_user(login_username, login_password):
                    st.rerun()


def render_dashboard():
    """Render main dashboard"""
    st.title("📁 Storage Web Dashboard")
    
    # Sidebar
    with st.sidebar:
        st.write(f"**Logged in as:** {st.session_state.username}")
        
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 All Files", "🏷️ Filter by Type"])
    
    # Tab 1: Upload
    with tab1:
        st.header("Upload Files")
        st.markdown("**Supported:** Images (jpg, png, gif) & Documents (pdf, doc, docx, txt, xlsx)")
        
        uploaded_file = st.file_uploader("Choose a file to upload", key="file_uploader")
        
        if uploaded_file is not None:
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("📤 Upload"):
                    upload_file(uploaded_file, st.session_state.token)
            with col2:
                st.info(f"File: {uploaded_file.name} ({uploaded_file.size} bytes)")
    
    # Tab 2: All Files
    with tab2:
        st.header("Your Files")
        
        if st.button("🔄 Refresh"):
            st.rerun()
        
        files = get_user_files(st.session_state.token)
        
        if not files:
            st.info("No files uploaded yet. Go to Upload tab to add files.")
        else:
            st.write(f"**Total Files:** {len(files)}")
            
            for file in files:
                col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
                
                with col1:
                    icon = "🖼️" if file["file_type"] == "image" else "📄"
                    st.write(f"{icon} {file['filename']}")
                
                with col2:
                    file_size_mb = file["file_size"] / (1024 * 1024)
                    st.write(f"{file_size_mb:.2f} MB")
                
                with col3:
                    uploaded_at = datetime.fromisoformat(file["uploaded_at"].replace("Z", "+00:00"))
                    st.write(uploaded_at.strftime("%Y-%m-%d %H:%M"))
                
                with col4:
                    if st.button("⬇️", key=f"download_{file['id']}"):
                        file_content = download_file(file["id"], st.session_state.token)
                        if file_content:
                            st.download_button(
                                label="Download",
                                data=file_content,
                                file_name=file["filename"],
                                key=f"dl_btn_{file['id']}"
                            )
                
                with col5:
                    if st.button("🗑️", key=f"delete_{file['id']}"):
                        delete_file(file["id"], st.session_state.token)
                        st.rerun()
                
                st.divider()
    
    # Tab 3: Filter by Type
    with tab3:
        st.header("Filter by Type")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🖼️ Images"):
                images = get_user_files(st.session_state.token, "image")
                if images:
                    for img in images:
                        st.image(img["filename"], caption=img["filename"])
                        st.write(f"Size: {img['file_size'] / (1024*1024):.2f} MB")
                        if st.button("🗑️ Delete", key=f"del_img_{img['id']}"):
                            delete_file(img["id"], st.session_state.token)
                            st.rerun()
                else:
                    st.info("No images uploaded")
        
        with col2:
            if st.button("📄 Documents"):
                documents = get_user_files(st.session_state.token, "document")
                if documents:
                    for doc in documents:
                        st.write(f"📄 {doc['filename']}")
                        st.write(f"Size: {doc['file_size'] / (1024*1024):.2f} MB")
                        if st.button("🗑️ Delete", key=f"del_doc_{doc['id']}"):
                            delete_file(doc["id"], st.session_state.token)
                            st.rerun()
                else:
                    st.info("No documents uploaded")


# ==================== Main App ====================

def main():
    if st.session_state.token is None:
        render_auth_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
