# 🧧 LazyLLMs - Lightweight LLM Model Manager

[![GitHub License](https://img.shields.io/github/license/your-repo/lazyllms)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Contributors](https://img.shields.io/github/contributors/your-repo/lazyllms)](https://github.com/your-repo/lazyllms/graphs/contributors)

---

## 🚀 Overview

**LazyLLMs** is a **TUI-based (Terminal UI) Model Manager**, inspired by **LazyDocker**, designed for **monitoring, managing, and interacting** with AI models, specifically **Ollama models**. With LazyLLMs, you can **view real-time system resource usage** and **control running AI models** directly from your terminal. It’s a powerful tool for developers and AI enthusiasts who want a lightweight, efficient way to manage their models without the overhead of graphical interfaces.

![LazyLLMs UI](https://raw.githubusercontent.com/iscloudready/lazyllms/refs/heads/main/Images/home.png)

### 🔹 Key Highlights:
- 🔹 **Real-Time Monitoring**: View live stats of running AI models including their performance and system resource usage.
- 🔹 **Resource Management**: Track critical system resources such as **CPU, RAM, GPU, and VRAM** to ensure optimal model performance.
- 🔹 **Model Control**: Start, stop, and manage models via simple CLI commands.
- 🔹 **Interactive Interface**: Navigate through an intuitive TUI powered by **Rich** and **Textual** libraries.

---

## 📌 Features

🖐 **Monitor Running AI Models**: Get an overview of all active models, their configurations, and resource usage.

🖐 **Track System Resource Usage**: Keep tabs on CPU, RAM, GPU, and VRAM in real time.

🖐 **Start & Stop Models via CLI**: Manage the lifecycle of your AI models effortlessly from the terminal.

🖐 **TUI-Based Interactive Interface**: Utilize a clean, responsive UI for managing models with minimal effort.

🖐 **Performance Metrics**: View detailed performance stats including throughput, latency, and memory usage.

🖐 **Live Log Monitoring**: Inspect logs in real-time to debug and monitor model behaviors.

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
🔹 This will show **all currently running AI models** with their details and resource usage.

---

### 📊 **Launch the Terminal UI**
```bash
python main.py tui
```
🔹 **Key Features in TUI:**
- ✔️ **Displays running models in a table with detailed stats**
- ✔️ **Shows system resource usage (CPU, RAM, GPU, VRAM)**
- ✔️ **Press `r` to refresh data.**
- ✔️ **Press `q` to quit the TUI.**
- ✔️ **Press `l` to toggle live logs.**

---

## 📌 Screenshots

### 📊 **Model & System Usage View**
![LazyLLMs UI](https://raw.githubusercontent.com/iscloudready/lazyllms/refs/heads/main/Images/home.png)

This view provides a comprehensive display of:
- 🔹 **Available Models**: Name, parameters, size, type, and status.
- 🔹 **System Resources**: CPU, RAM, GPU, VRAM usage in real time.
- 🔹 **Performance Stats**: Throughput, latency, and memory usage for each model.
- 🔹 **Model Details & Live Logs**: Detailed view of selected model attributes and real-time logs.

---

## 🏗️ Roadmap - Future Enhancements

🚀 **Auto-refreshing UI**: Enable real-time updates without the need for manual refresh.

🔥 **Live Log Monitoring**: Advanced logging features with filtering and search capabilities.

📦 **Docker & Kubernetes Support**: Seamless monitoring of AI models running inside containerized environments.

⚡ **GPU Load Optimization**: Enhanced tracking of GPU-specific metrics and performance tuning.

---

## 🤝 Contributing

We welcome contributions from the community! Follow these simple steps to contribute:

1️⃣ **Fork** the repository.

2️⃣ **Create a Feature Branch**:
```bash
git checkout -b feature-xyz
```

3️⃣ **Commit Your Changes**:
```bash
git commit -m "Added feature xyz"
```

4️⃣ **Push to Your Fork**:
```bash
git push origin feature-xyz
```

5️⃣ **Submit a Pull Request** 🚀

---

## 📝 License

This project is **MIT Licensed**. See the [LICENSE](LICENSE) file for more details.

---

## 📨 Connect with Us

📧 **Email**: email@example.com

---

Thank you for using **LazyLLMs**! 🚀 Feel free to share your feedback and contributions!
