import urllib.parse

def get_css():
    """
    Returns premium light-theme CSS styling for the Streamlit app.
    Injects custom typography, gradients, white cards, step badges, custom pill tags,
    and rounded container themes matching the reference UI.
    Also hides Streamlit's sidebar elements to enforce a single-page experience.
    """
    return """
    <style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Variables and Theme overrides (Light Theme) */
    :root {
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --bg-color: #faf7f0;
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --accent-color: #e25c38;
        --accent-bg: #fee2e2;
    }

    /* Base Layout Adjustments */
    .stApp {
        font-family: 'Plus Jakarta Sans', 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-color);
        color: var(--text-primary);
    }
    
    /* Compact layout adjustments to eliminate vertical scroll */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.02) !important;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        padding: 1.25rem 1.25rem !important;
    }
    
    p {
        margin-bottom: 0.4rem !important;
        margin-top: 0px !important;
    }
    
    /* Hide Streamlit Header bar, Sidebar elements & arrow button to guarantee single-page layout */
    header[data-testid="stHeader"],
    [data-testid="collapsedSidebarNoTab-left"],
    [data-testid="stSidebarCollapse"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Force radio button options in quiz section to be highly visible (dark text) */
    div[data-testid="stRadio"] label,
    div[data-testid="stRadio"] p,
    div[data-testid="stRadio"] span,
    div[data-testid="stRadio"] div {
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    
    /* Document Cards */
    .doc-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    /* Custom Streamlit container (card) overrides */
    div[data-testid="stExpander"] {
        border-radius: 12px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--card-bg) !important;
    }
    
    /* Clean Pills styling */
    .badge-item {
        border: 1px solid var(--border-color);
        background: #ffffff;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        display: inline-block;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }

    /* Step Badge & Header styling matching the reference UI */
    .step-header {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        gap: 6px;
        margin-bottom: 0.75rem;
    }

    .step-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border: 1.5px solid #fca5a5;
        border-radius: 50%;
        color: #e25c38;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'Outfit', sans-serif;
        background-color: #ffffff;
        line-height: 1;
    }

    .step-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        font-family: 'Outfit', sans-serif;
    }

    /* Premium Flashcard container - Light Theme */
    .flashcard {
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: 20px;
        padding: 2.5rem;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.04);
        position: relative;
        overflow: hidden;
        margin: 1.5rem 0;
    }

    .flashcard::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #e25c38 0%, #f43f5e 100%);
    }

    .flashcard-role {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: var(--accent-color);
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    .flashcard-content {
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1.5;
        margin-bottom: 1rem;
        font-family: 'Outfit', sans-serif;
    }

    /* Modernized button styling (Minimalist styled matching the reference) */
    div.stButton > button {
        border-radius: 8px !important;
        font-size: 0.92rem !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        border: 1px solid var(--border-color) !important;
        background-color: #ffffff !important;
        color: #475569 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    }
    
    div.stButton > button:hover {
        background-color: var(--accent-bg) !important;
        color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        transform: translateY(0) !important;
        box-shadow: none !important;
    }
    
    /* Modernize Streamlit's File Uploader to match reference UI */
    div[data-testid="stFileUploader"] {
        border: 1.5px dashed #fca5a5 !important;
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 0.5rem !important;
        transition: all 0.25s ease !important;
    }

    div[data-testid="stFileUploader"]:hover {
        border-color: var(--accent-color) !important;
        background-color: #fffaf9 !important;
    }

    /* Remove the default border and background from the inner dropzone */
    [data-testid="stFileUploaderDropzone"] {
        border: none !important;
        background-color: transparent !important;
        padding: 1rem 0.5rem !important;
    }

    /* Style the file uploader browse files button and add button */
    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploader"] button {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        color: #475569 !important;
        font-weight: 500 !important;
        padding: 0.35rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover,
    [data-testid="stFileUploader"] button:hover {
        color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
        background-color: var(--accent-bg) !important;
    }

    /* Enforce clean layout for uploaded file list inside uploader */
    div[data-testid="stFileUploader"] ul {
        list-style-type: none !important;
        padding: 0.25rem !important;
        margin: 0.5rem 0 0 0 !important;
    }

    /* Style file uploader icon (svg) to match theme colors */
    [data-testid="stFileUploaderDropzone"] svg {
        fill: var(--accent-color) !important;
        color: var(--accent-color) !important;
    }

    /* ========================================== */
    /* CUSTOM DARK THEME UPLOADER REDESIGN STYLES */
    /* ========================================== */

    /* Dark container styling for upload box */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-upload-marker) {
        background-color: #111827 !important; /* Tailwind gray-900 / dark slate */
        border: 1px solid #1f2937 !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
    }

    /* Hide default file uploader borders and drag-drop texts */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-upload-marker) div[data-testid="stFileUploader"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-upload-marker) [data-testid="stFileUploaderDropzone"] {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important; /* Align to left */
        gap: 8px !important;
        visibility: hidden !important; /* Hides default texts */
        height: auto !important;
    }

    /* Custom File Card Styling */
    .custom-file-card {
        display: flex !important;
        align-items: center !important;
        background-color: #1f2937 !important; /* Slightly lighter dark grey */
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        gap: 12px !important;
        margin-bottom: 8px !important;
    }

    .file-icon-wrapper {
        background-color: #ffffff !important;
        border-radius: 6px !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #111827 !important;
    }

    .file-icon-wrapper span {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.25rem !important;
    }

    .file-details {
        display: flex !important;
        flex-direction: column !important;
        flex-grow: 1 !important;
        overflow: hidden !important;
    }

    .file-name {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .file-size {
        color: #9ca3af !important;
        font-size: 0.75rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Style for the caption in empty state */
    .upload-caption {
        color: #9ca3af !important;
        font-size: 0.8rem !important;
        margin-top: 4px !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Delete button styling inside the file list */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-upload-marker) div.stButton > button {
        background: transparent !important;
        border: none !important;
        color: #9ca3af !important;
        font-size: 1.25rem !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.custom-upload-marker) div.stButton > button:hover {
        color: #ef4444 !important; /* Red color on hover */
        background: transparent !important;
        transform: scale(1.15) !important;
        border-color: transparent !important;
    }

    /* Empty state upload button styling: [📤 Upload] */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.empty-state) [data-testid="stFileUploaderDropzone"] button {
        visibility: visible !important;
        background-color: #1f2937 !important; /* dark grey button */
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.25rem !important;
        cursor: pointer !important;
        font-size: 0 !important; /* Hide original text "Browse files" */
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.empty-state) [data-testid="stFileUploaderDropzone"] button::before {
        content: "📤  Upload" !important;
        font-size: 0.9rem !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.empty-state) [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }

    /* Has files state upload button styling: [ + ] */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.has-files-state) [data-testid="stFileUploaderDropzone"] button {
        visibility: visible !important;
        background-color: #1f2937 !important; /* dark grey button */
        border: 1px solid #374151 !important;
        border-radius: 6px !important;
        color: #ffffff !important;
        font-weight: 500 !important;
        width: 32px !important;
        height: 32px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        font-size: 0 !important; /* Hide original text */
        margin-top: 8px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.has-files-state) [data-testid="stFileUploaderDropzone"] button::before {
        content: "+" !important;
        font-size: 1.4rem !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.has-files-state) [data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #374151 !important;
        border-color: #4b5563 !important;
    }

    /* Custom solid green banner for PDF Ready! */
    .pdf-ready-banner {
        background-color: #166534 !important; /* Solid green background (green-800) */
        color: #ffffff !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        text-align: center !important;
        margin-top: 0.5rem !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        box-shadow: 0 2px 8px rgba(22, 101, 52, 0.2) !important;
    }
    
    /* Quiz card layout */
    .quiz-card {
        background: #ffffff;
        border: 1px solid var(--border-color);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 1.5rem;
    }
    
    .quiz-question {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    </style>
    """

