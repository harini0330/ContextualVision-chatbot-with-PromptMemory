# 🧠🖼️ ImagePrompt-MemoryBot

> A multimodal AI chatbot that transforms static image interpretation into **conversational image analysis** — backed by **retrieval-augmented generation (RAG)**, structured **session memory**, and advanced **prompt engineering**.

---

## 📌 Overview

**ImagePrompt-MemoryBot** is an intelligent image analysis chatbot system that enables users to upload an image and have a dynamic, visually-grounded conversation about it. Built using **FastAPI**, **vanilla JavaScript**, and **RAG-enhanced LLM communication**, this system maintains **session-aware memory**, enabling context retention across multiple queries in real time.

Unlike conventional chatbots that forget after a prompt, this system **remembers** — and more importantly, it **grounds** all its answers in the actual visual content of the uploaded image.

---

## 🚀 Features

- 📷 **Image upload with preprocessing**: Quality control, compression, and base64 conversion.
- 💬 **Real-time interactive chatbot UI**: Seamless and responsive frontend built with HTML, CSS, and JavaScript.
- 🧠 **Session memory management**: Hybrid (in-memory + JSON) memory for persistent, structured conversations.
- 🧩 **RAG (Retrieval-Augmented Generation)**: All answers grounded in visual facts from the image.
- 🎯 **Advanced Prompt Engineering**: Carefully constructed prompts to reduce hallucinations and ensure factual accuracy.
- 🛠️ **FastAPI backend**: Modular, high-performance API with async support.
- 📈 **Performance optimized and scalable**: Docker-ready, frontend caching, semantic vector filtering.

---

## 📸 Screenshots

> _Add your screenshots here to visually demonstrate chat interactions and UI._



---

## 🧱 System Architecture

> _Include your architecture diagram here (e.g., FastAPI layers, session memory, LLM interface, frontend UI interactions)._

![Architecture Diagram](screens/architecture-diagram.png)

---

## 🔄 Workflow

> _Add your end-to-end system flow diagram here._

![Workflow](screens/workflow.png)

---

## 🛠️ Technologies Used

| Stack            | Description                              |
|------------------|------------------------------------------|
| **Backend**      | Python, FastAPI, Async API handling      |
| **Frontend**     | JavaScript (Vanilla), HTML5, TailwindCSS |
| **AI Model**     | LLM with Retrieval-Augmented Generation  |
| **Storage**      | Hybrid (RAM + JSON-based session storage)|
| **Deployment**   | Docker-ready, scalable architecture      |

---

## 📂 Project Structure

