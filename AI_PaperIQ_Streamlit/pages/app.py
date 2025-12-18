import streamlit as st
from utils import llm_service , pdf_extractor, text_analysis
import time
import requests
import textwrap
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import xml.etree.ElementTree as ET

# --------------------------------------------------------------------------------
# LOGIN PROTECTION
# --------------------------------------------------------------------------------
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.switch_page("pages/login.py")

# --------------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------------
st.set_page_config(
    page_title="AI PaperIQ – Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------------
# GLOBAL NEON + GLASS THEME
# --------------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 55%),
                radial-gradient(circle at bottom right, rgba(236,72,153,0.18), transparent 55%),
                #020617;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.85);
    backdrop-filter: blur(18px);
    border-right: 1px solid rgba(148,163,184,0.3);
}
section[data-testid="stSidebar"] > div {
    padding: 1.2rem 0.9rem;
}
.sidebar-glass {
    background: rgba(15,23,42,0.9);
    border-radius: 18px;
    padding: 1rem;
    border: 1px solid rgba(59,130,246,0.35);
    box-shadow: 0 0 22px rgba(15,23,42,0.9);
    animation: slideInLeft 0.7s ease-out;
}
.sidebar-title {
    font-weight: 700;
    font-size: 1rem;
    color: #e5e7eb;
    margin-bottom: 0.3rem;
}
.sidebar-sub {
    color: #9ca3af;
    font-size: 0.8rem;
    margin-bottom: 0.8rem;
}
.sidebar-nav-item {
    padding: 0.35rem 0.55rem;
    border-radius: 10px;
    font-size: 0.88rem;
    color: #cbd5f5;
    cursor: pointer;
    margin-bottom: 0.1rem;
    transition: 0.2s;
}
.sidebar-nav-item:hover {
    background: rgba(59,130,246,0.15);
}
.sidebar-nav-active {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white;
}

/* HERO HEADER */
.hero-header {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 40%, #ec4899 100%);
    padding: 1.75rem 2rem;
    border-radius: 22px;
    margin-bottom: 1.5rem;
    box-shadow: 0 0 32px rgba(59,130,246,0.6);
    border: 1px solid rgba(255,255,255,0.15);
    animation: fadeInUp 0.8s ease-out;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    color: #f9fafb;
    letter-spacing: -0.02em;
}
.hero-subtitle {
    color: rgba(241,245,249,0.9);
    margin-top: 0.25rem;
    font-size: 0.95rem;
}

/* PROFILE CHIP */
.profile-chip {
    background: rgba(15,23,42,0.65);
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    border: 1px solid rgba(148,163,184,0.6);
    color: #e5e7eb;
    font-size: 0.9rem;
}

/* TOP CONFIG BAR */
.top-config-bar {
    background: rgba(15,23,42,0.80);
    border-radius: 20px;
    padding: 1.2rem 1.6rem;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(59,130,246,0.4);
    box-shadow: 0 0 26px rgba(15,23,42,0.85);
    backdrop-filter: blur(14px);
    animation: fadeInUp 0.9s ease-out;
}

/* GLASS CARDS */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: radial-gradient(circle at top left, rgba(59,130,246,0.16), transparent 50%),
                rgba(15,23,42,0.9) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 28px rgba(15,23,42,0.98) !important;
}

/* NEON BUTTONS */
.stButton > button {
    border-radius: 14px !important;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    border: none !important;
    color: #f9fafb !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.75rem !important;
    width: 100% !important;
    box-shadow:
        0 0 12px rgba(59,130,246,0.6),
        0 0 22px rgba(139,92,246,0.55);
    animation: pulseBtn 2.4s infinite ease-in-out;
    transition: all 0.25s ease;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow:
        0 0 22px rgba(59,130,246,0.9),
        0 0 32px rgba(139,92,246,0.85);
}

