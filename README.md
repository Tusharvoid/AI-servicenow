# Ticket Management System - Streamlit Cloud Deployment

This folder contains the Streamlit frontend optimized for **Streamlit Cloud** deployment.

## 🚀 Quick Deploy to Streamlit Cloud

### 1. **Upload to GitHub**
```bash
# Create a new repository on GitHub
# Then upload these files to your repository
git init
git add .
git commit -m "Initial commit - Ticket Management System"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

### 2. **Deploy on Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select this repository and branch
5. Set main file path: `app.py`
6. Click "Deploy!"

### 3. **Configure Environment Variables**
In Streamlit Cloud app settings, add these secrets:

```toml
# In the Secrets section of your Streamlit Cloud app
API_BASE_URL = "https://ticket-management-api-production-62d3.up.railway.app"

# Optional: Email configuration
# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = "587"
# EMAIL_ADDRESS = "your-email@gmail.com"
# EMAIL_PASSWORD = "your-app-password"
```

## 📁 Files Included

- **`app.py`** - Main Streamlit application with full UI
- **`requirements.txt`** - Python dependencies for Streamlit Cloud
- **`.streamlit/config.toml`** - Streamlit configuration
- **`.env.example`** - Example environment variables
- **`README.md`** - This deployment guide

## 🔗 Backend API

This frontend connects to the Railway-deployed API:
- **API URL**: https://ticket-management-api-production-62d3.up.railway.app
- **Health Check**: https://ticket-management-api-production-62d3.up.railway.app/health
- **API Docs**: https://ticket-management-api-production-62d3.up.railway.app/docs

## ✨ Features

### **Dashboard** 🏠
- Ticket statistics and metrics
- Recent tickets overview
- View Details functionality with full conversation history

### **Create Ticket** ➕
- Form validation and file uploads
- Category selection and priority setting
- Email notifications (if configured)

### **Search** 🔍
- Search by title, description, or exact ticket ID
- Advanced search with dedicated ID lookup
- Expandable results with full details

### **Admin Panel** 👨‍💼
- Secure admin authentication (admin/admin)
- Complete ticket management
- File upload capabilities for admin replies
- AI-powered reply generation
- Status management and conversation history

### **File Management** 📎
- Image preview and display
- Secure file uploads to cloud storage
- Download links for all file types
- Support for multiple file formats

### **AI Integration** 🤖
- Intelligent reply generation
- Context-aware responses
- Automatic conversation integration

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API URL

# Run locally
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables:
- `API_BASE_URL` - Backend API URL (Required)
- `SMTP_*` - Email configuration (Optional)

### Admin Access:
- Username: `admin`
- Password: `admin`

## 📞 Support

For issues or questions:
1. Check the API health endpoint
2. Verify environment variables are set correctly
3. Ensure the Railway API is running

---

**Ready for production deployment on Streamlit Cloud!** 🚀
# AI-servicenow
