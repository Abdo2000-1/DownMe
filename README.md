# 📥 DownMe - Desktop Video Downloader

DownMe is a streamlined, user-friendly desktop application built to simplify video downloads. This project showcases the synergy between human architectural oversight and **AI-Assisted Engineering**, resulting in a robust, production-ready tool.

## 🚀 Overview
The application allows users to download videos from multiple platforms with a single click. It is designed for Windows users who need a reliable, standalone tool without the hassle of web-based advertisements or complex command-line interfaces.

## 🛠 Tech Stack & Methodology

- **Core Logic:** **Python 3.14** utilizing **yt-dlp** for industry-standard media extraction and **FFmpeg** for high-quality post-processing and merging.
- **Graphical User Interface (GUI):** Built with **CustomTkinter**, featuring a high-DPI scaled, responsive design with smooth animations and transitions.
- **Advanced Architecture:**
    - **Multithreading:** Leverages Python’s `threading` module to ensure a non-blocking UI during heavy download tasks.
    - **State Management:** Implemented a **Download Queue** using `collections.deque` and a JSON-based **History System** for persistent data.
    - **Real-time Monitoring:** Asynchronous UI updates for download speed, ETA, and progress bar animations (including a pulse effect).
- **OS Integration:** Windows Taskbar optimization (AppUserModelID) and automated clipboard interaction for seamless URL pasting.
- **Development Process:** Engineered through **AI-Assisted Development (Claude & Gemini)**, focusing on modularity, error handling (Arabic/English), and rapid prototyping.
- **Distribution:**
    - **Compilation:** Bundled into a standalone executable via **PyInstaller**.
    - **Packaging:** Native Windows Installer created with **Inno Setup** for a professional end-user experience.


    
## 🏗 My Role as an AI-Assisted Engineer
While the core logic was refined through advanced AI models, my role involved the critical **Software Engineering Lifecycle (SDLC)**:
- **System Design:** Orchestrated the modular structure of the app and defined the integration points between the UI and the downloader engine.
- **Debugging & Refinement:** Conducted extensive testing to resolve path issues, dependency conflicts (FFmpeg), and runtime errors.
- **Branding & Assets:** Designed the visual identity, including custom icons and branding elements.
- **Release Engineering:** Handled the compilation process into a `.exe` format, ensuring all dependencies were bundled correctly.
- **Deployment:** Authored the **Inno Setup** script to create a professional installation wizard and managed the distribution via MediaFire.

## ✨ Key Features
- ✅ **One-Click Download:** Just paste the link and hit the button.
- ✅ **Native Windows Integration:** Fully functional desktop app with a dedicated icon and Start Menu entry.
- ✅ **High-Speed Processing:** Optimized for performance and reliability.
- ✅ **No Installation Hassle:** Professional setup wizard for easy deployment.

## 📥 Download & Installation
The latest version is available for download on MediaFire. The package is compressed for safety and speed.

> [!IMPORTANT]
> **[Download DownMe from MediaFire](https://www.mediafire.com/file/uoi5zdw3f0sjygz/DownMe_V4.1.zip/file)**

## 🛡 License & Disclaimer
This project was built for educational purposes and personal use. Please ensure you respect the terms of service of any platform you download content from.

---
*Developed with ❤️ and AI-Assisted Innovation by [Abdo Al Adawy]*





Thank you for using DownMe! This tool allows you to download videos 
and audio from various platforms in high quality.

How to use:
1. Paste the video link in the URL box.
2. Select the desired format (MP4 or MP3).
3. Choose your preferred quality.
4. Click "Download Now" and wait for the magic to happen.

Note: This software uses FFmpeg technology for high-quality processing.
--------------------------------------------------
