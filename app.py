import streamlit as st
import boto3
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enhanced page configuration
st.set_page_config(
    page_title="Scholarship Assistant Bot", 
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .progress-container {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        height: 8px;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    .question-counter {
        text-align: center;
        font-weight: bold;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        color: #000000;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        color: #000000;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%); /* blue gradient */
        border-left: 4px solid #2196f3; /* blue border */
        color: #111;
    }
    
    .info-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
        color: #000000;
    }
    
    .warning-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        color: #000000;
    }
    
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        color: #000000;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 3px solid #007bff;
        color: #000000;
    }
    
    .sidebar-info h4 {
        color: #000000;
    }
    
    .sidebar-info ol {
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎓 Scholi the Scholarship Assistant</h1>
    <p>Find personalized scholarship opportunities based on your profile</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with information and controls
with st.sidebar:
    st.markdown("### 📋 Application Process")
    
    # Information panel
    st.markdown("""
    <div class="sidebar-info">
        <h4>💡 How it works</h4>
        <ol style="font-size: 0.9em;">
            <li>Answer 10 quick questions</li>
            <li>We analyze your profile</li>
            <li>Get personalized scholarship matches</li>
            <li>Apply with confidence!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # Reset button
    if st.button("🔄 Start Over", help="Reset the conversation and start fresh"):
        st.session_state.messages = []
        st.session_state.current_question = 1
        st.session_state.show_welcome = False
        st.session_state.welcome_timer = time.time()
        st.session_state.typing_response = ""
        st.session_state.typing_complete = True
        st.session_state.processing_response = False
        st.session_state.typing_text = ""
        st.session_state.typing_index = 0
        st.session_state.is_typing = False
        st.rerun()
    
    # Tips section
    with st.expander("📝 Tips for Better Results"):
        st.markdown("""
        - Be specific about your GPA and coursework
        - Mention all relevant activities and achievements
        - Include community involvement and leadership
        - Don't forget about unique circumstances
        """)

# AWS Setup
@st.cache_resource
def setup_bedrock():
    return boto3.client(
        'bedrock-agent-runtime',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        aws_session_token=os.getenv('AWS_SESSION_TOKEN'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

# Define questions at module level
questions = [
    "What is your current cumulative GPA? (e.g., 3.2)",
    "What is your declared major or intended field of study?",
    "How many college-level units have you completed?",
    "Are you enrolled full-time or part-time?",
    "Do you plan to transfer to a 4-year university?",
    "Have you completed the FAFSA application?",
    "Do you identify with any specific communities? (e.g., Former Foster Youth, African-American, Hispanic/Latinx, Asian/Pacific Islander, Armenian, LGBTQ+, Veterans/Military family, Students with disabilities, Single parents, etc.)",
    "Are you a California resident?",
    "What are your educational and career goals?",
    "Tell me about your clubs, certifications, and awards."
]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 1
if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = False
if "welcome_timer" not in st.session_state:
    st.session_state.welcome_timer = time.time()
if "typing_response" not in st.session_state:
    st.session_state.typing_response = ""
if "typing_complete" not in st.session_state:
    st.session_state.typing_complete = True
if "processing_response" not in st.session_state:
    st.session_state.processing_response = False
if "typing_text" not in st.session_state:
    st.session_state.typing_text = ""
if "typing_index" not in st.session_state:
    st.session_state.typing_index = 0
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# Check if AWS credentials are available
try:
    bedrock = setup_bedrock()
    kb_id = os.getenv('KNOWLEDGE_BASE_ID')
    
    if not kb_id:
        st.error("⚠️ Knowledge Base ID not configured. Please check your environment variables.")
        st.stop()
        
except Exception as e:
    st.error("⚠️ AWS configuration error. Please check your credentials.")
    st.stop()

# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    # Auto-show welcome message after 2 seconds for new users
    if len(st.session_state.messages) == 0 and not st.session_state.show_welcome:
        if time.time() - st.session_state.welcome_timer > 2:
            st.session_state.show_welcome = True
            first_question = "What is your current cumulative GPA? (e.g., 3.2)"
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "<h3>👋 Welcome!</h3>"
                    "<p>I'm here to help you find scholarships that match your profile. Let's start with a few questions to understand your background and goals.</p>"
                    f"<p><strong>First question:</strong> {first_question}</p>"
                )
            })
            st.rerun()
        else:
            # Show typing indicator
            st.markdown("""
            <div class="chat-message assistant-message" style="color: #111;">
                <strong>🎓 Scholarship Assistant:</strong><br>
                <span style="animation: blink 1.5s infinite;">💬 typing...</span>
            </div>
            <style>
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0.3; }
            }
            </style>
            """, unsafe_allow_html=True)
            time.sleep(0.5)
            st.rerun()

    # Display chat history with enhanced styling
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message" style="color: #111;">
                <strong>👤 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Show typing animation for questions only
            if (i == len(st.session_state.messages) - 1 and st.session_state.is_typing and 
                st.session_state.current_question < len(questions)):
                displayed_text = st.session_state.typing_text[:st.session_state.typing_index]
                st.markdown(f"""
                <div class="chat-message assistant-message" style="color: #111;">
                    <strong>🎓 Scholarship Assistant:</strong><br>
                    {displayed_text}<span style="animation: blink 1s infinite;">|</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Continue typing
                if st.session_state.typing_index < len(st.session_state.typing_text):
                    st.session_state.typing_index += 2  # 2 characters at a time
                    time.sleep(0.05)
                    st.rerun()
                else:
                    # Typing complete
                    st.session_state.is_typing = False
                    st.session_state.messages[-1]["content"] = st.session_state.typing_text
                    st.rerun()
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message" style="color: #111;">
                    <strong>🎓 Scholarship Assistant:</strong><br>
                    {message["content"]}
                </div>
                """, unsafe_allow_html=True)
with col2:
    pass

if prompt := st.chat_input("Type your answer here..."):
    # Add user message with enhanced display
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.processing_response = True
    st.rerun()  # Show user message immediately

# Process response if needed
if st.session_state.processing_response:
    st.session_state.processing_response = False
    
    # Show processing indicator
    with st.spinner("🔍 Processing your response..."):
        try:
            # Questions are now defined at module level
            
            # Determine response logic
            if len(st.session_state.messages) <= 1:
                next_question = questions[0]
                prompt_text = f"You are a friendly scholarship assistant. Ask: 'Question 1 of 10: {next_question}'. Keep it warm and encouraging."
            elif st.session_state.current_question <= len(questions):
                last_user_response = st.session_state.messages[-1]["content"]
                current_q = questions[st.session_state.current_question - 1]
                
                # Check if user wants to go back to previous question
                if "go back" in last_user_response.lower() or "last question" in last_user_response.lower():
                    if st.session_state.current_question > 1:
                        st.session_state.current_question -= 1
                        prev_q = questions[st.session_state.current_question - 1]
                        answer = f"Of course! Question {st.session_state.current_question} of 10: {prev_q}"
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                    else:
                        answer = f"We're already at the first question: Question {st.session_state.current_question} of 10: {current_q}"
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.rerun()
                elif st.session_state.current_question < len(questions):
                    next_q = questions[st.session_state.current_question]
                    prompt_text = f"""You are a scholarship assistant. Respond to the student naturally.
                    
