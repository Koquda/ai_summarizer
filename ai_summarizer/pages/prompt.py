import streamlit as st
import json
import os
import logging

logger = logging.getLogger(__name__)

dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(os.path.dirname(dir), "config.json")

def reset_to_default_prompt():
    try:
        logger.info("Resetting prompt to default value")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            default_prompt = config.get('default_system_prompt', '')
            config['system_prompt'] = default_prompt
            
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
        logger.info("Successfully reset prompt to default")
        return True
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {str(e)}")
        return False
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in reset_to_default_prompt: {str(e)}")
        return False

def load_system_prompt():
    try:
        logger.info("Loading system prompt")
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            prompt = config.get('system_prompt', '')
            logger.info("System prompt loaded successfully")
            return prompt
    except FileNotFoundError as e:
        logger.error(f"Config file not found: {str(e)}")
        return ''
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        return ''
    except Exception as e:
        logger.error(f"Unexpected error in load_system_prompt: {str(e)}")
        return ''

def save_system_prompt(prompt):
    try:
        logger.info("Saving system prompt")
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        config['system_prompt'] = prompt
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        logger.info("System prompt saved successfully")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        st.error(f"Error al guardar: formato JSON inválido")
        return False
    except Exception as e:
        logger.error(f"Error saving system prompt: {str(e)}")
        st.error(f"Error al guardar: {str(e)}")
        return False

def prompt_page():
    try:
        st.title("System Prompt Configuration")
        logger.info("Initializing prompt configuration page")

        if "prompt_textarea" not in st.session_state:
            st.session_state.prompt_textarea = load_system_prompt()
            logger.info("Initialized prompt textarea state")

        if st.button("Reset to default prompt"):
            logger.info("Reset button clicked")
            if reset_to_default_prompt():
                st.session_state.prompt_textarea = load_system_prompt()
                logger.info("Prompt reset successful")
                st.rerun()
            else:
                logger.error("Failed to reset prompt")
                st.error("Failed to reset prompt")
        
        new_prompt = st.text_area(
            "Edit System Prompt",
            value=st.session_state.get("prompt_textarea", ""),
            height=300,
            key="prompt_textarea"
        )
        
        if st.button("Save Prompt"):
            logger.info("Save button clicked")
            if save_system_prompt(new_prompt):
                logger.info("Prompt saved successfully")
                st.success("Prompt saved successfully!")
            else:
                logger.error("Failed to save prompt")
                st.error("Failed to save prompt")

    except Exception as e:
        logger.error(f"Unexpected error in prompt_page: {str(e)}")
        st.error("An unexpected error occurred. Please try again.")

if __name__ == "__main__":
    prompt_page()