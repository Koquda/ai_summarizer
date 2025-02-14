import streamlit as st
import json
import os

def reset_to_default_prompt():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Get default prompt
            default_prompt = config.get('default_system_prompt', '')
            # Set system_prompt to default
            config['system_prompt'] = default_prompt
            
        # Save the updated config
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        return True
    except FileNotFoundError:
        return False

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

    # Inicializar el estado si no existe
    if "prompt_textarea" not in st.session_state:
        st.session_state.prompt_textarea = load_system_prompt()

    # Manejar el reset antes de crear los widgets
    if st.button("Reset to default prompt"):
        if reset_to_default_prompt():
            # Actualizar directamente el estado con el nuevo valor
            st.session_state.prompt_textarea = load_system_prompt()
            st.rerun()
        else:
            st.error("Failed to reset prompt")
    
    # Text area for editing the prompt usando el estado
    new_prompt = st.text_area(
        "Edit System Prompt",
        value=st.session_state.prompt_textarea,
        height=300,
        key="prompt_textarea"
    )
    
    # Save button
    if st.button("Save Prompt"):
        if save_system_prompt(new_prompt):
            st.success("Prompt saved successfully!")
        else:
            st.error("Failed to save prompt")

if __name__ == "__main__":
    prompt_page()