# 🚀 ViralForge AI

> **AI-Powered Content Automation Platform** for creators, marketers, startups, agencies, and businesses to generate high-quality content, images, blogs, and social media posts in seconds.

See the [User Manual](USER_MANUAL.md) for the complete create, edit, render, export, scheduling, and admin workflow.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-61DAFB)
![Vite](https://img.shields.io/badge/Vite-Build-646CFF)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-UI-38BDF8)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

---

## 📖 Overview

ViralForge AI is a modern SaaS platform designed to automate content creation using cutting-edge AI models. It enables users to create articles, blogs, marketing copy, social media posts, AI-generated images, and much more—all from a single dashboard.

Whether you're a:

- 🎯 Digital Marketer
- ✍️ Content Creator
- 📢 Social Media Manager
- 🏢 Agency
- 🚀 Startup
- 💼 Business Owner

ViralForge AI helps you create engaging content in seconds while saving hours of manual work.

---

# ✨ Key Features

## 🤖 AI Writing

- AI Article Writer
- Blog Generator
- SEO Article Generator
- Product Description Generator
- Email Writer
- Marketing Copy
- Landing Page Copy
- Ad Copy Generator
- Rewrite & Improve Content
- Summarize Content
- Expand & Shorten Text

---

## 🎨 AI Image Generation

- Text-to-Image
- AI Art
- Social Media Images
- Blog Images
- Product Images
- Thumbnail Generation
- Image Prompt Enhancement

---

## 📱 Social Media Automation

Generate content for:

- Facebook
- Instagram
- LinkedIn
- X (Twitter)
- Threads
- Pinterest
- YouTube
- TikTok

Includes:

- Captions
- Hashtags
- Content Ideas
- Carousel Posts
- Viral Hooks
- CTA Generation

---

## 📝 SEO Tools

- SEO Blog Generator
- Keyword Optimization
- Meta Title Generator
- Meta Description Generator
- Slug Generator
- FAQ Generator
- Outline Generator

---

## 📄 Smart Templates

- Resume
- Cover Letter
- Business Proposal
- Press Release
- Job Description
- Product Launch
- Business Email
- Sales Email
- Cold Email
- Newsletter

---

## 👤 User Management

- JWT Authentication
- Secure Login
- Registration
- Profile Management
- Password Reset
- User Dashboard

---

## 💳 Subscription System

- Free Plan
- Pro Plan
- Premium Plan

Supports:

- Monthly Billing
- Yearly Billing
- Usage Tracking
- Credit System

---

## 📚 History

- AI Content History
- Image History
- Download Generated Content
- Copy to Clipboard
- Favorites

---

## 📊 Dashboard

Monitor:

- Generated Content
- Image Usage
- Remaining Credits
- Subscription Status
- Recent Activities
- Analytics

---

# 🏗️ Architecture

```
                +--------------------+
                |   React + Vite     |
                +---------+----------+
                          |
                     REST APIs
                          |
                +---------v----------+
                |      FastAPI       |
                +---------+----------+
                          |
         +----------------+----------------+
         |                                 |
   AI Providers                     PostgreSQL
         |                                 |
 +-------+--------+                        |
 |                |                        |
OpenAI       Google Gemini           SQLAlchemy ORM
 |
Hugging Face
```

---

# 🛠️ Tech Stack

## Backend

- Python 3.11+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- MySQL
- JWT Authentication
- Pydantic
- Uvicorn

---

## Frontend

- React 19
- Vite
- Tailwind CSS
- React Router
- Axios
- React Hook Form
- Framer Motion

---

## AI Providers

- OpenAI GPT
- Google Gemini
- Hugging Face
- Groq (Fallback)
- Future: Claude
- Future: DeepSeek

---

## DevOps

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- AWS EC2
- Ubuntu Server

---

# 📂 Project Structure

```
viralforge-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   │
│   ├── migrations/
│   ├── tests/
│   ├── requirements.txt
│   └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── store/
│   │   └── utils/
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs/
├── screenshots/
├── docker-compose.yml
├── LICENSE
├── README.md
└── .gitignore
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/viralforge-ai.git

cd viralforge-ai
```

---

## Backend

```bash
cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

uvicorn main:app --reload
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

# 📸 Screenshots

```
screenshots/

dashboard.png

ai-writer.png

blog-generator.png

seo-tool.png

image-generator.png

pricing.png
```

---

# 🔮 Upcoming Features

- AI Video Generation
- AI Voice Generation
- AI Presentation Generator
- AI Chat Assistant
- AI Website Builder
- AI Resume Builder
- Workflow Automation
- Team Collaboration
- Public API
- Browser Extension
- Mobile App
- Content Scheduler

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request

---

# 📜 License

Licensed under the MIT License.

---

# ⭐ Support

If you find this project useful:

⭐ Star the repository

🍴 Fork it

🐞 Report issues

💡 Suggest new features

---

## Made with ❤️ using FastAPI, React, and AI.