/* INPUTS */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(15,23,42,0.85) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(59,130,246,0.5) !important;
    color: #e5e7eb !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 1px rgba(96,165,250,0.9) !important;
}

/* SELECTBOX */
.stSelectbox > div > div {
    background: rgba(15,23,42,0.8) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(59,130,246,0.5) !important;
}

/* METRICS */
[data-testid="stMetricValue"] {
    color: #60a5fa !important;
}
[data-testid="stMetricLabel"] {
    color: #94a3b8 !important;
}

/* CHAT HEADER */
.chat-header-custom {
    background: linear-gradient(135deg,#1e3a8a,#3b82f6);
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    color: #f9fafb;
    font-weight: 600;
    margin-bottom: 10px;
}

/* NEON LOADER */
.neon-loader {
    width: 70px;
    height: 70px;
    border-radius: 999px;
    border: 3px solid rgba(59,130,246,0.3);
    border-top-color: #60a5fa;
    border-right-color: #a855f7;
    animation: spin 0.8s linear infinite, glowPulse 1.8s ease-in-out infinite;
    margin: 0 auto 0.5rem auto;
}
.neon-loader-text {
    text-align: center;
    font-size: 0.9rem;
    color: #e5e7eb;
}

/* Animations */
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes glowPulse {
    0% { box-shadow: 0 0 6px rgba(59,130,246,0.5); }
    50% { box-shadow: 0 0 20px rgba(139,92,246,1); }
    100% { box-shadow: 0 0 6px rgba(59,130,246,0.5); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-18px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulseBtn {
    0% { box-shadow: 0 0 10px rgba(59,130,246,0.5); }
    50% { box-shadow: 0 0 24px rgba(59,130,246,0.9); }
    100% { box-shadow: 0 0 10px rgba(59,130,246,0.5); }
}

/* Gradient titles */
h1, h2, h3 {
    background: linear-gradient(135deg,#e0f2fe,#bfdbfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""",
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------------
# SESSION STATE SETUP
# --------------------------------------------------------------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # [{role, text}]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hi! I'm your AI research assistant inside AI PaperIQ."}
    ]

if "user_name" not in st.session_state:
    st.session_state.user_name = "Researcher"

if "user_email" not in st.session_state:
    st.session_state.user_email = "user@example.com"

# saved summaries history
if "session_summaries" not in st.session_state:
    st.session_state.session_summaries = []  # list of dict
if "current_summary_index" not in st.session_state:
    st.session_state.current_summary_index = None

# default UI preferences
if "default_mode" not in st.session_state:
    st.session_state.default_mode = "Paste text"
if "default_model" not in st.session_state:
    st.session_state.default_model = "auto"
if "compact_view" not in st.session_state:
    st.session_state.compact_view = False

# arxiv search state
if "arxiv_results" not in st.session_state:
    st.session_state.arxiv_results = []
if "selected_paper_index" not in st.session_state:
    st.session_state.selected_paper_index = 0

# --------------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------------
def type_writer(placeholder, text: str, delay: float = 0.012):
    """Animated typing effect for assistant text."""
    buf = ""
    for ch in text:
        buf += ch
        placeholder.markdown(buf)
        time.sleep(delay)


def fetch_arxiv_advanced(query: str, max_results: int = 5, category_filter: str | None = None):
    """Advanced ArXiv fetcher with category filter and date sorting."""
    base_url = "http://export.arxiv.org/api/query"
    search_query = f"all:{query}"
    if category_filter:
        search_query += f"+AND+cat:{category_filter}"

    params = {
        "search_query": search_query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    resp = requests.get(base_url, params=params, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip().replace("\n", " ")
        summary = entry.findtext("atom:summary", default="", namespaces=ns).strip()
        published = entry.findtext("atom:published", default="", namespaces=ns)
        url = entry.findtext("atom:id", default="", namespaces=ns)
        authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
        categories = [c.get("term") for c in entry.findall("atom:category", ns)]

        # Clean abstract (collapse whitespace)
        summary_clean = " ".join(summary.split())

        papers.append(
            {
                "title": title,
                "summary": summary_clean,
                "published": published,
                "link": url,
                "authors": authors,
                "categories": categories,
            }
        )

    return papers


def build_txt(summary_entry: dict) -> BytesIO:
    """Create TXT bytes for download."""
    buf = BytesIO()
    title = summary_entry.get("title") or "AI PaperIQ Summary"
    header = f"{title}\n\n"
    meta_lines = []
    meta = summary_entry.get("metadata") or {}
    if meta.get("source_mode"):
        meta_lines.append(f"Source: {meta['source_mode']}")
    if meta.get("topic"):
        meta_lines.append(f"Topic: {meta['topic']}")
    if meta.get("arxiv_url"):
        meta_lines.append(f"URL: {meta['arxiv_url']}")
    if meta.get("published"):
        meta_lines.append(f"Published: {meta['published']}")
    header += "\n".join(meta_lines) + "\n\n"

    body = summary_entry.get("summary_text", "")
    buf.write((header + body).encode("utf-8"))
    buf.seek(0)
    return buf


def build_pdf(summary_entry: dict) -> BytesIO:
    """Create simple PDF for download."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    title = summary_entry.get("title") or "AI PaperIQ Summary"
    text = summary_entry.get("summary_text", "")

    y = height - 60
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, title)
    y -= 30

    meta = summary_entry.get("metadata") or {}
    c.setFont("Helvetica", 9)
    for line in [
        f"Source: {meta.get('source_mode','AI PaperIQ')}",
        f"Topic: {meta.get('topic','')}",
        f"URL: {meta.get('arxiv_url','')}",
        f"Published: {meta.get('published','')}",
    ]:
        if line.strip().endswith(":"):
            continue
        c.drawString(40, y, line)
        y -= 14
    y -= 10

    c.setFont("Helvetica", 10)
    wrap_width = 90
    for para in text.split("\n"):
        for wrapped in textwrap.wrap(para, wrap_width):
            if y < 40:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            c.drawString(40, y, wrapped)
            y -= 14
        y -= 8

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def build_citation(summary_entry: dict) -> tuple[str, str] | tuple[None, None]:
    """Create APA-style and BibTeX citation if ArXiv metadata is available."""
    meta = summary_entry.get("metadata") or {}
    url = meta.get("arxiv_url")
    title = summary_entry.get("title")
    authors = meta.get("authors")
    published = meta.get("published")

    if not (url and title and authors):
        return None, None

    # Simple author formatting
    def format_author(name: str) -> str:
        parts = name.split()
        if not parts:
            return name
        last = parts[-1]
        initials = "".join(p[0].upper() + "." for p in parts[:-1])
        return f"{last}, {initials}"

    author_str = ", ".join(format_author(a) for a in authors)
    year = "n.d."
    if published and len(published) >= 4:
        year = published[:4]

    apa = f"{author_str} ({year}). {title}. arXiv. {url}"

    key_title = "".join(ch for ch in title.split()[0].lower() if ch.isalnum())
    key = f"{key_title}{year}"
    bibtex = f"""@article{{{key},
  title={{ {title} }},
  author={{ {' and '.join(authors)} }},
  year={{ {year} }},
  journal={{arXiv preprint}},
  url={{ {url} }}
}}"""
    return apa, bibtex


# --------------------------------------------------------------------------------
# CHATBOT
# --------------------------------------------------------------------------------
def get_chat_response(message, context):
    msg = message.lower()

    if "recommend" in msg or "tip" in msg:
        if not context.get("has_summary"):
            return "💡 Try **Search topic** mode with a keyword to pull the latest paper from arXiv."
        return "✨ You can inspect similarity, compression and readability in the Analytics panel."

    try:
        system_prompt = f"""
You are the in-app AI assistant for AI PaperIQ, a research summarization and analytics platform.

Current context:
- Mode: {context.get('mode')}
- Has summary: {context.get('has_summary')}

Keep responses short, friendly and helpful.
"""
        full = system_prompt + "\n\nUser: " + message
        return llm_service.generate_chat_response(full)
    except Exception:
        return "⚠️ I had trouble answering that. Please try again."


def render_chat_ui(mode):
    st.markdown('<div class="chat-header-custom">🤖 AI Assistant</div>', unsafe_allow_html=True)
    chat_box = st.container(height=300)

    with chat_box:
        for msg in st.session_state.chat_history:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

    if prompt := st.chat_input("Ask something about the app, summaries, or suggestions..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with chat_box:
            st.chat_message("user", avatar="👤").write(prompt)

        context = {
            "mode": mode,
            "has_summary": bool(st.session_state.session_summaries),
        }
        response = get_chat_response(prompt, context)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with chat_box:
            msg_container = st.chat_message("assistant", avatar="🤖")
            placeholder = msg_container.empty()
            type_writer(placeholder, response)


# --------------------------------------------------------------------------------
# SIDEBAR – NAV + SETTINGS
# --------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-glass'>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>🧠 AI PaperIQ</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sidebar-sub'>Smart research summarization, analytics and AI assistance in one place.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sidebar-nav-item sidebar-nav-active'>📊 Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-nav-item'>📄 Summaries</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-nav-item'>📈 Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-nav-item'>⚙ Settings</div>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### ⚙ User Settings")
    st.session_state.default_mode = st.selectbox(
        "Default Input Mode",
        ["Paste text", "Upload PDF", "Search topic"],
        index=["Paste text", "Upload PDF", "Search topic"].index(st.session_state.default_mode),
    )
    st.session_state.default_model = st.selectbox(
        "Default Model",
        ["auto", "pro", "flash"],
        index=["auto", "pro", "flash"].index(st.session_state.default_model),
    )
    st.session_state.compact_view = st.checkbox("Compact layout", value=st.session_state.compact_view)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# HERO HEADER + PROFILE
# --------------------------------------------------------------------------------
hero_cols = st.columns([4, 1.6])

with hero_cols[0]:
    st.markdown(
        """
        <div class="hero-header">
            <div class="hero-title">AI PaperIQ Dashboard</div>
            <div class="hero-subtitle">
                Upload, summarize and analyze research papers with AI-powered insights and real-time analytics.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_cols[1]:
    if hasattr(st, "popover"):
        with st.popover(f"👤 {st.session_state.user_name}", use_container_width=True):
            st.write(f"**Email:** {st.session_state.user_email}")
            st.write("**Role:** Researcher")
            st.write("Status: ✅ Logged in")
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.switch_page("login.py")
    else:
        st.markdown(
            f"<div class='profile-chip'>👤 {st.session_state.user_name}</div>",
            unsafe_allow_html=True,
        )
    if st.button("🚪 Logout", use_container_width=True):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/login.py")

# --------------------------------------------------------------------------------
# TOP CONFIG BAR
# --------------------------------------------------------------------------------
with st.container():
    st.markdown("<div class='top-config-bar'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([3, 3, 2])

    with c1:
        mode = st.selectbox(
            "Input Mode",
            ["Paste text", "Upload PDF", "Search topic"],
            index=["Paste text", "Upload PDF", "Search topic"].index(st.session_state.default_mode),
            label_visibility="collapsed",
        )

    with c2:
        ai_model = st.selectbox(
            "AI Model",
            ["auto", "pro", "flash"],
            index=["auto", "pro", "flash"].index(st.session_state.default_model),
            label_visibility="collapsed",
        )

    with c3:
        if hasattr(st, "popover"):
            with st.popover("💬 Nova", use_container_width=True):
                render_chat_ui(mode)
        else:
            with st.expander("💬 Nova"):
                render_chat_ui(mode)

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# TOPIC + ADVANCED ARXIV CONTROLS
# --------------------------------------------------------------------------------
topic = ""
category_filter = ""
max_results = 3

if mode == "Search topic":
    topic = st.text_input("🔍 Research Topic", placeholder="e.g., Federated Learning in Healthcare")
    cols = st.columns([2, 2, 1])
    with cols[0]:
        category_filter = st.text_input("Category (optional, e.g., cs.LG)")
    with cols[1]:
        max_results = st.slider("Max papers", 1, 5, 3)
    with cols[2]:
        if st.button("🔎 Fetch from arXiv"):
            if not topic.strip():
                st.error("Please enter a topic to search.")
            else:
                try:
                    st.session_state.arxiv_results = fetch_arxiv_advanced(
                        topic.strip(), max_results=max_results, category_filter=category_filter.strip() or None
                    )
                    if not st.session_state.arxiv_results:
                        st.warning("No papers found for this query.")
                    else:
                        st.session_state.selected_paper_index = 0
                except Exception as e:
                    st.error(f"ArXiv fetch failed: {e}")

    if st.session_state.arxiv_results:
        st.markdown("##### 📚 Matching ArXiv Papers")
        options = [
            f"{i+1}. {p['title'][:70]}..." for i, p in enumerate(st.session_state.arxiv_results)
        ]
        st.session_state.selected_paper_index = st.radio(
            "Select a paper for summarization:",
            options=list(range(len(options))),
            format_func=lambda i: options[i],
            index=st.session_state.selected_paper_index,
            horizontal=False,
        )

        sel = st.session_state.arxiv_results[st.session_state.selected_paper_index]
        with st.expander("View selected abstract & metadata", expanded=False):
            st.write(f"**Title:** {sel['title']}")
            st.write("**Authors:** " + ", ".join(sel["authors"]))
            st.write(f"**Published:** {sel['published']}")
            st.write("**Categories:** " + ", ".join(sel["categories"]))
            st.markdown("**Abstract:**")
            st.write(sel["summary"])

# --------------------------------------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------------------------------------
left_col, right_col = st.columns([3, 2], gap="large")

# ===================== LEFT: Summarization & Conversation =====================
with left_col:
    # ---- Summarization Engine ----
    with st.container(border=True):
        st.markdown("### 💬 AI Summarization Engine")

        user_input = ""

        if mode == "Paste text":
            user_input = st.text_area(
                "📝 Paste your research text",
                height=220 if st.session_state.compact_view else 260,
            )

        elif mode == "Upload PDF":
            uploaded = st.file_uploader("📄 Upload Research Paper (PDF)", type=["pdf"])
            if uploaded:
                with st.spinner("🔄 Extracting text from PDF..."):
                    try:
                        user_input = pdf_extractor.extract_text_from_pdf(uploaded)
                        st.success(f"✅ Extracted {len(user_input)} characters from PDF.")
                    except Exception as e:
                        st.error(f"❌ Failed to extract text: {e}")

        elif mode == "Search topic":
            user_input = st.text_area(
                "📝 Optional custom text / notes (will be appended to abstract)",
                height=150 if st.session_state.compact_view else 180,
            )

        generate = st.button("✨ Generate Summary", use_container_width=True)

        if generate:
            content = ""
            meta = {"source_mode": mode, "topic": topic}

            loader_ph = st.empty()
            loader_ph.markdown(
                """
                <div style="text-align:center; padding:0.7rem 0 0.2rem 0;">
                    <div class="neon-loader"></div>
                    <div class="neon-loader-text">AI is working on your summary...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if mode == "Search topic" and st.session_state.arxiv_results:
                p = st.session_state.arxiv_results[st.session_state.selected_paper_index]
                content = p["summary"]
                if user_input.strip():
                    content += "\n\nUser Notes:\n" + user_input.strip()
                meta.update(
                    {
                        "arxiv_url": p["link"],
                        "published": p["published"],
                        "authors": p["authors"],
                        "categories": p["categories"],
                    }
                )
                title = p["title"]
            elif mode == "Search topic":
                # fallback simple mode if no prefetch
                if not topic.strip():
                    loader_ph.empty()
                    st.error("⚠️ Please enter a topic or fetch a paper from arXiv.")
                else:
                    try:
                        papers = fetch_arxiv_advanced(topic.strip(), max_results=1)
                        if not papers:
                            loader_ph.empty()
                            st.error("No papers found for this topic.")
                        else:
                            p = papers[0]
                            content = p["summary"]
                            if user_input.strip():
                                content += "\n\nUser Notes:\n" + user_input.strip()
                            meta.update(
                                {
                                    "arxiv_url": p["link"],
                                    "published": p["published"],
                                    "authors": p["authors"],
                                    "categories": p["categories"],
                                }
                            )
                            title = p["title"]
                            st.markdown("---")
                            st.markdown(f"**📄 {p['title']}**")
                            st.write("👥 " + ", ".join(p["authors"]))
                            st.markdown("---")
                    except Exception as e:
                        loader_ph.empty()
                        st.error(f"ArXiv search failed: {e}")
            else:
                content = user_input
                title = "Custom Input Summary"

            loader_ph.empty()

            if content and content.strip():
                st.session_state.conversation.append({"role": "user", "text": content[:1000] + "..."})

                with st.spinner("🤖 AI is generating your summary..."):
                    model_choice = (
                        "pro" if ai_model == "pro" else "flash" if ai_model == "flash" else "auto"
                    )
                    summary = llm_service.summarize_text(content, preferred=model_choice)

                st.session_state.conversation.append({"role": "ai", "text": summary})
                # analytics for this summary
                try:
                    analysis = text_analysis.analyze_texts(content, summary)
                except Exception:
                    analysis = None

                # save in history
                entry_id = len(st.session_state.session_summaries)
                summary_entry = {
                    "id": entry_id,
                    "mode": mode,
                    "title": title,
                    "topic": topic,
                    "input_text": content,
                    "summary_text": summary,
                    "created_at": time.time(),
                    "analysis": analysis,
                    "metadata": meta,
                }
                st.session_state.session_summaries.append(summary_entry)
                st.session_state.current_summary_index = entry_id

                st.success("✅ Summary generated & saved to history!")
                st.rerun()
            else:
                st.error("⚠️ No text/content available to summarize.")

    # ---- Conversation History (AI messages) ----
    if st.session_state.conversation:
        with st.container(border=True):
            st.markdown("### 📜 Conversation History")
            for msg in reversed(st.session_state.conversation):
                if msg["role"] == "ai":
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(msg["text"])

# ===================== RIGHT: Analytics, Export, Comparison, History =====================
with right_col:
    with st.container(border=True):
        st.markdown("### 📊 Analytics Dashboard")

        current_entry = None
        if st.session_state.session_summaries:
            if st.session_state.current_summary_index is None:
                st.session_state.current_summary_index = len(st.session_state.session_summaries) - 1
            current_entry = st.session_state.session_summaries[st.session_state.current_summary_index]

            if current_entry.get("analysis"):
                analysis = current_entry["analysis"]

                m1, m2 = st.columns(2)
                m1.metric("📝 Input Words", f"{analysis['input_word_count']:,}")
                m2.metric("📄 Summary Words", f"{analysis['summary_word_count']:,}")

                m3, m4 = st.columns(2)
                m3.metric("🎯 Similarity", f"{analysis['cosine_similarity']*100:.1f}%")
                m4.metric("📉 Compression", f"{analysis['compression_ratio']:.1%}")

                st.markdown("---")
                st.markdown(f"**📚 Readability (Flesch):** {analysis['flesch_summary']:.1f}")

                st.plotly_chart(
                    text_analysis.plot_comparison(analysis), use_container_width=True
                )
            else:
                st.info("Analytics not available for this summary (analysis failed).")
        else:
            st.info("Generate your first summary to unlock analytics.")

    # ---- Export + Citation ----
    if current_entry:
        with st.container(border=True):
            st.markdown("### 📤 Export & Citations")

            c1, c2 = st.columns(2)
            txt_buf = build_txt(current_entry)
            pdf_buf = build_pdf(current_entry)

            with c1:
                st.download_button(
                    "⬇ Download TXT",
                    data=txt_buf,
                    file_name="summary.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with c2:
                st.download_button(
                    "⬇ Download PDF",
                    data=pdf_buf,
                    file_name="summary.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            apa, bibtex = build_citation(current_entry)
            if apa:
                st.markdown("---")
                st.markdown("**🔗 Suggested Citation (APA):**")
                st.markdown(apa)
                st.markdown("**📚 BibTeX:**")
                st.code(bibtex, language="bibtex")
            else:
                st.markdown("---")
                st.info("Citation available only for ArXiv-based summaries.")

    # ---- Multi-paper comparison + History ----
    if st.session_state.session_summaries:
        with st.container(border=True):
            st.markdown("### 📚 Saved Summaries & Comparison")

            entries = st.session_state.session_summaries
            labels = [
                f"{e['id']+1}. { (e['title'] or 'Untitled')[:45] }"
                for e in entries
            ]

            # Select current summary to view
            st.session_state.current_summary_index = st.selectbox(
                "Active summary:",
                options=list(range(len(labels))),
                index=st.session_state.current_summary_index
                if st.session_state.current_summary_index is not None
                else len(labels) - 1,
                format_func=lambda i: labels[i],
            )

            if len(entries) >= 2:
                st.markdown("#### 🔁 Compare two summaries")

                col_a, col_b = st.columns(2)
                with col_a:
                    idx_a = st.selectbox(
                        "Summary A",
                        options=list(range(len(labels))),
                        format_func=lambda i: labels[i],
                        key="cmp_a",
                    )
                with col_b:
                    idx_b = st.selectbox(
                        "Summary B",
                        options=list(range(len(labels))),
                        format_func=lambda i: labels[i],
                        key="cmp_b",
                    )

                if idx_a != idx_b:
                    ea = entries[idx_a]
                    eb = entries[idx_b]
                    if ea.get("analysis") and eb.get("analysis"):
                        a = ea["analysis"]
                        b = eb["analysis"]
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("**Summary A Metrics**")
                            st.write(f"Words: {a['summary_word_count']}")
                            st.write(f"Similarity: {a['cosine_similarity']*100:.1f}%")
                            st.write(f"Compression: {a['compression_ratio']:.1%}")
                        with c2:
                            st.markdown("**Summary B Metrics**")
                            st.write(f"Words: {b['summary_word_count']}")
                            st.write(f"Similarity: {b['cosine_similarity']*100:.1f}%")
                            st.write(f"Compression: {b['compression_ratio']:.1%}")
                    else:
                        st.info("Analytics missing for one of the selected summaries.")
                else:
                    st.info("Select two different summaries to compare.")

            st.markdown("---")
            with st.expander("📜 All saved summaries", expanded=False):
                for e in reversed(entries):
                    st.markdown(f"**{e['id']+1}. {e['title']}**")
                    meta = e.get("metadata") or {}
                    if meta.get("topic"):
                        st.write(f"Topic: {meta['topic']}")
                    if meta.get("arxiv_url"):
                        st.write(f"URL: {meta['arxiv_url']}")
                    st.write(f"Mode: {e['mode']}")
                    st.write(f"Words (summary): {e.get('analysis',{}).get('summary_word_count','-')}")
                    st.markdown("---")

# --------------------------------------------------------------------------------
# FOOTER
# --------------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; padding:1rem; color:#9ca3af; font-size:0.85rem;'>© 2024 AI PaperIQ · Built with Streamlit & Gemini AI</div>",
    unsafe_allow_html=True,
)
