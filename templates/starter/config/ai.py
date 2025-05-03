from arkalos import env

config = {

    # Default LLM configuration to use (from the pre-defined list below)
    'use': env('AI', 'ollama/qwen2.5-coder'),

    # LLM configurations for specific actions
    'use_actions': {
        'text2sql': env('AI_ACTION_TEXT2SQL', 'ollama/qwen2.5-coder'),
    },

    # Pre-defined LLM configurations
    # Add new quick configurations here
    # key - any name to be used in settings above ('use' and 'use_actions')
    # value - {provider, model, ?api_key, ...}
    # You can create similar configurations for the same provider/model with a different name
    'configurations': {

        'ollama/qwen2.5-coder': {
            'provider': 'ollama',
            'model': 'qwen2.5-coder',
        },

        'deepseek/deepseek-chat': {
            'provider': 'deepseek',
            'model': 'deepseek-chat',
            'api_key': env('DEEPSEEK_API_KEY', '')
        },

        'openai/gpt-4.1': {
            'provider': 'openai',
            'model': 'gpt-4.1',
            'api_key': env('OPENAI_API_KEY', '')
        }
    }
}
