import os
from dotenv import load_dotenv
import streamlit as st
from datetime import datetime, timezone
import requests
import json

# Load environment variables (for local development)
load_dotenv()

# API Configuration - Streamlit Cloud uses st.secrets, fallback to env vars
try:
    # Try Streamlit Cloud secrets first
    API_BASE_URL = st.secrets["API_BASE_URL"]
except (KeyError, FileNotFoundError):
    # Fallback to environment variables for local development
    API_BASE_URL = os.getenv("API_BASE_URL", "https://ticket-management-api-production-62d3.up.railway.app")

# Test API connection
def test_api_connection():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

# API Helper functions
def get_all_tickets():
    try:
        response = requests.get(f"{API_BASE_URL}/tickets/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch tickets: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

def create_ticket(ticket_data):
    try:
        response = requests.post(f"{API_BASE_URL}/tickets/", json=ticket_data)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Failed to create ticket: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error creating ticket: {e}")
        return None

def get_ticket_by_id(ticket_id):
    try:
        response = requests.get(f"{API_BASE_URL}/tickets/{ticket_id}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch ticket: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching ticket: {e}")
        return None

def upload_file_via_api(file_content, filename, ticket_id):
    try:
        files = {"file": (filename, file_content)}
        response = requests.post(f"{API_BASE_URL}/tickets/{ticket_id}/attachment", files=files)
        if response.status_code == 200:
            response_data = response.json()
            # Return the signed URL for accessing the file
            return response_data.get("signed_url") or response_data.get("attachment_url")
        else:
            st.error(f"Failed to upload file: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        return None

def generate_ai_reply(ticket_id, message, image_base64=None, image_filename=None):
    try:
        payload = {
            "ticket_id": ticket_id,
            "message": message
        }
        if image_base64:
            payload["image_base64"] = image_base64
            payload["image_filename"] = image_filename
            
        response = requests.post(f"{API_BASE_URL}/ai/reply", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to generate AI reply: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error generating AI reply: {e}")
        return None

def send_email_via_api(ticket_id, email_data):
    try:
        response = requests.post(f"{API_BASE_URL}/tickets/{ticket_id}/send-email", json=email_data)
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def add_reply_via_api(ticket_id, reply_data):
    try:
        response = requests.post(f"{API_BASE_URL}/tickets/{ticket_id}/replies", json=reply_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to add reply: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error adding reply: {e}")
        return None

def get_ticket_replies(ticket_id):
    try:
        # Get the full ticket data which includes replies
        response = requests.get(f"{API_BASE_URL}/tickets/{ticket_id}")
        if response.status_code == 200:
            ticket_data = response.json()
            return ticket_data.get('replies', [])
        else:
            return []
    except Exception as e:
        st.error(f"Error fetching replies: {e}")
        return []

def update_ticket_status(ticket_id, status):
    try:
        response = requests.patch(f"{API_BASE_URL}/tickets/{ticket_id}/status", json={"status": status})
        return response.status_code == 200
    except Exception as e:
        st.error(f"Error updating ticket status: {e}")
        return False

# Streamlit App
def main():
    st.set_page_config(
        page_title="🎫 ServiceNow-Style Ticket System",
        page_icon="🎫",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for beautiful styling
    st.markdown("""
    <style>
        .main > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .stApp > header {
            background-color: transparent;
        }
        .ticket-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
        }
        .chat-message {
            padding: 10px 15px;
            border-radius: 10px;
            margin: 5px 0;
            max-width: 80%;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }
        .assistant-message {
            background-color: #f5f5f5;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }
        .admin-message {
            background-color: #fff3e0;
            margin-right: auto;
            border-bottom-left-radius: 5px;
            border-left: 3px solid #ff9800;
        }
        .status-open { color: #4caf50; font-weight: bold; }
        .status-in-progress { color: #ff9800; font-weight: bold; }
        .status-closed { color: #f44336; font-weight: bold; }
        .priority-high { color: #f44336; font-weight: bold; }
        .priority-medium { color: #ff9800; font-weight: bold; }
        .priority-low { color: #4caf50; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    # Check API connection
    if not test_api_connection():
        st.error(f"⚠️ Cannot connect to API at {API_BASE_URL}")
        st.info("Please check if the API is running and the URL is correct.")
        return

    st.success(f"✅ Connected to API: {API_BASE_URL}")

    # Sidebar navigation
    st.sidebar.title("🎫 Navigation")
    page = st.sidebar.selectbox("Select Page", ["🏠 Dashboard", "➕ Create Ticket", "👤 My Tickets", "🔍 Search Tickets", "👨‍💼 Admin Panel"])

    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "➕ Create Ticket":
        create_ticket_page()
    elif page == "👤 My Tickets":
        my_tickets_page()
    elif page == "🔍 Search Tickets":
        search_tickets_page()
    elif page == "👨‍💼 Admin Panel":
        admin_panel()

def show_dashboard():
    st.title("🏠 Ticket Management Dashboard")
    
    # Get tickets data
    tickets = get_all_tickets()
    
    if not tickets:
        st.info("No tickets found. Create your first ticket!")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    open_tickets = len([t for t in tickets if t['status'] == 'Open'])
    in_progress_tickets = len([t for t in tickets if t['status'] == 'In Progress'])
    closed_tickets = len([t for t in tickets if t['status'] == 'Closed'])
    total_tickets = len(tickets)
    
    with col1:
        st.metric("Total Tickets", total_tickets)
    with col2:
        st.metric("Open", open_tickets)
    with col3:
        st.metric("In Progress", in_progress_tickets)
    with col4:
        st.metric("Closed", closed_tickets)
    
    # Recent tickets
    st.subheader("📋 Recent Tickets")
    
    # Check if user clicked "View Details" for a specific ticket
    if 'selected_ticket_id' in st.session_state:
        selected_ticket = None
        for ticket in tickets:
            if ticket['id'] == st.session_state['selected_ticket_id']:
                selected_ticket = ticket
                break
        
        if selected_ticket:
            st.subheader(f"🎫 Ticket Details - #{selected_ticket['id']}")
            if st.button("← Back to Dashboard"):
                del st.session_state['selected_ticket_id']
                st.rerun()
            
            show_ticket_details(selected_ticket)
            return
    
    # Sort tickets by creation date (newest first)
    sorted_tickets = sorted(tickets, key=lambda x: x.get('created_at', ''), reverse=True)
    
    for ticket in sorted_tickets[:10]:  # Show last 10 tickets
        with st.expander(f"🎫 #{ticket['id']} - {ticket['title']}", expanded=False):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Description:** {ticket['description'][:200]}...")
                st.write(f"**Created by:** {ticket.get('created_by', 'Unknown')}")
            with col2:
                status_class = f"status-{ticket['status'].lower().replace(' ', '-')}"
                st.markdown(f"<p class='{status_class}'>Status: {ticket['status']}</p>", unsafe_allow_html=True)
                st.write(f"**Category:** {ticket['category']}")
            with col3:
                st.write(f"**Created:** {ticket.get('created_at', 'Unknown')[:10]}")
                if st.button("View Details", key=f"view_{ticket['id']}"):
                    st.session_state['selected_ticket_id'] = ticket['id']
                    st.rerun()

def create_ticket_page():
    st.title("➕ Create New Ticket")
    
    with st.form("create_ticket_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Ticket Title*", placeholder="Brief description of the issue")
            category = st.selectbox("Category*", ["Technical", "Bug Report", "Feature Request", "General Inquiry", "Account Issue"])
            created_by = st.text_input("Your Name*", placeholder="Enter your name")
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            email = st.text_input("Your Email", placeholder="your.email@company.com")
        
        description = st.text_area("Description*", placeholder="Provide detailed information about your request...", height=150)
        
        # File upload
        uploaded_files = st.file_uploader("Attach Files (Optional)", accept_multiple_files=True)
        
        submit = st.form_submit_button("🎫 Create Ticket", use_container_width=True)
        
        if submit:
            if not all([title, category, description, created_by]):
                st.error("Please fill in all required fields (*)")
                return
            
            # Create ticket data - API only accepts title, description, category
            ticket_data = {
                "title": title,
                "description": description,
                "category": category
            }
            
            # Create ticket via API
            new_ticket = create_ticket(ticket_data)
            
            if new_ticket:
                st.success(f"✅ Ticket #{new_ticket['id']} created successfully!")
                
                # Handle file uploads after ticket creation
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        file_url = upload_file_via_api(uploaded_file.getvalue(), uploaded_file.name, new_ticket['id'])
                        if file_url:
                            st.info(f"📎 File '{uploaded_file.name}' uploaded successfully!")
                
                # Generate AI reply
                ai_response = generate_ai_reply(new_ticket['id'], f"New ticket: {title}\n\n{description}")
                if ai_response:
                    st.info("🤖 AI assistant has reviewed your ticket!")
                
                st.balloons()
                
                # Send email notification if email provided
                if email:
                    email_data = {
                        "to_email": email,
                        "subject": f"Ticket #{new_ticket['id']} Created Successfully",
                        "message": f"Your ticket '{title}' has been created and assigned ID #{new_ticket['id']}. We'll get back to you soon!"
                    }
                    if send_email_via_api(new_ticket['id'], email_data):
                        st.info("📧 Confirmation email sent!")

def my_tickets_page():
    st.title("👤 My Tickets")
    
    # Get user's name to filter tickets
    user_name = st.text_input("Enter your name to view your tickets:", placeholder="Enter the name you used when creating tickets")
    
    if user_name:
        tickets = get_all_tickets()
        my_tickets = [t for t in tickets if user_name.lower() in t.get('created_by', '').lower()]
        
        if not my_tickets:
            st.info(f"No tickets found for '{user_name}'")
            return
        
        st.success(f"Found {len(my_tickets)} tickets for '{user_name}'")
        
        for ticket in sorted(my_tickets, key=lambda x: x.get('created_at', ''), reverse=True):
            with st.expander(f"🎫 #{ticket['id']} - {ticket['title']} ({ticket['status']})", expanded=False):
                show_ticket_details(ticket)

def search_tickets_page():
    st.title("🔍 Search Tickets")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("Search tickets by title, description, or ticket ID:", placeholder="Enter search term...")
    with col2:
        search_by_id = st.text_input("Or search by Ticket ID:", placeholder="e.g., 123")
    
    # Determine search criteria
    if search_by_id:
        search_term = search_by_id.strip()
        st.info(f"🔍 Searching for Ticket ID: {search_term}")
    elif search_term:
        st.info(f"🔍 Searching for: '{search_term}'")
    
    if search_term:
        tickets = get_all_tickets()
        
        # Filter tickets based on search term
        filtered_tickets = []
        for ticket in tickets:
            # If searching by ID, exact match
            if search_by_id and str(ticket.get('id', '')) == search_term.strip():
                filtered_tickets.append(ticket)
            # General search in title, description, or ID
            elif not search_by_id and (search_term.lower() in ticket.get('title', '').lower() or 
                search_term.lower() in ticket.get('description', '').lower() or 
                search_term in str(ticket.get('id', ''))):
                filtered_tickets.append(ticket)
        
        if not filtered_tickets:
            if search_by_id:
                st.error(f"❌ No ticket found with ID: {search_term}")
            else:
                st.info("No tickets found matching your search.")
            return
        
        if search_by_id:
            st.success(f"✅ Found ticket #{search_term}")
        else:
            st.success(f"Found {len(filtered_tickets)} tickets matching '{search_term}'")
        
        for ticket in filtered_tickets:
            with st.expander(f"🎫 #{ticket['id']} - {ticket['title']}", expanded=True if search_by_id else False):
                show_ticket_details(ticket)

def show_ticket_details(ticket):
    # Ticket information section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Description:** {ticket['description']}")
        st.write(f"**Created by:** {ticket.get('created_by', 'Unknown')}")
        if ticket.get('contact_email'):
            st.write(f"**Contact:** {ticket['contact_email']}")
    
    with col2:
        status_class = f"status-{ticket['status'].lower().replace(' ', '-')}"
        st.markdown(f"<p class='{status_class}'>Status: {ticket['status']}</p>", unsafe_allow_html=True)
        st.write(f"**Category:** {ticket['category']}")
        st.write(f"**Priority:** {ticket.get('priority', 'Medium')}")
        st.write(f"**Created:** {ticket.get('created_at', 'Unknown')[:16]}")
    
    # Show main ticket attachment if exists
    if ticket.get('attachment_url'):
        st.markdown("---")
        st.markdown("📎 **Original Ticket Attachment:**")
        attachment_url = ticket['attachment_url']
        
        # Try to extract filename from URL
        try:
            if attachment_url.startswith('http'):
                # Remove query parameters first (everything after '?')
                url_without_params = attachment_url.split('?')[0]
                
                # Extract the path part after the last '/'
                path_part = url_without_params.split('/')[-1]
                
                # Handle timestamp format like "api_2025-09-04T14:30:50.602985+00:00_test.txt"
                if '_' in path_part and len(path_part.split('_')) >= 3:
                    # Find the original filename after the timestamp
                    parts = path_part.split('_')
                    # Look for parts that contain file extensions
                    for i, part in enumerate(parts):
                        if '.' in part and any(ext in part.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.pdf', '.txt', '.doc', '.xlsx']):
                            file_name = '_'.join(parts[i:])
                            break
                    else:
                        # If no extension found, take the last part
                        file_name = parts[-1] if parts else "attachment"
                else:
                    file_name = path_part
                
                # Clean up URL encoding
                file_name = file_name.replace('%20', ' ').replace('%2B', '+')
            else:
                file_name = "attachment"
        except:
            file_name = "attachment"
        
        # Display based on file type
        if any(ext in attachment_url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg']):
            try:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(attachment_url, caption=f"📷 {file_name}", use_column_width=True)
                with col2:
                    st.markdown(f"**File:** {file_name}")
                    st.markdown(f"**Type:** Image")
                    st.markdown(f"[🔗 Open in new tab]({attachment_url})")
            except Exception as e:
                st.warning(f"Could not display image: {file_name}")
                st.markdown(f"📎 [📥 Download {file_name}]({attachment_url})")
        else:
            # For non-image files, show download link with file info
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"📄 **{file_name}**")
                st.markdown(f"📎 [📥 Download File]({attachment_url})")
            with col2:
                st.markdown(f"**Type:** Document")
                st.markdown(f"[🔗 Open Link]({attachment_url})")
    
    # Show replies/conversation
    replies = get_ticket_replies(ticket['id'])
    
    st.markdown("---")
    st.subheader("💬 Conversation History")
    
    if replies and len(replies) > 0:
        st.success(f"� {len(replies)} conversation messages found")
        
        # Sort replies by timestamp if available
        try:
            sorted_replies = sorted(replies, key=lambda x: x.get('created_at', x.get('timestamp', '')))
        except:
            sorted_replies = replies
            
        for i, reply in enumerate(sorted_replies):
            # Handle different field name possibilities
            role = reply.get('role') or reply.get('reply_type', 'user')
            text = reply.get('text') or reply.get('content', '')
            timestamp = reply.get('created_at') or reply.get('timestamp', '')
            
            # Format timestamp
            time_str = ""
            if timestamp:
                try:
                    time_str = f" • {timestamp[:16]}"
                except:
                    time_str = ""
            
            if role == 'user':
                st.markdown(f'<div class="chat-message user-message">👤 <strong>User{time_str}:</strong><br>{text}</div>', unsafe_allow_html=True)
            elif role == 'ai':
                st.markdown(f'<div class="chat-message assistant-message">🤖 <strong>AI Assistant{time_str}:</strong><br>{text}</div>', unsafe_allow_html=True)
            elif role == 'admin':
                st.markdown(f'<div class="chat-message admin-message">👨‍💼 <strong>Admin{time_str}:</strong><br>{text}</div>', unsafe_allow_html=True)
            
            # Show reply attachments if any
            if reply.get('attachment_url'):
                reply_attachment = reply['attachment_url']
                st.markdown("📎 **Attachment:**")
                
                # Extract filename
                try:
                    # Remove query parameters first (everything after '?')
                    url_without_params = reply_attachment.split('?')[0]
                    
                    # Extract the path part after the last '/'
                    path_part = url_without_params.split('/')[-1]
                    
                    # Handle timestamp format like "api_2025-09-04T14:30:50.602985+00:00_test.txt"
                    if '_' in path_part and len(path_part.split('_')) >= 3:
                        parts = path_part.split('_')
                        # Look for parts that contain file extensions
                        for i, part in enumerate(parts):
                            if '.' in part and any(ext in part.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.pdf', '.txt', '.doc', '.xlsx']):
                                reply_file_name = '_'.join(parts[i:])
                                break
                        else:
                            reply_file_name = parts[-1] if parts else "attachment"
                    else:
                        reply_file_name = path_part
                    
                    # Clean up URL encoding
                    reply_file_name = reply_file_name.replace('%20', ' ').replace('%2B', '+')
                except:
                    reply_file_name = "attachment"
                
                if any(ext in reply_attachment.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg']):
                    try:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.image(reply_attachment, caption=f"📷 {reply_file_name}", width=250)
                        with col2:
                            st.markdown(f"[🔗 View Full Size]({reply_attachment})")
                    except:
                        st.markdown(f"📎 [📥 Download {reply_file_name}]({reply_attachment})")
                else:
                    st.markdown(f"📎 [📥 Download {reply_file_name}]({reply_attachment})")
            
            if i < len(sorted_replies) - 1:  # Add separator except for last message
                st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("💭 No conversation messages yet. Be the first to add a reply!")
    
    # Add reply option
    st.markdown("---")
    st.subheader("✍️ Add Your Reply")
    with st.form(f"reply_form_{ticket['id']}"):
        new_reply = st.text_area("Write your reply:", key=f"reply_{ticket['id']}", placeholder="Type your message here...")
        
        # File upload for replies
        uploaded_file = st.file_uploader("📎 Attach File (Optional)", 
                                       type=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'doc', 'docx', 'xlsx', 'zip'],
                                       key=f"reply_file_{ticket['id']}")
        
        # Show file preview if uploaded
        if uploaded_file:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.info(f"📎 **Ready to upload:**")
            with col2:
                st.write(f"**File:** {uploaded_file.name}")
                st.write(f"**Size:** {len(uploaded_file.getvalue())} bytes")
                if uploaded_file.type.startswith('image/'):
                    st.image(uploaded_file, caption="Preview", width=200)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.form_submit_button("📤 Send Reply", use_container_width=True):
                if new_reply.strip() or uploaded_file:
                    # Handle file upload first if provided
                    attachment_url = None
                    if uploaded_file:
                        with st.spinner("📤 Uploading file..."):
                            attachment_url = upload_file_via_api(uploaded_file.getvalue(), uploaded_file.name, ticket['id'])
                            if attachment_url:
                                st.success(f"📎 File '{uploaded_file.name}' uploaded successfully!")
                            else:
                                st.error("❌ Failed to upload file. Sending reply without attachment.")
                    
                    # Send reply with attachment URL if available
                    reply_text = new_reply.strip() if new_reply.strip() else f"📎 Shared a file: {uploaded_file.name if uploaded_file else 'attachment'}"
                    reply_data = {
                        "text": reply_text,
                        "role": "user"
                    }
                    
                    # Add attachment URL to reply if file was uploaded
                    if attachment_url:
                        reply_data["attachment_url"] = attachment_url
                    
                    if add_reply_via_api(ticket['id'], reply_data):
                        if attachment_url:
                            st.success("✅ Reply with attachment sent successfully!")
                        else:
                            st.success("✅ Reply sent successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to send reply. Please try again.")
                else:
                    st.warning("⚠️ Please enter a reply or attach a file before sending.")
        with col2:
            if st.form_submit_button("🔄 Refresh", use_container_width=True):
                st.rerun()

def admin_panel():
    st.title("👨‍💼 Admin Panel")
    
    # Simple admin authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state['admin_authenticated'] = False
    
    if not st.session_state['admin_authenticated']:
        with st.form("admin_login"):
            st.subheader("Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                if username == "admin" and password == "admin":
                    st.session_state['admin_authenticated'] = True
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return
    
    # Admin dashboard
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({'admin_authenticated': False}))
    
    tickets = get_all_tickets()
    
    # Admin statistics
    col1, col2, col3, col4 = st.columns(4)
    open_tickets = len([t for t in tickets if t['status'] == 'Open'])
    in_progress = len([t for t in tickets if t['status'] == 'In Progress'])
    closed_tickets = len([t for t in tickets if t['status'] == 'Closed'])
    
    with col1:
        st.metric("Total Tickets", len(tickets))
    with col2:
        st.metric("Open", open_tickets)
    with col3:
        st.metric("In Progress", in_progress)
    with col4:
        st.metric("Closed", closed_tickets)
    
    # Ticket management
    st.subheader("🎫 Manage Tickets")
    
    for ticket in sorted(tickets, key=lambda x: x.get('created_at', ''), reverse=True):
        with st.expander(f"🎫 #{ticket['id']} - {ticket['title']} ({ticket['status']})", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Description:** {ticket['description']}")
                st.write(f"**Created by:** {ticket.get('created_by', 'Unknown')}")
                st.write(f"**Category:** {ticket['category']}")
                
                # Show conversation
                replies = get_ticket_replies(ticket['id'])
                if replies:
                    st.write("**Conversation:**")
                    for reply in replies:
                        # Handle different field name possibilities  
                        role = reply.get('role') or reply.get('reply_type', 'user')
                        text = reply.get('text') or reply.get('content', '')
                        
                        if role == 'user':
                            st.markdown(f'<div class="chat-message user-message">👤 <strong>User:</strong> {text}</div>', unsafe_allow_html=True)
                        elif role == 'ai':
                            st.markdown(f'<div class="chat-message assistant-message">🤖 <strong>AI:</strong> {text}</div>', unsafe_allow_html=True)
                        elif role == 'admin':
                            st.markdown(f'<div class="chat-message admin-message">👨‍💼 <strong>Admin:</strong> {text}</div>', unsafe_allow_html=True)
                        
                        # Show attachments in admin panel conversation too
                        if reply.get('attachment_url'):
                            attachment_url = reply['attachment_url']
                            try:
                                # Remove query parameters first (everything after '?')
                                url_without_params = attachment_url.split('?')[0]
                                
                                # Extract the path part after the last '/'
                                path_part = url_without_params.split('/')[-1]
                                
                                # Handle timestamp format like "api_2025-09-04T14:30:50.602985+00:00_test.txt"
                                if '_' in path_part and len(path_part.split('_')) >= 3:
                                    parts = path_part.split('_')
                                    # Look for parts that contain file extensions
                                    for i, part in enumerate(parts):
                                        if '.' in part and any(ext in part.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.pdf', '.txt', '.doc', '.xlsx']):
                                            file_name = '_'.join(parts[i:])
                                            break
                                    else:
                                        file_name = parts[-1] if parts else "attachment"
                                else:
                                    file_name = path_part
                                
                                # Clean up URL encoding
                                file_name = file_name.replace('%20', ' ').replace('%2B', '+')
                            except:
                                file_name = "attachment"
                            
                            if any(ext in attachment_url.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']):
                                try:
                                    st.image(attachment_url, caption=f"📷 {file_name}", width=200)
                                except:
                                    st.markdown(f"📎 [📥 {file_name}]({attachment_url})")
                            else:
                                st.markdown(f"📎 [📥 {file_name}]({attachment_url})")
            
            with col2:
                # Status update
                new_status = st.selectbox("Status", ["Open", "In Progress", "Closed"], 
                                        index=["Open", "In Progress", "Closed"].index(ticket['status']),
                                        key=f"status_{ticket['id']}")
                
                if st.button("Update Status", key=f"update_{ticket['id']}"):
                    if update_ticket_status(ticket['id'], new_status):
                        st.success("Status updated!")
                        st.rerun()
                
                # Admin reply with file upload
                st.write("**💬 Admin Actions:**")
                st.info("🤖 **AI Reply Feature**: The 'Generate AI Reply' button uses artificial intelligence to automatically analyze the ticket content, conversation history, and context to provide an intelligent, helpful response. The AI will automatically post the reply to the conversation.")
                
                with st.form(f"admin_reply_{ticket['id']}"):
                    admin_reply = st.text_area("Admin Reply:", key=f"admin_reply_{ticket['id']}")
                    admin_file = st.file_uploader("📎 Attach File (Optional)", key=f"admin_file_{ticket['id']}")
                    
                    # Show admin file preview if uploaded
                    if admin_file:
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            st.info(f"📎 **Admin attachment:**")
                        with col2:
                            st.write(f"**File:** {admin_file.name}")
                            st.write(f"**Size:** {len(admin_file.getvalue())} bytes")
                            if admin_file.type.startswith('image/'):
                                st.image(admin_file, caption="Preview", width=200)
                    
                    col_reply1, col_reply2 = st.columns(2)
                    with col_reply1:
                        if st.form_submit_button("Send Reply"):
                            if admin_reply or admin_file:
                                # Upload file first if provided
                                attachment_url = None
                                if admin_file:
                                    attachment_url = upload_file_via_api(admin_file.getvalue(), admin_file.name, ticket['id'])
                                    if attachment_url:
                                        st.info(f"📎 File '{admin_file.name}' uploaded!")
                                
                                # Send reply with attachment URL if available
                                reply_text = admin_reply if admin_reply else f"📎 Shared a file: {admin_file.name if admin_file else 'attachment'}"
                                reply_data = {
                                    "text": reply_text,
                                    "role": "admin"
                                }
                                
                                # Add attachment URL to reply if file was uploaded
                                if attachment_url:
                                    reply_data["attachment_url"] = attachment_url
                                
                                if add_reply_via_api(ticket['id'], reply_data):
                                    if attachment_url:
                                        st.success("✅ Admin reply with attachment sent!")
                                    else:
                                        st.success("✅ Admin reply sent!")
                                    st.rerun()
                            else:
                                st.warning("Please enter a reply or attach a file")
                    
                    with col_reply2:
                        if st.form_submit_button("🤖 Generate AI Reply"):
                            # Show what the AI reply feature does
                            with st.spinner("🤖 AI is analyzing the ticket and generating an intelligent response..."):
                                # Get all conversation history for better context
                                conversation_context = f"Ticket: {ticket['title']}\nDescription: {ticket['description']}\n\n"
                                replies = get_ticket_replies(ticket['id'])
                                if replies:
                                    conversation_context += "Previous conversation:\n"
                                    for reply in replies:
                                        role = reply.get('role', 'user')
                                        text = reply.get('text', '')
                                        conversation_context += f"{role.title()}: {text}\n"
                                
                                # Generate AI reply with full context
                                ai_response = generate_ai_reply(ticket['id'], f"As a helpful customer service AI, provide a professional and helpful response to this ticket based on the conversation context:\n\n{conversation_context}")
                                if ai_response:
                                    st.success("🤖 AI reply automatically generated and added to the conversation!")
                                    st.info("💡 The AI analyzed the ticket content and conversation history to provide an intelligent, contextual response.")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate AI reply. Please try again.")

if __name__ == "__main__":
    main()
