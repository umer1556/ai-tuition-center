import os
import tempfile
import base64
from datetime import datetime

import gradio as gr
from dotenv import load_dotenv

# ----------------------------
# Dependency Checks
# ----------------------------
try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    A4 = None
    canvas = None

# ----------------------------
# Config
# ----------------------------
load_dotenv()
GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip()

APP_TITLE = "AI Tuition Centre"
TEXT_MODEL_ID = "llama-3.3-70b-versatile"
VISION_MODEL_ID = "llama-3.2-11b-vision-preview"
MAX_DOC_CHARS = 12000

# ----------------------------
# Data
# ----------------------------
SCHOOL_SUBJECTS = {
    "Mathematics": "🔢", "English Language": "📝", "English Literature": "📚",
    "Combined Science": "🔬", "Biology": "🧬", "Chemistry": "⚗️",
    "Physics": "⚛️", "Computer Science": "💻", "Geography": "🌍",
    "History": "📜", "Religious Studies": "🕌", "Business Studies": "💼",
}

COLLEGE_SUBJECTS = {
    "Mathematics (A-Level)": "📐", "Further Mathematics": "∞",
    "Computer Science (A-Level)": "💾", "Physics (A-Level)": "🔭",
    "Chemistry (A-Level)": "🧪", "Biology (A-Level)": "🦠",
    "Economics (A-Level)": "📊", "Business (A-Level)": "📈",
    "Psychology (A-Level)": "🧠", "Sociology (A-Level)": "👥",
}

UNIVERSITY_SUBJECTS_COMMON = {
    "Programming Fundamentals": "👨‍💻", "Object-Oriented Programming": "🎯",
    "Data Structures": "🗂️", "Algorithms": "🔄", "Discrete Mathematics": "🔢",
    "Databases (DBMS / SQL)": "🗄️", "Digital Logic Design": "⚡",
    "Computer Architecture": "🖥️", "Operating Systems": "🖱️",
    "Computer Networks": "🌐", "Software Engineering": "⚙️",
    "Web Development": "🌟", "Mobile App Development": "📱",
    "Cyber Security": "🔒", "Cryptography": "🔐", "AI / Machine Learning": "🤖",
    "Data Science": "📉", "Cloud Computing": "☁️", "DevOps (CI/CD)": "🚀",
    "HCI": "🖐️", "Final Year Project": "🎓",
}

UNIVERSITY_MAJORS = [
    "Computer Science", "Software Engineering", "Data Science", "Cyber Security",
    "Information Systems", "Business Management", "Economics", "Finance",
    "Accounting", "Engineering", "Other",
]

UNIVERSITY_SUBJECTS_BY_MAJOR = {
    "Computer Science": UNIVERSITY_SUBJECTS_COMMON,
    "Software Engineering": UNIVERSITY_SUBJECTS_COMMON,
    "Cyber Security": UNIVERSITY_SUBJECTS_COMMON,
    "Data Science": UNIVERSITY_SUBJECTS_COMMON,
    "Information Systems": UNIVERSITY_SUBJECTS_COMMON,
    "Finance": {
        "Corporate Finance": "💰", "Financial Markets": "📊",
        "Portfolio Theory": "📈", "Valuation": "💵"
    },
    "Economics": {
        "Microeconomics": "📊", "Macroeconomics": "🌍",
        "Econometrics": "📈", "Game Theory": "🎮"
    },
    "Engineering": {
        "Engineering Math": "📐", "Signals & Systems": "📡",
        "Control Systems": "🎛️", "Programming": "💻"
    },
    "Business Management": {
        "Strategy": "🎯", "Operations": "⚙️", "Marketing": "📢",
        "Analytics": "📊", "Accounting": "💰"
    },
    "Accounting": {
        "Financial Accounting": "💵", "Management Accounting": "📊", "Auditing": "🔍"
    },
    "Other": UNIVERSITY_SUBJECTS_COMMON,
}

HELP_MODES = {
    "Explain Concept": "💡", "Solve Step-by-Step": "🔢",
    "Check My Work": "✅", "Create Study Plan": "📅", "Quiz Me": "❓",
}

