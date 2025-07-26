# AI Model Generator for Blender
A Blender addon that generates 3D models from text prompts using AI.
## What it does
This addon adds a panel to Blender's sidebar that lets you describe a 3D model in plain text, and it will generate the corresponding Blender Python code to create that model using AI APIs like Google Gemini.
## Features
- Generate 3D models from text descriptions
- Works with Google Gemini API or custom endpoints  
- Integrates directly into Blender's UI
- Automatically organizes generated models in collections
## Installation
1. Download the `ai_model_generator.py` file
2. In Blender, go to Edit > Preferences > Add-ons
3. Click "Install..." and select the Python file
4. Enable the addon by checking the box
## Usage
1. Open the 3D viewport sidebar (press N)
2. Go to the "AI Gen" tab
3. Enter your API key (get one from ai.google.dev for Gemini)
4. Type what you want to create (e.g., "a red sports car")
5. Click "Generate Model"
## Output:
- prompt: "create a dining table"
- gemini flash:
  <img width="1920" height="1048" alt="Screenshot from 2025-07-26 12-58-56" src="https://github.com/user-attachments/assets/d6fa678c-8836-4b1f-9dc3-c0eca97cbf45" />
- groq (llama 3.3):
  <img width="1920" height="1048" alt="Screenshot from 2025-07-26 12-59-36" src="https://github.com/user-attachments/assets/e3521611-dc13-4d28-9cc1-80e891abdf24" />
- sonnet:
  <img width="1920" height="1048" alt="Screenshot from 2025-07-26 17-12-50" src="https://github.com/user-attachments/assets/b0f2c4f3-8385-4ad3-839b-5fecdbd0073f" />


## Custom API Setup

### Expected Request Format
Your custom API endpoint should accept POST requests with:
```json
{
  "prompt": "Create a simple cube",
  "format": "blender_python"
}
```

### Expected Response Format
```json
{
  "script": "import bpy\n# Your Blender Python code here\nbpy.ops.mesh.primitive_cube_add()"
}
```

### Authentication
The addon supports Bearer token authentication:
```
Authorization: Bearer YOUR_API_KEY
```

### Popular Local LLM Setups

#### Ollama
```bash
# Install Ollama and run a model
ollama run codellama
# Your endpoint: http://localhost:11434/api/generate
```

#### LM Studio
- Download and run LM Studio
- Load a code-capable model
- Enable API server
- Your endpoint: http://localhost:1234/v1/chat/completions

#### Text Generation WebUI
```bash
# Run with API enabled
python server.py --api --listen
# Your endpoint: http://localhost:5000/api/v1/generate
```

## Requirements
- Blender 3.0+
- Internet connection
- API key from supported provider
## Contribution Guidlines:
- Follow existing code style and structure
- Test your changes in Blender before submitting
- Add comments for complex functionality
All contributions will be reviewed and credited. Thanks for helping make this project better!
---
Created by MrKuros (Kashish Patel)