Previous question: {current_q}
Student response: {last_user_response}
                    
If they need help: Explain briefly what you're asking for, then re-ask Question {st.session_state.current_question} of 10: {current_q}
                    
If gibberish: Re-ask Question {st.session_state.current_question} of 10: {current_q}
                    
If valid answer (including yes/no/not yet/etc): Say 'Great!' and ask Question {st.session_state.current_question + 1} of 10: {next_q}
                    
Do not re-ask the same question after giving advice. Move forward.
                    Do not explain your reasoning. Respond directly to the student."""
                else:
                    # This is question 10 - after this we should go to scholarship analysis
                    prompt_text = f"""You are a scholarship assistant. Respond to the student naturally.
                    
Previous question: {current_q}
Student response: {last_user_response}
                    
If they need help: Explain briefly what you're asking for, then re-ask Question {st.session_state.current_question} of 10: {current_q}
                    
If gibberish: Re-ask Question {st.session_state.current_question} of 10: {current_q}
                    
If valid answer: Say 'Great! Let me analyze your profile and find matching scholarships.'
                    
Do not explain your reasoning. Respond directly to the student."""
            else:
                # Analysis phase
                user_answers = []
                for i, msg in enumerate(st.session_state.messages):
                    if msg["role"] == "user":
                        question_num = (i + 1) // 2
                        if question_num <= len(questions):
                            user_answers.append(f"Q{question_num}: {questions[question_num-1]} A: {msg['content']}")
                
                answers_summary = "\n".join(user_answers)
                prompt_text = f"""Based on this student's profile, find ALL scholarships they are eligible for from the knowledge base. Calculate a match percentage for each scholarship and sort them from highest to lowest match.

