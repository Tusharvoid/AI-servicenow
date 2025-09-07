
# 🚀 AI-Powered ServiceNow Ticketing & Monitoring Platform

This project demonstrates a **cloud-native AI-powered workflow** that integrates multiple services to automate **ServiceNow ticketing, monitoring, and visualization**.  

---

## 📌 Architecture Overview

The platform combines several components:

1. **Ticketing Website** – [AI ServiceNow Ticket Portal](https://ai-sservicenow.streamlit.app/)  
   - Built with **Streamlit**  
   - Allows users to raise and track tickets  
   - Provides a simple UI for interaction  

2. **Database (Supabase on S3)** – [Supabase Project](https://supabase.com/dashboard/project/sctacmxkbbigfbtmiaqr)  
   - Stores tickets, user data, and workflow history  
   - Acts as the **central data layer**  

3. **Monitoring (Grafana + Prometheus on Railway)**  
   - Collects system & application metrics  
   - Provides live dashboards to visualize performance  

4. **Automation & AI Orchestration (n8n)**  
   - Executes workflows to automate ticket assignment, escalation, and AI responses  
   - Integrates with ServiceNow-like system for ticket lifecycle  

5. **Frontend Showcase (SkyClub Website)**  
   - Final user-facing demo site to showcase the complete system  

---

## 🛠️ Workflow (High-Level)

1. A user creates a ticket on the **Streamlit portal**.  
2. The ticket is stored in **Supabase (Postgres/S3 backend)**.  
3. **n8n workflow** is triggered → it processes ticket details with AI and routes it.  
4. **Prometheus** collects metrics from services → visualized in **Grafana** dashboards.  
5. **SkyClub** acts as a showcase site for demonstrating the full integration.  

---

## 🔧 Tech Stack

- **Frontend**: Streamlit, SkyClub (showcase)  
- **Backend**: Supabase (Postgres + S3), n8n workflows  
- **Monitoring**: Grafana + Prometheus (Railway deployment)  
- **Automation**: n8n AI workflows (ticket management, escalation)  
- **Cloud Hosting**: Railway, Supabase, Streamlit Cloud  

---

## 📊 Example Use Case

- A user reports *"Server CPU usage high"*.  
- The ticket is logged in **Supabase**.  
- **n8n AI workflow** analyzes → decides if escalation needed.  
- If critical → auto-escalates + updates ticket.  
- Metrics are tracked in **Prometheus** and visualized on **Grafana dashboard**.  

---

## 🚀 How to Run

1. Deploy the **Streamlit app** for ticketing.  
2. Connect **Supabase DB** (acts as centralized data layer).  
3. Configure **n8n workflows** for ticket automation.  
4. Deploy **Grafana + Prometheus** on Railway for monitoring.  
5. Use **SkyClub site** to demonstrate the system end-to-end.  

---

## 📌 Future Improvements

- Add real **ServiceNow API integration** instead of demo portal.  
- Use **LLM-based triage system** for smarter ticket categorization.  
- Expand monitoring to include **logs & traces** (OpenTelemetry).  
- Multi-tenant support for enterprise adoption.  

---

## 🤝 Contribution

Feel free to fork, improve, and contribute to the project!  

---

## 📄 License

MIT License © 2025  