def get_voice_input_html():
    """
    Returns custom HTML/JS code for client-side Voice Input using Web Speech API.
    Communicates the transcription back to the parent window Streamlit chat input.
    """
    return """
    <div class="voice-input-container">
        <button id="mic-btn" class="mic-button" onclick="toggleRecognition()">
            <svg viewBox="0 0 24 24" class="mic-icon">
                <path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"/>
            </svg>
        </button>
        <span id="mic-status" class="mic-status">Voice Dictate</span>
    </div>

    <style>
    .voice-input-container {
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 6px 12px;
        border-radius: 30px;
        width: fit-content;
        margin-top: 5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .mic-button {
        background: #e25c38;
        border: none;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        padding: 0;
        outline: none;
    }
    .mic-button:hover {
        background: #d44a27;
        transform: scale(1.05);
    }
    .mic-icon {
        width: 18px;
        height: 18px;
        fill: currentColor;
    }
    .mic-status {
        color: #64748b;
        font-size: 0.85rem;
        font-weight: 500;
        user-select: none;
    }
    
    /* Recording active animation */
    .recording {
        background: #ef4444 !important;
        animation: pulse 1.5s infinite;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.6);
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }
    </style>

    <script>
    let recognition;
    let isRecording = false;

    function toggleRecognition() {
        if (isRecording) {
            recognition.stop();
            return;
        }

        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!window.SpeechRecognition) {
            alert("Speech recognition is not supported in this browser. Please try Chrome, Edge, or Safari.");
            return;
        }

        recognition = new window.SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isRecording = true;
            document.getElementById('mic-btn').classList.add('recording');
            document.getElementById('mic-status').innerText = 'Listening...';
        };

        recognition.onend = function() {
            isRecording = false;
            document.getElementById('mic-btn').classList.remove('recording');
            document.getElementById('mic-status').innerText = 'Voice Dictate';
        };

        recognition.onerror = function(event) {
            console.error("Speech recognition error", event.error);
            isRecording = false;
            document.getElementById('mic-btn').classList.remove('recording');
            document.getElementById('mic-status').innerText = 'Error: ' + event.error;
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('mic-status').innerText = 'Transcribing...';
            
            try {
                const parentDoc = window.parent.document;
                const chatInput = Array.from(parentDoc.querySelectorAll('textarea')).find(el => 
                    el.placeholder && (el.placeholder.includes('Ask') || el.placeholder.includes('Query') || el.placeholder.includes('message'))
                );
                
                if (chatInput) {
                    chatInput.value = transcript;
                    chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    setTimeout(() => {
                        const sendBtn = chatInput.parentElement.querySelector('button');
                        if (sendBtn) {
                            sendBtn.click();
                        }
                    }, 200);
                } else {
                    copyToClipboard(transcript);
                }
            } catch (e) {
                console.error("Access to parent document blocked or failed:", e);
                copyToClipboard(transcript);
            }
        };

        recognition.start();
    }

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(function() {
            document.getElementById('mic-status').innerText = 'Copied to clipboard!';
            setTimeout(() => {
                document.getElementById('mic-status').innerText = 'Voice Dictate';
            }, 3000);
        }, function(err) {
            alert('Speech transcribed: ' + text);
        });
    }
    </script>
    """

