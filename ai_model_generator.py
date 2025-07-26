import bpy
import bmesh
import requests
import json
import traceback
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator, Panel, PropertyGroup
from bpy_extras.io_utils import ImportHelper

bl_info = {
    "name": "AI Model Generator",
    "author": "Kashish Patel (Mr_Kuros)",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > AI Gen",
    "description": "Generate 3D models from text prompts using AI",
    "category": "Add Mesh",
}

# Properties
class AIGenProperties(PropertyGroup):
    prompt: StringProperty(
        name="Prompt",
        description="Describe the 3D model you want to generate",
        default="Create a simple cube",
        maxlen=500
    )
    
    api_provider: EnumProperty(
        name="API Provider",
        description="Choose AI API provider",
        items=[
            ('GEMINI', "Google Gemini", "Use Google Gemini API"),
            ('GROQ', "Groq", "Use Groq API with fast inference"),
            ('OPENAI', "OpenAI GPT", "Use OpenAI GPT models"),
            ('ANTHROPIC', "Anthropic Claude", "Use Anthropic Claude models"),
            ('CUSTOM', "Custom Model", "Use custom API endpoint")
        ],
        default='GEMINI'
    )
    
    groq_model: EnumProperty(
        name="Groq Model",
        description="Choose Groq model",
        items=[
            ('llama-3.3-70b-versatile', "Llama 3.3 70B", "Llama 3.3 70B Versatile"),
            ('llama-3.1-70b-versatile', "Llama 3.1 70B", "Llama 3.1 70B Versatile"),
            ('llama-3.1-8b-instant', "Llama 3.1 8B", "Llama 3.1 8B Instant"),
            ('mixtral-8x7b-32768', "Mixtral 8x7B", "Mixtral 8x7B"),
            ('gemma2-9b-it', "Gemma2 9B", "Gemma2 9B IT")
        ],
        default='llama-3.3-70b-versatile'
    )
    
    openai_model: EnumProperty(
        name="OpenAI Model",
        description="Choose OpenAI GPT model",
        items=[
            ('gpt-4o-mini', "GPT-4o Mini", "Cheapest and fastest GPT-4 class model"),
            ('gpt-4.1-mini', "GPT-4.1 Mini", "Latest mini model with improved capabilities"),
            ('gpt-4o', "GPT-4o", "Most capable multimodal model"),
            ('gpt-4-turbo', "GPT-4 Turbo", "Previous generation turbo model"),
            ('gpt-3.5-turbo', "GPT-3.5 Turbo", "Fast and inexpensive model")
        ],
        default='gpt-4.1-mini'
    )
    
    anthropic_model: EnumProperty(
        name="Claude Model",
        description="Choose Anthropic Claude model",
        items=[
            ('claude-sonnet-4-20250514', "Claude Sonnet 4", "Latest and most capable model"),
            ('claude-3-5-sonnet-20241022', "Claude 3.5 Sonnet", "Most capable model for coding"),
            ('claude-3-5-haiku-20241022', "Claude 3.5 Haiku", "Fast and cost-effective"),
            ('claude-3-opus-20240229', "Claude 3 Opus", "Previous flagship model")
        ],
        default='claude-sonnet-4-20250514'
    )
    
    api_url: StringProperty(
        name="API URL",
        description="URL of your custom API endpoint",
        default="http://localhost:8000/generate",
        maxlen=500
    )
    
    api_key: StringProperty(
        name="API Key",
        description="Your API key (Gemini or Groq)",
        default="",
        maxlen=200,
        subtype='PASSWORD'
    )
    
    auto_clear: BoolProperty(
        name="Auto Clear Scene",
        description="Clear existing objects before generating new model",
        default=True
    )