# ----------------------------
# CSS (keeps browser dark/light behavior)
# ----------------------------
CSS = """
:root { --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.gradio-container { max-width: 100%; padding: 0; }
#app-header {
    background: var(--primary-gradient);
    padding: 24px;
    text-align: center;
    color: white;
}
#app-header h1 { font-size: 2rem; font-weight: 700; margin: 0; color: white; }
#app-header .status { font-size: 0.9rem; opacity: 0.9; }
#left-sidebar {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
    padding: 24px;
}
.dark #left-sidebar {
    background: #0f172a;
    border-right: 1px solid #334155;
}
/* Input row stability */
#input-row {
  align-items: flex-end !important;
  gap: 8px !important;
  padding: 0 6px 6px 6px !important;
}
#input-row > * {
  min-width: 0 !important;
}
/* Text area */
#msg-box textarea {
  border-radius: 14px !important;
  min-height: 48px !important;
  max-height: 180px !important;
  padding: 12px 14px !important;
}
/* Send button */
#send-btn {
  background: var(--primary-gradient) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  width: 56px !important;
  min-width: 56px !important;
  height: 48px !important;
  padding: 0 !important;
  font-size: 20px !important;
  line-height: 1 !important;
}
"""

# ----------------------------
# Helpers
# ----------------------------
def _s(x):
    return (x or "").strip()

def status_text():
    if Groq is None:
        return "⚠️ Groq SDK missing"
    if not GROQ_API_KEY:
        return "⚠️ API Key missing"
    return "✨ Ready to help you learn!"

def _get_client():
    if not GROQ_API_KEY or Groq is None:
        return None
    try:
        return Groq(api_key=GROQ_API_KEY)
    except Exception:
        return None

def normalize_history(history):
    """
    Ensures history is always:
    [{"role":"user|assistant","content":"..."}]
    Converts old tuple format if present.
    """
    out = []
    for item in (history or []):
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and content is not None:
                out.append({"role": role, "content": str(content)})
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            u, b = item
            if u:
                out.append({"role": "user", "content": str(u)})
            if b:
                out.append({"role": "assistant", "content": str(b)})
    return out

def extract_text(file_obj):
    try:
        path = file_obj.name if hasattr(file_obj, "name") else file_obj
        if not path or not os.path.exists(path):
            return ""
        ext = os.path.splitext(path)[1].lower()

        if ext == ".pdf" and PdfReader:
            reader = PdfReader(path)
            return "\n".join([(p.extract_text() or "") for p in reader.pages[:10]])[:MAX_DOC_CHARS]

        with open(path, "r", errors="ignore") as f:
            return f.read()[:MAX_DOC_CHARS]
    except Exception:
        return "[Error reading file]"

def encode_image(path):
    try:
        if not path or not os.path.exists(path):
            return ""
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

def subjects_for(lvl, maj):
    lvl = _s(lvl)
    if lvl == "School":
        return SCHOOL_SUBJECTS
    if lvl == "College":
        return COLLEGE_SUBJECTS
    return UNIVERSITY_SUBJECTS_BY_MAJOR.get(_s(maj) or "Other", UNIVERSITY_SUBJECTS_COMMON)

def format_subject_choices(d):
    return [f"{v} {k}" for k, v in d.items()]

def extract_subject_name(s):
    return s.split(" ", 1)[1] if s and " " in s else s

def _wrap_text(text, width):
    lines = []
    for para in (text or "").split("\n"):
        while len(para) > width:
            cut = para.rfind(" ", 0, width)
            if cut == -1:
                cut = width
            lines.append(para[:cut])
            para = para[cut:].strip()
        lines.append(para)
    return lines

# ----------------------------
# PDF Export
# ----------------------------
def export_pdf(history):
    history = normalize_history(history)
    if not history or not canvas:
        return None

    path = os.path.join(tempfile.gettempdir(), f"tuition_{datetime.now().strftime('%H%M%S')}.pdf")
    c = canvas.Canvas(path, pagesize=A4)
    y = 800

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "AI Tuition Chat Export")
    y -= 40

    for item in history:
        role = item.get("role", "")
        content = item.get("content", "")
        if role not in ("user", "assistant"):
            continue

        speaker = "You" if role == "user" else "Tutor"

        if y < 90:
            c.showPage()
            y = 800

        c.setFont("Helvetica-Bold", 10)
        c.drawString(40, y, f"{speaker}:")
        y -= 15

        c.setFont("Helvetica", 10)
        for line in _wrap_text(str(content), 90):
            c.drawString(50, y, line)
            y -= 12
            if y < 90:
                c.showPage()
                y = 800
                c.setFont("Helvetica", 10)
        y -= 12

    c.save()
    return path

