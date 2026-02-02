# 🤖 Gemma 3 Storyboard Agent

**Fully Autonomous AI Creative Studio** running locally with Gemma 3 & ComfyUI.

## 📖 Overview
This project demonstrates an **Autonomous Multi-Agent Workflow** designed to automate creative production. Instead of requiring human users to act as "Prompt Engineers," this system simulates a full creative team running locally on your machine.

### Key Innovation: Multimodal Feedback Loop
Unlike standard automation tools that simply fire prompts blindly, this system utilizes a **Multimodal LLM (Vision-Language Model)**.
The **Reviewer Agent** effectively "sees" the generated image using Gemma 3's vision capabilities. This enables a true **closed-loop quality control** process where the AI critiques the actual visual output against the narrative intent, rather than just relying on text probability.

The workflow consists of four specialized agents:
1.  **Storyteller**: Writes a short story based on the theme.
2.  **Director**: Visualizes a specific scene from the story (lighting, composition).
3.  **Prompter**: Converts the director's vision into technical Stable Diffusion tags.
4.  **Reviewer**: Visually inspects the image and rejects it if it fails to meet the director's vision.

## 🛠️ Tech Stack
* **Frontend/UI**: [NiceGUI](https://nicegui.io/) (Real-time dashboard)
* **LLM Backend**: [Ollama](https://ollama.com/) (Model: `gemma3:27b-it` / Vision Capable)
* **Image Generation**: [ComfyUI](https://github.com/comfyanonymous/ComfyUI) (via API & WebSocket)
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

## 🎥 Demo: The "Self-Correction" Loop
Check out this run where the Agent corrects itself!
1. The Reviewer Agent rejects the first image due to lack of detail.
2. The Prompter Agent adjusts the tags based on the feedback.
3. The second attempt is approved.

https://youtu.be/t0uqLjdvDtA

## 🇯🇵 For Japanese Clients (日本語での解説)

このリポジトリは、**「マルチモーダルLLM」と「ComfyUI API」を連携させた自律型AIシステム**のプロトタイプです。

### 技術的なハイライト
* **マルチモーダル・フィードバック (Multimodal Loop)**:
    従来の自動化ツールは「画像を生成して終わり」でした。本システムは、生成された画像をLLM（Gemma 3）が**視覚的に認識**し、意図通りかその場で判断します。「AIが自分の描いた絵を見て、自分で修正する」プロセスを実装しています。
* **ComfyUIのAPI制御**:
    PythonからWebSocket経由で直接画像生成エンジンを制御し、複雑なワークフローを完全自動化しています。

**【お仕事の依頼について】**
「生成AIを使った業務効率化」の中でも、特に**品質チェックまで自動化したい**というニーズにお応えします。
APIコストのかからないローカル環境構築や、特定の画風に特化した自律エージェント開発など、お気軽にご相談ください。

## 👤 Author
* doc4voc