# Operators
class AIGEN_OT_generate(Operator):
    """Generate 3D model from prompt"""
    bl_idname = "aigen.generate"
    bl_label = "Generate Model"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.ai_gen_props
        
        if not props.prompt.strip():
            self.report({'ERROR'}, "Please enter a prompt")
            return {'CANCELLED'}
        
        # Show progress
        self.report({'INFO'}, f"Generating model for: {props.prompt}")
        
        try:
            # Call API
            script_code = self.call_api(props)
            
            if script_code and script_code.strip():
                # Debug: Print the received script to console
                print("=== RECEIVED SCRIPT ===")
                print(script_code)
                print("=== END SCRIPT ===")
                
                # Execute the generated script
                self.execute_script(script_code, props, context)
                self.report({'INFO'}, "Model generated successfully!")
            else:
                self.report({'ERROR'}, "Failed to get valid script from API")
                print("DEBUG: Empty or None script received")
                return {'CANCELLED'}
                
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
            print(f"DEBUG: Exception occurred: {str(e)}")
            traceback.print_exc()
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def call_api(self, props):
        """Call the AI API and return the generated script"""
        try:
            if props.api_provider == 'GEMINI':
                return self.call_gemini_api(props)
            elif props.api_provider == 'GROQ':
                return self.call_groq_api(props)
            elif props.api_provider == 'OPENAI':
                return self.call_openai_api(props)
            elif props.api_provider == 'ANTHROPIC':
                return self.call_anthropic_api(props)
            else:
                return self.call_custom_api(props)
        except Exception as e:
            self.report({'ERROR'}, f"API Error: {str(e)}")
            return None
    
    def call_gemini_api(self, props):
        """Call Google Gemini API"""
        if not props.api_key.strip():
            self.report({'ERROR'}, "Please enter your Gemini API key")
            return None
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Create a detailed prompt for Blender script generation
        system_prompt = """You are a Blender Python script generator. Generate clean, working Python code that uses the Blender API (bpy) to create 3D models.

Rules:
1. Only return Python code, no explanations or markdown
2. Use bpy.ops and bpy.data modules
3. Create objects at origin (0,0,0) unless specified
4. Use proper error handling
5. Clear any existing selections first
6. Select created objects at the end
7. Keep code clean and commented

Example format:
import bpy
import bmesh

# Clear existing selection
bpy.ops.object.select_all(action='DESELECT')

# Your model creation code here
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
"""
        
        user_prompt = f"Generate a Blender Python script to create: {props.prompt}"
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt + "\n\n" + user_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1000
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": props.api_key
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"DEBUG: Gemini API Response Status: {response.status_code}")
        print(f"DEBUG: Gemini API Response: {response.text[:500]}...")  # First 500 chars
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG: Parsed JSON keys: {result.keys()}")
            
            # Extract the generated text from Gemini response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                print(f"DEBUG: Candidate keys: {candidate.keys()}")
                
                if 'content' in candidate and 'parts' in candidate['content']:
                    content = candidate['content']['parts'][0]['text']
                    print(f"DEBUG: Raw content length: {len(content)}")
                    print(f"DEBUG: Raw content preview: {content[:200]}...")
                    
                    # Clean up the response - remove markdown code blocks if present
                    if content.startswith('```python'):
                        content = content.split('```python')[1].split('```')[0]
                    elif content.startswith('```'):
                        content = content.split('```')[1].split('```')[0]
                    
                    cleaned_content = content.strip()
                    print(f"DEBUG: Cleaned content length: {len(cleaned_content)}")
                    print(f"DEBUG: Cleaned content preview: {cleaned_content[:200]}...")
                    
                    return cleaned_content
                else:
                    print("DEBUG: No content/parts in candidate")
                    self.report({'ERROR'}, "Invalid response structure from Gemini")
                    return None
            else:
                print("DEBUG: No candidates in response")
                self.report({'ERROR'}, "No content generated by Gemini")
                return None
        else:
            error_msg = f"Gemini API Error: {response.status_code}"
            print(f"DEBUG: API Error - Status: {response.status_code}")
            print(f"DEBUG: API Error - Response: {response.text}")
            
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                        print(f"DEBUG: Error message: {error_data['error'].get('message', '')}")
                except:
                    pass
            self.report({'ERROR'}, error_msg)
            return None
    
    def call_anthropic_api(self, props):
        """Call Anthropic Claude API"""
        if not props.api_key.strip():
            self.report({'ERROR'}, "Please enter your Anthropic API key")
            return None
        
        url = "https://api.anthropic.com/v1/messages"
        
        # Create a detailed prompt for Blender script generation
        system_prompt = """You are a Blender Python script generator. Generate clean, working Python code that uses the Blender API (bpy) to create 3D models.

Rules:
1. Only return Python code, no explanations or markdown
2. Use bpy.ops and bpy.data modules
3. Create objects at origin (0,0,0) unless specified
4. Use proper error handling
5. Clear any existing selections first
6. Select created objects at the end
7. Keep code clean and commented

Example format:
import bpy
import bmesh

# Clear existing selection
bpy.ops.object.select_all(action='DESELECT')

# Your model creation code here
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
"""
        
        user_prompt = f"Generate a Blender Python script to create: {props.prompt}"
        
        data = {
            "model": props.anthropic_model,
            "max_tokens": 1000,
            "temperature": 0.7,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": props.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"DEBUG: Anthropic API Response Status: {response.status_code}")
        print(f"DEBUG: Anthropic API Response: {response.text[:500]}...")  # First 500 chars
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG: Parsed JSON keys: {result.keys()}")
            
            # Extract the generated text from Anthropic response
            if 'content' in result and len(result['content']) > 0:
                content_block = result['content'][0]
                print(f"DEBUG: Content block keys: {content_block.keys()}")
                
                if 'text' in content_block:
                    content = content_block['text']
                    print(f"DEBUG: Raw content length: {len(content)}")
                    print(f"DEBUG: Raw content preview: {content[:200]}...")
                    
                    # Clean up the response - remove markdown code blocks if present
                    if content.startswith('```python'):
                        content = content.split('```python')[1].split('```')[0]
                    elif content.startswith('```'):
                        content = content.split('```')[1].split('```')[0]
                    
                    cleaned_content = content.strip()
                    print(f"DEBUG: Cleaned content length: {len(cleaned_content)}")
                    print(f"DEBUG: Cleaned content preview: {cleaned_content[:200]}...")
                    
                    return cleaned_content
                else:
                    print("DEBUG: No text in content block")
                    self.report({'ERROR'}, "Invalid response structure from Anthropic")
                    return None
            else:
                print("DEBUG: No content in response")
                self.report({'ERROR'}, "No content generated by Anthropic")
                return None
        else:
            error_msg = f"Anthropic API Error: {response.status_code}"
            print(f"DEBUG: API Error - Status: {response.status_code}")
            print(f"DEBUG: API Error - Response: {response.text}")
            
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_type = error_data['error'].get('type', '')
                        error_message = error_data['error'].get('message', '')
                        
                        # Show more specific error messages
                        if error_type == 'authentication_error':
                            error_msg = "Invalid Anthropic API key. Check your key at console.anthropic.com"
                        elif error_type == 'permission_error':
                            error_msg = "Anthropic API permission denied. Check your account access"
                        else:
                            error_msg += f" - {error_message}"
                        
                        print(f"DEBUG: Error type: {error_type}")
                        print(f"DEBUG: Error message: {error_message}")
                except:
                    pass
            self.report({'ERROR'}, error_msg)
            return None
    
    def call_openai_api(self, props):
        """Call OpenAI GPT API"""
        if not props.api_key.strip():
            self.report({'ERROR'}, "Please enter your OpenAI API key")
            return None
        
        url = "https://api.openai.com/v1/chat/completions"
        
        # Create a detailed prompt for Blender script generation
        system_prompt = """You are a Blender Python script generator. Generate clean, working Python code that uses the Blender API (bpy) to create 3D models.

Rules:
1. Only return Python code, no explanations or markdown
2. Use bpy.ops and bpy.data modules
3. Create objects at origin (0,0,0) unless specified
4. Use proper error handling
5. Clear any existing selections first
6. Select created objects at the end
7. Keep code clean and commented

Example format:
import bpy
import bmesh

# Clear existing selection
bpy.ops.object.select_all(action='DESELECT')

# Your model creation code here
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
"""
        
        user_prompt = f"Generate a Blender Python script to create: {props.prompt}"
        
        data = {
            "model": props.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {props.api_key}"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"DEBUG: OpenAI API Response Status: {response.status_code}")
        print(f"DEBUG: OpenAI API Response: {response.text[:500]}...")  # First 500 chars
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG: Parsed JSON keys: {result.keys()}")
            
            # Extract the generated text from OpenAI response
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                print(f"DEBUG: Choice keys: {choice.keys()}")
                
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    print(f"DEBUG: Raw content length: {len(content)}")
                    print(f"DEBUG: Raw content preview: {content[:200]}...")
                    
                    # Clean up the response - remove markdown code blocks if present
                    if content.startswith('```python'):
                        content = content.split('```python')[1].split('```')[0]
                    elif content.startswith('```'):
                        content = content.split('```')[1].split('```')[0]
                    
                    cleaned_content = content.strip()
                    print(f"DEBUG: Cleaned content length: {len(cleaned_content)}")
                    print(f"DEBUG: Cleaned content preview: {cleaned_content[:200]}...")
                    
                    return cleaned_content
                else:
                    print("DEBUG: No message/content in choice")
                    self.report({'ERROR'}, "Invalid response structure from OpenAI")
                    return None
            else:
                print("DEBUG: No choices in response")
                self.report({'ERROR'}, "No content generated by OpenAI")
                return None
        else:
            error_msg = f"OpenAI API Error: {response.status_code}"
            print(f"DEBUG: API Error - Status: {response.status_code}")
            print(f"DEBUG: API Error - Response: {response.text}")
            
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_type = error_data['error'].get('type', '')
                        error_message = error_data['error'].get('message', '')
                        
                        # Show more specific error messages
                        if error_type == 'insufficient_quota':
                            error_msg = "OpenAI quota exceeded. Please add credits at platform.openai.com/billing"
                        elif error_type == 'invalid_api_key':
                            error_msg = "Invalid OpenAI API key. Check your key at platform.openai.com/api-keys"
                        else:
                            error_msg += f" - {error_message}"
                        
                        print(f"DEBUG: Error type: {error_type}")
                        print(f"DEBUG: Error message: {error_message}")
                except:
                    pass
            self.report({'ERROR'}, error_msg)
            return None
    
    def call_groq_api(self, props):
        """Call Groq API"""
        if not props.api_key.strip():
            self.report({'ERROR'}, "Please enter your Groq API key")
            return None
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Create a detailed prompt for Blender script generation
        system_prompt = """You are a Blender Python script generator. Generate clean, working Python code that uses the Blender API (bpy) to create 3D models.

Rules:
1. Only return Python code, no explanations or markdown
2. Use bpy.ops and bpy.data modules
3. Create objects at origin (0,0,0) unless specified
4. Use proper error handling
5. Clear any existing selections first
6. Select created objects at the end
7. Keep code clean and commented

Example format:
import bpy
import bmesh

# Clear existing selection
bpy.ops.object.select_all(action='DESELECT')

# Your model creation code here
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
"""
        
        user_prompt = f"Generate a Blender Python script to create: {props.prompt}"
        
        data = {
            "model": props.groq_model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {props.api_key}"
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"DEBUG: Groq API Response Status: {response.status_code}")
        print(f"DEBUG: Groq API Response: {response.text[:500]}...")  # First 500 chars
        
        if response.status_code == 200:
            result = response.json()
            print(f"DEBUG: Parsed JSON keys: {result.keys()}")
            
            # Extract the generated text from Groq response
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                print(f"DEBUG: Choice keys: {choice.keys()}")
                
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    print(f"DEBUG: Raw content length: {len(content)}")
                    print(f"DEBUG: Raw content preview: {content[:200]}...")
                    
                    # Clean up the response - remove markdown code blocks if present
                    if content.startswith('```python'):
                        content = content.split('```python')[1].split('```')[0]
                    elif content.startswith('```'):
                        content = content.split('```')[1].split('```')[0]
                    
                    cleaned_content = content.strip()
                    print(f"DEBUG: Cleaned content length: {len(cleaned_content)}")
                    print(f"DEBUG: Cleaned content preview: {cleaned_content[:200]}...")
                    
                    return cleaned_content
                else:
                    print("DEBUG: No message/content in choice")
                    self.report({'ERROR'}, "Invalid response structure from Groq")
                    return None
            else:
                print("DEBUG: No choices in response")
                self.report({'ERROR'}, "No content generated by Groq")
                return None
        else:
            error_msg = f"Groq API Error: {response.status_code}"
            print(f"DEBUG: API Error - Status: {response.status_code}")
            print(f"DEBUG: API Error - Response: {response.text}")
            
            if response.text:
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg += f" - {error_data['error'].get('message', '')}"
                        print(f"DEBUG: Error message: {error_data['error'].get('message', '')}")
                except:
                    pass
            self.report({'ERROR'}, error_msg)
            return None
    
    def call_custom_api(self, props):
        """Call custom API endpoint"""
        try:
            # Prepare request data
            data = {
                "prompt": props.prompt,
                "format": "blender_python"
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add API key if provided
            if props.api_key.strip():
                headers["Authorization"] = f"Bearer {props.api_key}"
            
            # Make API request
            response = requests.post(
                props.api_url,
                json=data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Assuming API returns {"script": "python_code_here"}
                return result.get("script", "")
            else:
                self.report({'ERROR'}, f"API Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.report({'ERROR'}, f"Network Error: {str(e)}")
            return None
        except json.JSONDecodeError:
            self.report({'ERROR'}, "Invalid JSON response from API")
            return None
    
    def execute_script(self, script_code, props, context):
        """Safely execute the generated Blender script"""
        try:
            print(f"DEBUG: Executing script of length: {len(script_code)}")
            
            # Optional: Clear scene first
            if props.auto_clear:
                self.clear_scene()
            
            # Create a new collection for generated objects
            collection_name = f"AI_Generated_{props.prompt[:20]}"
            collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(collection)
            
            # Set up execution environment
            exec_globals = {
                'bpy': bpy,
                'bmesh': bmesh,
                'context': context,
                'collection': collection,
                '__name__': '__main__'
            }
            
            # Execute the script
            print("DEBUG: About to execute script...")
            exec(script_code, exec_globals)
            print("DEBUG: Script executed successfully")
            
            # Update the scene
            context.view_layer.update()
            
        except Exception as e:
            self.report({'ERROR'}, f"Script execution error: {str(e)}")
            print(f"DEBUG: Script execution failed: {str(e)}")
            # Print full traceback to console for debugging
            print("Full traceback:")
            traceback.print_exc()
    
    def clear_scene(self):
        """Clear all mesh objects from the scene"""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

class AIGEN_OT_test_connection(Operator):
    """Test API connection"""
    bl_idname = "aigen.test_connection"
    bl_label = "Test Connection"
    
    def execute(self, context):
        props = context.scene.ai_gen_props
        
        try:
            if props.api_provider == 'GEMINI':
                if not props.api_key.strip():
                    self.report({'ERROR'}, "Please enter your Gemini API key")
                    return {'CANCELLED'}
                
                # Test with a simple prompt
                url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
                data = {
                    "contents": [{"parts": [{"text": "Say hello"}]}]
                }
                headers = {
                    "Content-Type": "application/json",
                    "X-goog-api-key": props.api_key
                }
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.report({'INFO'}, "Gemini API connection successful!")
                else:
                    self.report({'ERROR'}, f"Gemini API error: {response.status_code}")
            
            elif props.api_provider == 'GROQ':
                if not props.api_key.strip():
                    self.report({'ERROR'}, "Please enter your Groq API key")
                    return {'CANCELLED'}
                
                # Test with a simple prompt
                url = "https://api.groq.com/openai/v1/chat/completions"
                data = {
                    "model": props.groq_model,
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {props.api_key}"
                }
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.report({'INFO'}, "Groq API connection successful!")
                else:
                    self.report({'ERROR'}, f"Groq API error: {response.status_code}")
            
            elif props.api_provider == 'OPENAI':
                if not props.api_key.strip():
                    self.report({'ERROR'}, "Please enter your OpenAI API key")
                    return {'CANCELLED'}
                
                # Test with a simple prompt
                url = "https://api.openai.com/v1/chat/completions"
                data = {
                    "model": props.openai_model,
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {props.api_key}"
                }
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.report({'INFO'}, "OpenAI API connection successful!")
                else:
                    self.report({'ERROR'}, f"OpenAI API error: {response.status_code}")
            
            elif props.api_provider == 'ANTHROPIC':
                if not props.api_key.strip():
                    self.report({'ERROR'}, "Please enter your Anthropic API key")
                    return {'CANCELLED'}
                
                # Test with a simple prompt
                url = "https://api.anthropic.com/v1/messages"
                data = {
                    "model": props.anthropic_model,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "Say hello"}]
                }
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": props.api_key,
                    "anthropic-version": "2023-06-01"
                }
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.report({'INFO'}, "Anthropic API connection successful!")
                else:
                    self.report({'ERROR'}, f"Anthropic API error: {response.status_code}")
            
            else:
                response = requests.get(props.api_url, timeout=5)
                if response.status_code == 200:
                    self.report({'INFO'}, "Custom API connection successful!")
                else:
                    self.report({'WARNING'}, f"Custom API returned status: {response.status_code}")
        except Exception as e:
            self.report({'ERROR'}, f"Connection failed: {str(e)}")
        
        return {'FINISHED'}

class AIGEN_OT_save_script(Operator, ImportHelper):
    """Save the last generated script to file"""
    bl_idname = "aigen.save_script"
    bl_label = "Save Last Script"
    filename_ext = ".py"
    
    def execute(self, context):
        # This would save the last generated script
        # For now, just show a message
        self.report({'INFO'}, "Script saving not implemented yet")
        return {'FINISHED'}

# UI Panel
class AIGEN_PT_main_panel(Panel):
    """Main panel for AI Model Generator"""
    bl_label = "AI Model Generator"
    bl_idname = "AIGEN_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AI Gen'
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.ai_gen_props
        
        # Prompt section
        box = layout.box()
        box.label(text="Generation Settings:", icon='SETTINGS')
        
        # Make the prompt text box bigger
        col = box.column()
        col.prop(props, "prompt", text="")
        col.scale_y = 2.0  # Make it taller
        
        box.prop(props, "auto_clear")
        
        # Generate button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("aigen.generate", text="Generate Model", icon='MESH_CUBE')
        
        # API settings
        box = layout.box()
        box.label(text="API Settings:", icon='WORLD')
        box.prop(props, "api_provider", text="Provider")
        
        if props.api_provider == 'GEMINI':
            box.prop(props, "api_key", text="Gemini API Key")
            box.label(text="Get your key at: ai.google.dev", icon='INFO')
        elif props.api_provider == 'GROQ':
            box.prop(props, "groq_model", text="Model")
            box.prop(props, "api_key", text="Groq API Key")
            box.label(text="Get your key at: console.groq.com", icon='INFO')
        elif props.api_provider == 'OPENAI':
            box.prop(props, "openai_model", text="Model")
            box.prop(props, "api_key", text="OpenAI API Key")
            box.label(text="Get your key at: platform.openai.com", icon='INFO')
        elif props.api_provider == 'ANTHROPIC':
            box.prop(props, "anthropic_model", text="Model")
            box.prop(props, "api_key", text="Anthropic API Key")
            box.label(text="Get your key at: console.anthropic.com", icon='INFO')
        else:  # CUSTOM
            box.prop(props, "api_url", text="API URL")
            box.prop(props, "api_key", text="API Key (optional)")
        
        # Utility buttons
        row = box.row()
        row.operator("aigen.test_connection", text="Test", icon='PLUGIN')
        row.operator("aigen.save_script", text="Save Script", icon='FILE_TICK')

# Registration
classes = (
    AIGenProperties,
    AIGEN_OT_generate,
    AIGEN_OT_test_connection,
    AIGEN_OT_save_script,
    AIGEN_PT_main_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.ai_gen_props = bpy.props.PointerProperty(type=AIGenProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.ai_gen_props

if __name__ == "__main__":
    register()
