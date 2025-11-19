import streamlit as st
from transformers import pipeline

@st.cache_resource
def load_pipeline(task, model_id):
    """
    Loads a Hugging Face pipeline and caches it in memory.
    This prevents reloading the model on every user interaction.
    
    Args:
        task (str): The HF task identifier (e.g., 'summarization').
        model_id (str): The specific model repository name.
    """
    return pipeline(task, model=model_id)

def execute_pipeline(step_config, input_text):
    """
    Executes a specific model step based on the configuration.
    
    Args:
        step_config (dict): Configuration dictionary for the current step.
        input_text (str): The input text (or previous step's output).
        
    Returns:
        str: The processed text output.
    """
    # Load the model (or retrieve from cache)
    pipe = load_pipeline(step_config['task'], step_config['model_id'])
    
    # Logic specific to different tasks
    if step_config['task'] in ['text2text-generation', 'summarization']:
        # For generation tasks, we set a max_length to avoid cutting off too early
        # You can parametrize 'max_length' via UI if needed
        response = pipe(input_text, max_length=512)
        
        if step_config['task'] == 'summarization':
            return response[0]['summary_text']
        return response[0]['generated_text']
        
    elif step_config['task'] == 'translation_en_to_es':
        response = pipe(input_text)
        return response[0]['translation_text']
        
    # Fallback for other text-based models (like sentiment analysis)
    return str(pipe(input_text))