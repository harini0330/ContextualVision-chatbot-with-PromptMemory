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

- Home Interface
![image](https://github.com/user-attachments/assets/8506a550-9d77-4a16-a13a-f857a9e1a3c7)

- Chat Interface
![image](https://github.com/user-attachments/assets/7c296bec-72a3-4960-a547-65a408a6d57b)

- Analyis of image
![image](https://github.com/user-attachments/assets/48226e4e-bbda-47f5-bb24-5c4870961ac9)

- Uploaded image View
![image](https://github.com/user-attachments/assets/2db472db-4b22-46e8-b537-610c3af18644)





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

