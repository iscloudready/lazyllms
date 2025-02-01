# 🦾 LazyLLMs - Lightweight LLM Model Manager

[![GitHub License](https://img.shields.io/github/license/your-repo/lazyllms)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Contributors](https://img.shields.io/github/contributors/your-repo/lazyllms)](https://github.com/your-repo/lazyllms/graphs/contributors)

---

## 🚀 Overview

**LazyLLMs** is a **TUI-based (Terminal UI) Model Manager**, inspired by **LazyDocker**, for monitoring and managing AI models like **Ollama models**. It provides a **real-time system resource view** and **control over running models** directly from the command line.

### 🔹 Features:
✅ **Monitor Running AI Models**
✅ **Track System Resource Usage (CPU, RAM, GPU, VRAM)**
✅ **Start & Stop Models via CLI**
✅ **TUI-Based Interactive Interface (Rich & Textual)**

---

## 📌 Installation & Setup

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/lazyllms.git
cd lazyllms
```

### **2️⃣ Set Up Virtual Environment**
```bash
python -m venv lazyllms_venv
source lazyllms_venv/bin/activate   # For macOS/Linux
lazyllms_venv\Scripts\activate      # For Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage Guide

### 🔍 **List Running Models**
```bash
python main.py list
```
🔹 This will show **all currently running AI models**.

---

### 📊 **Launch the Terminal UI**
```bash
python main.py tui
```
✔️ **Displays running models in a table**
✔️ **Shows system resource usage (CPU, RAM, GPU, VRAM)**
✔️ **Press `r` to refresh data.**
✔️ **Press `q` to quit the TUI.**

---

## 📌 Screenshots

### **📊 Model & System Usage View**
![LazyLLMs UI](https://raw.githubusercontent.com/iscloudready/lazyllms/refs/heads/main/Images/home.png)

---

## 🏗️ Roadmap - Future Enhancements

🚀 **Auto-refreshing UI** (Real-time updates without manual refresh)
🔥 **Live Log Monitoring** (Display logs of running models)
📦 **Docker & Kubernetes Support** (Monitor AI models inside containers)
⚡ **GPU Load Optimization** (Track GPU-specific metrics)

---

## 🤝 Contributing

We welcome contributions! Follow these steps:

1️⃣ **Fork** the repo
2️⃣ **Create a Feature Branch** (`feature-xyz`)
3️⃣ **Commit Changes** (`git commit -m "Added feature xyz"`)
4️⃣ **Submit a Pull Request** 🚀

---

## 📝 License

This project is **MIT Licensed**. See the [LICENSE](LICENSE) file for details.

---

## 💌 Connect with Us

📧 **Email**: your-email@example.com
🐦 **Twitter**: [@your-handle](https://twitter.com/)
🌟 **LinkedIn**: [Your Profile](https://linkedin.com/in/)