Student Profile:
{answers_summary}

For each scholarship, MUST include:
1. **Scholarship Name** (with link if available)
2. **Match Percentage** (e.g., 95% Match) - based on how well they meet requirements
3. **Application Deadline** - ALWAYS show the deadline prominently
4. **Award Amount** if available
5. **Why they qualify** (specific requirements they meet)
6. **Next steps** for application

Sort scholarships from highest match percentage to lowest. Only show scholarships they qualify for.

Required format:
🏆 **[Scholarship Name]** - 95% Match
⏰ **Deadline: [Specific Date]** | 💰 Award: $X,XXX
✅ Why you qualify: [specific reasons]
📝 Next steps: [application process]

IMPORTANT: Always display the deadline prominently for each scholarship."""
            
            # Call Bedrock with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = bedrock.retrieve_and_generate(
                        input={'text': prompt_text},
                        retrieveAndGenerateConfiguration={
                            'type': 'KNOWLEDGE_BASE',
                            'knowledgeBaseConfiguration': {
                                'knowledgeBaseId': kb_id,
                                'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}'
                            }
                        }
                    )
                    
                    answer = response['output']['text']
                    
                    # Only increment question counter if model says "Great!" (valid response) OR if we're on question 10
                    if st.session_state.current_question <= len(questions) and ("Great!" in answer or st.session_state.current_question == len(questions)):
                        st.session_state.current_question += 1
                        
                    # If model says it will analyze scholarships, force the analysis
                    if "analyze your profile" in answer.lower() or "find matching scholarships" in answer.lower():
                        st.session_state.current_question = len(questions) + 1
                        st.session_state.processing_response = True
                    
                    break
                    
                except Exception as e:
                    if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 2)
                        continue
                    elif "ThrottlingException" in str(e):
                        st.error("🚫 Service temporarily overloaded. Please try again in a moment.")
                        st.stop()
                    else:
                        raise e
            
            # Add assistant response (simplified to avoid typing animation issues)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Scroll to top for scholarship results only
            if st.session_state.current_question > len(questions):
                st.markdown("""
                <script>
                setTimeout(function() {
                    var messages = document.querySelectorAll('.chat-message.assistant-message');
                    if (messages.length > 0) {
                        messages[messages.length - 1].scrollIntoView({behavior: 'smooth', block: 'start'});
                    }
                }, 100);
                </script>
                """, unsafe_allow_html=True)
            
            # Show success message for completion
            if st.session_state.current_question > len(questions):
                st.balloons()
                st.success("🎉 Analysis complete! Your scholarships are ranked by match percentage - highest matches first!")
                st.info("💡 Focus on scholarships with 80%+ match for the best chances of success.")
            
            # Auto-refresh to show new messages
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.markdown("""
            <div class="warning-card">
                <strong>Troubleshooting Tips:</strong>
                <ul>
                    <li>Check your internet connection</li>
                    <li>Verify AWS credentials are properly configured</li>
                    <li>Try clicking "Start Over" to reset</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🎓 Scholarship Assistant | Helping students find financial aid opportunities</p>
    <p style="font-size: 0.8em;">Built with Streamlit & AWS Bedrock | Secure & Private</p>
</div>
""", unsafe_allow_html=True)