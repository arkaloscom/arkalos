from arkalos import router
from arkalos.ai import DWHAgent

@router.get("/")
async def index():
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat Interface</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Add Prism.js CSS for syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <link rel="stylesheet" href="/assets/css/app.css">
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" class="header-logo">
            <div class="header-title">Arkalos AI</div>
        </div>
         
        <div class="messages-container" id="messages">
            <div class="message-row">
                <div class="bot-avatar">
                    <img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" class="avatar-logo">
                </div>
                <div class="message bot"><p>{DWHAgent.GREETING}</p></div>
            </div>
        </div>
         
        <div class="message-input-container">
            <div class="message-input-wrapper">
                <textarea id="message-input" placeholder="Message Arkalos AI..." rows="3"></textarea>
                <div class="input-controls">
                    <button class="send-button" id="send-button">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
    <!-- Add Prism.js for syntax highlighting -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/showdown/2.1.0/showdown.min.js"></script>
    <script src="/assets/js/app.js"></script>
</body>
</html>
    """
