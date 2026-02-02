import asyncio
import base64
import json
import os
import time
import urllib.parse
import urllib.request
import uuid
import websocket  # pip install websocket-client
from nicegui import ui, app
import ollama

# ==========================================
# ⚙️ Configuration
# ==========================================
COMFYUI_SERVER_ADDRESS = "127.0.0.1:8188"
WORKFLOW_FILE = "image_netayume_lumina_t2i.json"
PROMPT_NODE_ID = "26:24" 
MODEL_NAME = "gemma3:27b-it-q4_K_M"
CLIENT_ID = str(uuid.uuid4())

# ==========================================
# 🔌 ComfyUI API Client Functions
# ==========================================
def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": CLIENT_ID}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{COMFYUI_SERVER_ADDRESS}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{COMFYUI_SERVER_ADDRESS}/view?{url_values}") as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen(f"http://{COMFYUI_SERVER_ADDRESS}/history/{prompt_id}") as response:
        return json.loads(response.read())

def connect_to_comfyui(workflow_data, positive_prompt):
    """Connects to ComfyUI, generates the image, and returns binary data."""
    ws = websocket.WebSocket()
    ws.connect(f"ws://{COMFYUI_SERVER_ADDRESS}/ws?clientId={CLIENT_ID}")
    
    if PROMPT_NODE_ID in workflow_data:
        if "inputs" in workflow_data[PROMPT_NODE_ID]:
            if "value" in workflow_data[PROMPT_NODE_ID]["inputs"]:
                workflow_data[PROMPT_NODE_ID]["inputs"]["value"] = positive_prompt
            else:
                workflow_data[PROMPT_NODE_ID]["inputs"]["text"] = positive_prompt
    else:
        print(f"Error: Node ID {PROMPT_NODE_ID} not found.")
        return None

    prompt_response = queue_prompt(workflow_data)
    prompt_id = prompt_response['prompt_id']
    
    output_images = []
    
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break 
        else:
            continue

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                output_images.append(image_data)
    
    ws.close()
    return output_images[0] if output_images else None

