# 🎓 AI Tuition Centre

> **Empowering learners with an AI-powered personal tutor tailored for School, College, and University levels.**

[![Gradio](https://img.shields.io/badge/UI-Gradio-orange)](https://gradio.app/)
[![Groq](https://img.shields.io/badge/Inference-Groq-red)](https://groq.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Demo-Live-yellow)](https://huggingface.co/spaces/Umer1556/tution.AI)

## 🌟 Overview
**AI Tuition Centre** is a sophisticated learning assistant designed to provide context-aware academic support. By leveraging the **Groq LPU™ Inference Engine**, it delivers near-instant responses to complex queries, whether they are text-based, uploaded documents, or visual problems. 

This project was built to bridge the gap between static AI chats and personalized tutoring by offering specific help modes (like step-by-step solving and study planning) tailored to the student's academic level.

---

## ✨ Features
- **🎯 Multi-level Logic:** Customized response styles for School, College, and University learners.
- **🧠 Specialized Help Modes:** - *Explain:* Conceptual breakdowns.
  - *Step-by-step:* Detailed problem-solving.
  - *Check Work:* Feedback on user-submitted answers.
  - *Study Plan:* Personalized learning paths.
  - *Quiz Mode:* Test your knowledge instantly.
- **📄 Document Intelligence:** Support for `.pdf` and `.txt` for context-based tutoring.
- **🖼️ Visual Learning:** Image support for solving handwritten or textbook questions.
- **📥 Exportable Insights:** Save your learning sessions directly to PDF using ReportLab.

---

## 🛠️ Tech Stack
- **Frontend:** [Gradio](https://gradio.app/)
- **LLM Orchestration:** [Groq API](https://groq.com/) (Llama-3 models)
- **PDF Processing:** PyPDF & ReportLab
- **Environment Management:** python-dotenv

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone [https://github.com/Umer1556/AI-Tuition-Centre.git](https://github.com/Umer1556/AI-Tuition-Centre.git)
cd AI-Tuition-Centre
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=your_api_key_here
```

### 4. Run the Application
```bash
python app.py
```

---

## 🌐 Live Demo
Experience the tutor in action without any setup: 
👉 **[Try it on Hugging Face Spaces](https://huggingface.co/spaces/Umer1556/tution.AI)**

---

## 📸 Screenshots
<p align="center">
  <img src="https://github.com/user-attachments/assets/78bf0108-92e5-4c44-b1e9-6687f00e64e4" width="45%" alt="Home UI">
  <img src="https://github.com/user-attachments/assets/a5093e8c-ea37-40f8-af5c-0a4925167e4e" width="45%" alt="Chat Example">
</p>

---

## 👤 Author
**Umer1556**
- **GitHub:** [@Umer1556](https://github.com/Umer1556)
- **Hugging Face:** [Umer1556](https://huggingface.co/Umer1556)

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
