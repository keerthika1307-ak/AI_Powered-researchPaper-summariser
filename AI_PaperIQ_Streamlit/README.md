# AI_PaperIQ Streamlit App (Ready-to-run)

This is a Streamlit-based Research Paper Summariser using Google Gemini and ArXiv.

## Quick start
1. Create and activate a virtual environment
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - macOS / Linux:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Gemini API key.
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Open the URL printed by Streamlit (usually http://localhost:8501).

## Notes
- API costs: Gemini calls may incur costs. Use `flash` for testing and `pro` for higher-quality summaries.
- PDF extraction uses PyMuPDF (fast). For large PDFs, extraction may take time.
- The app includes multiple visualizations: word/sentence counts, cosine similarity, keyword overlap, top keywords chart, and Flesch reading ease.