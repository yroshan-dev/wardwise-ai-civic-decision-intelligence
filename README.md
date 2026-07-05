# WardWise AI: Civic Decision Intelligence Platform

### 🏙️ *WardWise AI turns civic complaints into priority scores, hotspot insights, and AI-generated decision briefs so community teams can act faster with limited resources.*

---

## 📌 Problem Statement
Municipal administrations and local community teams are flooded daily with unstructured civic complaints (e.g., waste dumping, pipeline blockages, streetlights, safety risks). The decision bottleneck is the manual review process:
1. Identifying which wards are developing into critical hotspots is slow.
2. Evaluating compound risk (e.g., a medium-severity issue that has been reported multiple times in the same ward combined with dispatch delays) is mathematically tedious.
3. Writing daily reports or resource-dispatch justifications takes hours of manual synthesis.

## 💡 Solution Overview
**WardWise AI** is a prototype civic decision intelligence tool that helps city officials, ward administrators, and civic teams move from raw complaint data to action in seconds. 
- **Dual Data Layer**: Supports loading complaints directly from a **Google BigQuery** table (`gen-lang-client-0853737784.wardwise_ai.civic_complaints`) as the primary data source, with an automatic fallback to local CSV (`data/civic_complaints.csv`) if BigQuery is disabled or fails to authenticate.
- **Automated Triage**: Calculates an explainable compound Priority Score for every issue.
- **Hotspot Detection**: Visualizes category and geographical hotspots through interactive charts.
- **AI Decision Briefs**: Uses Google Gemini to generate natural-language briefs, risk summaries, and action plans directly from current data insights.

---

## 🚀 Features
1. **Interactive Dashboard**: Metric cards tracking active caseload, high-priority issues, active hotspots, top complaints, and average delays. Includes a "What this means" narrative description.
2. **Geographical Hotspot Analysis**: Dynamic Plotly visualizations plotting complaints by ward, by category, severity percentages, and average resolution latencies.
3. **Priority Triage List**: Interactive tabular grid sorting complaints by priority score. Features real-time multi-select filters for Wards, Categories, and Priority levels. High-priority scores automatically render as visual progress bars.
4. **Gemini AI Briefing Room**: Select preset strategic questions or ask custom questions. Generating a brief invokes Gemini to summarize the situation, compile data evidence, draft immediate recommended actions, estimate impact, and flag ignored risks.

---

## 🛠️ Tech Stack
- **UI Framework**: Streamlit (Python)
- **Data Engineering**: Pandas (Python)
- **Data Visualization**: Plotly Express
- **AI Engine**: Google GenAI SDK (`google-genai` calling `gemini-2.5-flash`)
- **Configuration & Security**: Python-dotenv
- **Prototype Data Layer**: Google BigQuery table (`gen-lang-client-0853737784.wardwise_ai.civic_complaints`) as primary, with a local CSV file (`data/civic_complaints.csv`) fallback
- **Deployment**: Docker container (configured for port 8080)

---

## ☁️ Google Cloud Usage
- **Gemini API / Vertex AI**: Powers the AI Decision Briefing page, performing structured reasoning over complex complaint metrics.
- **Cloud Run**: Hosts the Streamlit web application on a scalable, serverless container platform.
- **BigQuery (Production Architecture)**: Intended production analytics warehouse to scale from CSV files to massive civic datasets (supporting real-time streaming ingestion of IoT and public-service logs).
- **Cloud Storage (Production Architecture)**: Intended storage repository for archived municipal reports, PDF attachments, and spatial logs.
- **Cloud Functions (Production Architecture)**: Intended serverless trigger layer to alert ward officials automatically when priority scores spike above threshold levels.

---

## 📐 Architecture
```
BigQuery Table / CSV Fallback Data
               ↓
    Python + Pandas Analysis
               ↓
  Priority Scoring & Hotspot Detection
               ↓
  Gemini AI Decision Brief Generation
               ↓
      Streamlit Dashboard UI
               ↓
  Cloud Run Deployment (Containerized)
```

---

## 🏆 Strong Submission Checklist

*   **Real User**:
    - A ward administrator, municipal coordinator, or civic NGO lead who has to make rapid daily decisions about where to dispatch maintenance teams and vehicles.
*   **Decision Bottleneck**:
    - Reviewing hundreds of scattered complaints. Administrators cannot easily spot geographic clusters, calculate compound risk scores, or write justification reports to dispatch teams.
