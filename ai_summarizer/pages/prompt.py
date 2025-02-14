import streamlit as st
import json
import os

def load_system_prompt():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('system_prompt', '')
    except FileNotFoundError:
        return ''

def save_system_prompt(prompt):
    try:
        config = {}
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config['system_prompt'] = prompt
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {str(e)}")
        return False

def prompt_page():
    st.title("System Prompt Configuration")

    # Load current prompt
    current_prompt = load_system_prompt()
    
    # Text area for editing the prompt
    new_prompt = st.text_area("Edit System Prompt", value=current_prompt, height=300)
    
    # Save button
    if st.button("Save Prompt"):
        if save_system_prompt(new_prompt):
            st.success("Prompt saved successfully!")
        else:
            st.error("Failed to save prompt")

if __name__ == "__main__":
    prompt_page()