def get_voice_output_html(text):
    """
    Returns an HTML/JS widget for text-to-speech using standard browser speechSynthesis.
    The text is URL-encoded to avoid JS escape character crashes.
    """
    encoded_text = urllib.parse.quote(text)
    template = r"""
    <button class="speaker-btn" onclick="speakText()">
        <svg viewBox="0 0 24 24" class="speaker-icon">
            <path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.85 14,18.71V20.77C18.07,19.86 21,16.28 21,12C21,7.72 18.07,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.77 16.5,12M3,9V15H7L12,20V4L7,9H3Z"/>
        </svg>
        <span>Read Aloud</span>
    </button>

    <style>
    .speaker-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #475569;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-top: 6px;
        outline: none;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .speaker-btn:hover {
        background: #fee2e2;
        border-color: #fca5a5;
        color: #e25c38;
    }
    .speaker-icon {
        width: 14px;
        height: 14px;
        fill: currentColor;
    }
    </style>

    <script>
    function speakText() {
        try {
            window.speechSynthesis.cancel();
            
            // Decode prompt text
            const textToSpeak = decodeURIComponent("__ENCODED_TEXT__");
            
            // Clean markdown tags
            const cleanedText = textToSpeak
                .replace(/[#*_\-+>=[\](){}\~]/g, '')
                .replace(/\s+/g, ' ')
                .trim();
                
            const utterance = new SpeechSynthesisUtterance(cleanedText);
            utterance.lang = 'en-US';
            
            // Adjust rate & pitch for study assistant tone
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            
            window.speechSynthesis.speak(utterance);
        } catch (e) {
            console.error("Text to speech failed", e);
        }
    }
    </script>
    """
    return template.replace("__ENCODED_TEXT__", encoded_text)
