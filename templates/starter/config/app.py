from arkalos import env

config = {
    'name': env('APP_NAME', 'Arkalos App'),
    'env': env('APP_ENV', 'production'),
    'llm': env('LLM', 'qwen2.5-coder'),
    
    'debug': env('APP_DEBUG', False),
}