*   **Data Pipeline**:
    - BigQuery Table (or CSV Fallback) $\rightarrow$ Pandas loading & pre-processing $\rightarrow$ Priority Scoring (Severity points + Repeated ward-category issue frequency + Response delay hours) $\rightarrow$ Plotly Hotspot Visualization $\rightarrow$ LLM prompt synthesis $\rightarrow$ Streamlit Dashboard.
*   **Useful Output**:
    - An explainable Priority Score, recommended dispatch actions by category (e.g., sending electrical teams or trash vehicles), and instant AI executive summaries.
*   **Acceleration Proof**:
    - Reduces manual triage review time from hours of reading spreadsheets to seconds of automated prioritization and AI summarization.

---

## 🎬 Demo Storyboard

*   **Beat 1: User + Data**:
    - The ward officer logs in and sees a dashboard with 125 complaints. Wards 6 and 8 are visibly highlighted as hotspots, with Waste, Water, and Drainage dominating.
*   **Beat 2: Build Pipeline**:
    - The officer navigates to **Priority Triage**. They see the compound scoring formula: base severity + repeat issue penalty (+5 points per complaint in the same Ward/Category) + response delay penalty (+20 points if delayed $\ge$ 24 hours).
*   **Beat 3: Add Acceleration**:
    - The officer filters the triage table to view only `Critical` and `High` issues. They see immediate suggested actions (e.g. "Send maintenance team for blockage inspection and cleaning") and can dispatch crews accordingly.
*   **Beat 4: Show Decision**:
    - The officer navigates to **AI Decision Brief** and selects: *"Generate a decision brief for the city officer"*. Gemini 2.5 Flash outputs a formatted report detailing the situation, data-backed evidence, recommended actions, impact, and risks if ignored.

---

## 💻 How to Run Locally

### Prerequisites
Make sure Python 3.9+ is installed.

### 1. Clone & Set Up Virtual Environment
Activate terminal in the project directory:
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Google Cloud BigQuery & API Keys

1. **Authenticate Google Cloud SDK** (For local BigQuery access using Application Default Credentials):
   ```bash
   gcloud auth application-default login
   ```
   *(Ensure your active project is set to `gen-lang-client-0853737784` or configure it via the environment).*

2. **Configure Environment Variables**:
   Duplicate `security.env.example` as `security.env` and configure your keys and options:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here

   # BigQuery Settings (Optional)
   USE_BIGQUERY=true
   GOOGLE_CLOUD_PROJECT=gen-lang-client-0853737784
   BIGQUERY_DATASET=wardwise_ai
   BIGQUERY_TABLE=civic_complaints
   ```
   - To run the app using local CSV data directly without trying BigQuery, set `USE_BIGQUERY=false`.
   - `security.env` is ignored by git to prevent secret leaks.

### 4. Run the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🚢 How to Deploy to Cloud Run

The containerized application is configured to run on port 8080.

### Deploy Command
Run this command from the project root:
```bash
gcloud run deploy wardwise-ai --source . --region asia-south1 --allow-unauthenticated --set-env-vars GEMINI_API_KEY=YOUR_API_KEY_HERE
```
*(Make sure to replace `YOUR_API_KEY_HERE` with your actual Google Gemini API key. The container uses Cloud Run environment variables instead of reading `security.env` inside the docker filesystem).*

---

## 📝 Demo Script
1. **Show Dashboard**: Walk through the top cards. Point out that 125 complaints are registered and explain the average response delay. Highlight the "What this means" narrative section.
2. **Show Hotspot Analysis**: Point out the 2x2 grid. Highlight that Ward 6 and Ward 8 are clearly visible hotspots. Note that Waste, Drainage, and Water are the most frequent categories.
3. **Show Triage Table**: Expand the "How the Priority Score is Calculated" section. Select `Ward 6` and `Critical` in filters. Show the progress bar illustrating priority scores. Point out the auto-assigned Suggested Action.
4. **Show AI Briefing**: Go to the AI Decision Brief page. Select *"Which ward needs the most urgent attention today?"* and click **Generate AI Brief**. Show how Gemini references Ward 6 and 8, compiles evidence, and lists specific actions with impact and risk assessments.

---

## 🔮 Future Scope
1. **BigQuery Live Integration**: Transition from static CSV loading to dynamic BigQuery queries, allowing municipal offices to ingest live complaints from municipal web portals.
2. **Speech-to-Text Complaint Logging**: Allow field officers to record audio complaints that are transcribed and classified into wards and categories using Gemini's multimodal capabilities.
3. **Geospatial Mapping**: Integrate coordinate mapping to plot hotspots directly on an interactive map overlay of the city.