# ----------------------------
# Core Logic (voice removed)
# ----------------------------
def generate_response(level, subject, major, major_oth, mode, msg, doc, img, history):
    history = normalize_history(history)
    client = _get_client()

    subj_name = extract_subject_name(_s(subject))
    if not subj_name:
        history.append({"role": "assistant", "content": "Please select a Subject first! 📚"})
        return history, history, "", None, None

    user_text = _s(msg)
    doc_text = extract_text(doc) if doc else ""
    img_b64 = encode_image(img) if img else ""

    if not user_text and not doc_text and not img_b64:
        return history, history, "", None, None

    display_msg = user_text if user_text else "[File/Image Attached]"

    if not client:
        history.append({"role": "user", "content": display_msg})
        history.append({"role": "assistant", "content": "⚠️ API Key missing."})
        return history, history, "", None, None

    # Build model messages
    sys_prompt = "You are a friendly AI tutor. Use emojis. Be clear and helpful."
    api_messages = [{"role": "system", "content": sys_prompt}]

    for m in history:
        role = m.get("role")
        content = m.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            api_messages.append({"role": role, "content": content})

    ctx = f"Level: {level}, Subject: {subj_name}, Mode: {mode}\n"
    if _s(major) and level == "University":
        ctx += f"Major: {major}\n"
    if _s(major_oth):
        ctx += f"Other major detail: {major_oth}\n"
    if doc_text:
        ctx += f"\nDocument Content:\n{doc_text}\n"

    full_msg = f"{ctx}\nStudent:\n{display_msg}"

    if img_b64:
        api_messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": full_msg},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
            ]
        })
    else:
        api_messages.append({"role": "user", "content": full_msg})

    try:
        resp = client.chat.completions.create(
            model=VISION_MODEL_ID if img_b64 else TEXT_MODEL_ID,
            messages=api_messages,
            temperature=0.7,
            max_tokens=1500
        )
        answer = (resp.choices[0].message.content or "").strip() or "I couldn't generate a reply this time."
    except Exception as e:
        answer = f"Error: {str(e)}"

    history.append({"role": "user", "content": display_msg})
    history.append({"role": "assistant", "content": answer})

    return history, history, "", None, None

def update_subs(lvl, maj):
    opts = format_subject_choices(subjects_for(lvl, maj))
    return gr.update(choices=opts, value=opts[0] if opts else ""), gr.update(visible=(lvl == "University"))

# ----------------------------
# UI
# ----------------------------
with gr.Blocks(title=APP_TITLE, theme=gr.themes.Soft(), css=CSS) as demo:
    chat_history = gr.State([])

    gr.HTML(f'<div id="app-header"><h1>🎓 {APP_TITLE}</h1><div class="status">{status_text()}</div></div>')

    with gr.Row():
        # Sidebar
        with gr.Column(scale=1, elem_id="left-sidebar"):
            level = gr.Radio(["School", "College", "University"], value="School", label="Education Level")
            subject = gr.Dropdown(
                format_subject_choices(SCHOOL_SUBJECTS),
                label="Subject",
                value=format_subject_choices(SCHOOL_SUBJECTS)[0]
            )

            with gr.Group(visible=False) as maj_grp:
                major = gr.Dropdown(UNIVERSITY_MAJORS, value="Computer Science", label="Major")
                major_oth = gr.Textbox(label="Other Major", visible=False)

            mode = gr.Dropdown(list(HELP_MODES.keys()), value="Explain Concept", label="Help Mode")

            gr.HTML("<br>")
            export_btn = gr.Button("Download PDF", elem_id="export-btn")
            dl_file = gr.File(visible=False)

        # Chat area
        with gr.Column(scale=3, elem_id="chat-container"):
            chatbot = gr.Chatbot(label="", show_label=False, height=550)

            with gr.Group():
                with gr.Row(elem_id="input-row", equal_height=True):
                    msg = gr.Textbox(
                        show_label=False,
                        placeholder="Type your message...",
                        lines=1,
                        max_lines=8,
                        scale=12,
                        elem_id="msg-box"
                    )

                    send_btn = gr.Button("➤", scale=0, min_width=56, elem_id="send-btn")

                with gr.Accordion("📎 Attach File", open=False):
                    with gr.Row():
                        doc = gr.File(label="PDF/TXT", file_types=[".pdf", ".txt"])
                        img = gr.Image(label="Image", type="filepath")

    # Events
    level.change(update_subs, [level, major], [subject, maj_grp])
    major.change(update_subs, [level, major], [subject, maj_grp])

    inputs = [level, subject, major, major_oth, mode, msg, doc, img, chat_history]
    outputs = [chatbot, chat_history, msg, doc, img]

    msg.submit(generate_response, inputs, outputs)
    send_btn.click(generate_response, inputs, outputs)

    export_btn.click(export_pdf, [chat_history], [dl_file])
    export_btn.click(lambda: gr.update(visible=True), None, [dl_file])

if __name__ == "__main__":
    demo.launch()
