# 🤖 Gemma 3 Storyboard Agent

**Fully Autonomous AI Creative Studio** running locally with Gemma 3 & ComfyUI.

## 📖 Overview
This is a prototype of an **Agentic Workflow** system where AI agents collaborate to create storytelling illustrations from a single user prompt.
Instead of just generating an image, the system acts as a creative studio:

1.  **Storyteller**: Writes a short story based on the theme.
2.  **Director**: Visualizes a specific scene from the story (lighting, composition).
3.  **Prompter**: Converts the director's vision into technical Stable Diffusion tags.
4.  **Reviewer**: Critiques the generated image and requests retakes if necessary.

## 🛠️ Tech Stack
* **Frontend/UI**: [NiceGUI](https://nicegui.io/)
* **LLM Backend**: [Ollama](https://ollama.com/) (Model: `gemma3:27b-it`)
* **Image Generation**: [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
* **Language**: Python 3.10+

## 🚀 How to Run

1.  **Prerequisites**
    * Install Ollama and pull the model: `ollama pull gemma3:27b-it`
    * Install ComfyUI and ensure it's listening on `127.0.0.1:8188`.

2.  **Installation**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/repo-name.git](https://github.com/YOUR_USERNAME/repo-name.git)
    cd repo-name
    pip install -r requirements.txt
    ```

3.  **Usage**
    ```bash
    python dashboard.py
    ```
    Access `http://localhost:8080` in your browser.

## 🎥 Demo
(Add your demo GIF or video link here)

## 👤 Author
* [Your Name]