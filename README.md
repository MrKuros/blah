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