# ==========================================
# 📂 Workflow Loader
# ==========================================
def get_workflow_data():
    try:
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# ==========================================
# 🖥️ UI & Agent Loop (The Storyboard Pipeline)
# ==========================================
@ui.page('/')
def main_page():
    # --- UI State Variables ---
    is_running = False
    
    # --- Layout ---
    with ui.header().classes('bg-slate-900 text-white'):
        ui.label('🤖 Gemma 3 Storyboard Cockpit').classes('text-xl font-bold')
        ui.label(f'Model: {MODEL_NAME}').classes('text-xs opacity-70')

    with ui.row().classes('w-full items-center gap-4 p-4'):
        user_input = ui.input(label='Theme / Idea', placeholder='e.g., Cyberpunk Detective, Solitary Hacker').classes('w-1/2')
        btn_start = ui.button('START STORY', icon='auto_stories').classes('bg-indigo-600')
        btn_stop = ui.button('ABORT', icon='stop').classes('bg-red-600')
        btn_stop.set_visibility(False)
        status_label = ui.label('Ready').classes('text-lg font-bold text-slate-600')

    # Top Row: Concept (Storyteller & Director)
    with ui.grid(columns=2).classes('w-full gap-4 p-4'):
        # 1. Storyteller
        with ui.card().classes('w-full h-64 border-2 border-slate-200 scroll-y-auto') as card_story:
            ui.label('📖 Storyteller').classes('text-lg font-bold text-indigo-600')
            story_status = ui.markdown('Waiting...').classes('text-sm text-slate-500')
            ui.separator()
            story_display = ui.markdown('').classes('text-sm p-2')

        # 2. Director
        with ui.card().classes('w-full h-64 border-2 border-slate-200 scroll-y-auto') as card_dir:
            ui.label('🎬 Director').classes('text-lg font-bold text-pink-600')
            dir_status = ui.markdown('Waiting...').classes('text-sm text-slate-500')
            ui.separator()
            scene_display = ui.markdown('').classes('text-sm p-2')

    # Bottom Row: Production (Prompter, Developer, Reviewer)
    with ui.grid(columns=3).classes('w-full gap-4 p-4'):
        # 3. Prompter
        with ui.card().classes('w-full h-full border-2 border-slate-200') as card_prompt:
            ui.label('⌨️ Prompter').classes('text-lg font-bold text-blue-600')
            prompt_status = ui.markdown('Waiting...').classes('text-sm text-slate-500')
            ui.separator()
            ui.label('Tags:').classes('text-xs font-bold')
            prompt_display = ui.code('None').classes('w-full text-xs break-all')

        # 4. Developer
        with ui.card().classes('w-full h-full border-2 border-slate-200') as card_dev:
            ui.label('🎨 Developer').classes('text-lg font-bold text-purple-600')
            dev_status = ui.markdown('Waiting...').classes('text-sm text-slate-500')
            ui.separator()
            result_image = ui.image('https://placehold.co/600x400?text=No+Image').classes('w-full rounded-md shadow-sm')

        # 5. Reviewer
        with ui.card().classes('w-full h-full border-2 border-slate-200') as card_rev:
            ui.label('🧐 Reviewer').classes('text-lg font-bold text-red-600')
            rev_status = ui.markdown('Waiting...').classes('text-sm text-slate-500')
            ui.separator()
            feedback_display = ui.markdown('No feedback yet.').classes('text-sm border p-2 rounded bg-slate-50')

    with ui.expansion('System Logs', icon='list', value=True).classes('w-full p-4'):
        log_container = ui.log().classes('w-full h-40 bg-slate-100 p-2 font-mono text-xs')

    # --- Logic ---
    async def run_loop():
        nonlocal is_running
        is_running = True
        btn_start.disable()
        btn_stop.set_visibility(True)
        user_req = user_input.value
        
        # State Data
        current_story = ""
        current_scene_desc = ""
        current_prompt = ""
        feedback = ""
        b64_img = None
        max_retries = 3

        workflow_data = get_workflow_data()
        if not workflow_data:
            ui.notify(f"Error: {WORKFLOW_FILE} not found!", type='negative')
            is_running = False
            btn_start.enable()
            return

        try:
            # =================================================
            # PHASE 1: Concept (Story & Direction) - Run Once
            # =================================================
            status_label.set_text("Status: Dreaming a story...")
            
            # STEP 1: Storyteller
            card_story.classes(remove='border-slate-200', add='border-indigo-500 shadow-lg')
            story_status.set_content('**Writing Story...**')
            
            sys_story = "You are a creative novelist. Write a very short, vivid story (max 100 words) based on the user's theme. Focus on atmosphere and emotion."
            res_story = await asyncio.to_thread(ollama.chat, model=MODEL_NAME, messages=[
                {'role':'system','content':sys_story},
                {'role':'user','content':f"Theme: {user_req}"}
            ])
            current_story = res_story['message']['content']
            story_display.set_content(current_story)
            story_status.set_content('Done.')
            card_story.classes(remove='border-indigo-500 shadow-lg', add='border-slate-200')
            log_container.push("Storyteller: Story created.")
            await asyncio.sleep(1)

            # STEP 2: Director
            if not is_running: raise Exception("Aborted")
            card_dir.classes(remove='border-slate-200', add='border-pink-500 shadow-lg')
            dir_status.set_content('**Directing Scene...**')
            
            sys_dir = "You are a movie director. Read the story and describe the SINGLE most visually striking scene for an illustration. Include Subject, Action, Lighting, and Mood. Do NOT use tags, use natural English sentences."
            res_dir = await asyncio.to_thread(ollama.chat, model=MODEL_NAME, messages=[
                {'role':'system','content':sys_dir},
                {'role':'user','content':f"Story: {current_story}"}
            ])
            current_scene_desc = res_dir['message']['content']
            scene_display.set_content(current_scene_desc)
            dir_status.set_content('Done.')
            card_dir.classes(remove='border-pink-500 shadow-lg', add='border-slate-200')
            log_container.push("Director: Scene set.")
            await asyncio.sleep(1)

            # =================================================
            # PHASE 2: Production (Prompt -> Image -> Review) - Loop
            # =================================================
            
            for i in range(max_retries):
                if not is_running: break
                loop_label = f"Take {i+1}/{max_retries}"
                status_label.set_text(f"Status: Filming ({loop_label})")
                log_container.push(f"=== {loop_label} Started ===")

                # STEP 3: Prompter
                card_prompt.classes(remove='border-slate-200', add='border-blue-500 shadow-lg')
                prompt_status.set_content('**Optimizing Tags...**')
                
                sys_prompt = "You are an expert Stable Diffusion Prompt Engineer. Convert the description into highly detailed, comma-separated English tags/keywords. Include quality boosters (masterpiece, best quality, 8k)."
                
                if i == 0:
                    msg_content = f"Scene Description: {current_scene_desc}"
                else:
                    msg_content = f"Original Scene: {current_scene_desc}\nPrevious Prompt: {current_prompt}\nReviewer Feedback (Fix this): {feedback}"
                
                res_p = await asyncio.to_thread(ollama.chat, model=MODEL_NAME, messages=[
                    {'role':'system','content':sys_prompt},
                    {'role':'user','content':msg_content}
                ])
                current_prompt = res_p['message']['content']
                prompt_display.set_content(current_prompt)
                prompt_status.set_content('Done.')
                card_prompt.classes(remove='border-blue-500 shadow-lg', add='border-slate-200')
                await asyncio.sleep(1)

                # STEP 4: Developer
                if not is_running: break
                card_dev.classes(remove='border-slate-200', add='border-purple-500 shadow-lg')
                dev_status.set_content('**Rendering...**')
                
                img_data = await asyncio.to_thread(connect_to_comfyui, workflow_data, current_prompt)
                
                if img_data:
                    b64_img = base64.b64encode(img_data).decode('utf-8')
                    result_image.set_source(f'data:image/png;base64,{b64_img}')
                    dev_status.set_content('Rendered.')
                else:
                    dev_status.set_content('Failed.')
                    log_container.push("Developer: Image generation failed.")
                    card_dev.classes(remove='border-purple-500 shadow-lg', add='border-slate-200')
                    continue

                card_dev.classes(remove='border-purple-500 shadow-lg', add='border-slate-200')
                await asyncio.sleep(1)

                # STEP 5: Reviewer
                if not is_running: break
                card_rev.classes(remove='border-slate-200', add='border-red-500 shadow-lg')
                rev_status.set_content('**Reviewing...**')
                
                prompt_rev = f"""
                ROLE: You are a strict Art Director.
                TASK: Compare the image with the Director's Scene Description: "{current_scene_desc}".
                INSTRUCTIONS:
                - Check for visual consistency with the description.
                - Check for image quality (distortion, bad anatomy).
                OUTPUT (JSON ONLY): {{ "status": "PASS" or "RETRY", "reason": "Short feedback." }}
                """
                
                res_rev = await asyncio.to_thread(ollama.chat, model=MODEL_NAME, messages=[
                    {'role':'user', 'content':prompt_rev, 'images':[b64_img]}
                ])
                
                content = res_rev['message']['content']
                status = "RETRY"
                feedback = content
                try:
                    clean = content.replace("```json", "").replace("```", "").strip()
                    data = json.loads(clean)
                    status = data.get("status", "RETRY")
                    feedback = data.get("reason", content)
                except:
                    pass

                if status == "PASS":
                    feedback_display.set_content(f"### ✅ PASSED\n\n{feedback}")
                    ui.notify('Perfect Shot!', type='positive')
                    status_label.set_text("Status: PRODUCTION COMPLETE")
                    rev_status.set_content('APPROVED')
                    card_rev.classes(remove='border-red-500 shadow-lg', add='border-slate-200')
                    break 
                else:
                    feedback_display.set_content(f"### ⛔ RETRY\n\n{feedback}")
                    rev_status.set_content('REJECTED')
                    ui.notify(f'Retake {i+1} Requested.', type='warning')
                    card_rev.classes(remove='border-red-500 shadow-lg', add='border-slate-200')
                    await asyncio.sleep(2)

        except Exception as e:
            log_container.push(f"Critical Error: {e}")
            status_label.set_text("Status: ERROR")
        
        is_running = False
        btn_start.enable()
        btn_stop.set_visibility(False)

    def stop_loop():
        nonlocal is_running
        is_running = False
        status_label.set_text("Status: ABORTED")
        log_container.push("Mission Aborted by User.")

    btn_start.on('click', run_loop)
    btn_stop.on('click', stop_loop)

ui.run(title='Gemma Storyboard', reload=False)