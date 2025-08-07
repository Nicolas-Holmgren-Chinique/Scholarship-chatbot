import streamlit as st
import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup
st.set_page_config(page_title="Simple RAG Chatbot", page_icon="🤖")
st.title("Scholi 🎓🤖 - Your AI Scholarship Assistant")

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

# Initialize
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add initial welcome message
    welcome_message = """
    👋 **Welcome to Scholi 🎓!**

    I'm your AI scholarship assistant specifically designed to help **community college students** find scholarships! 💸

    I'll ask you a few quick questions to match you with scholarships you qualify for from our database. Let's get started:

    **Question 1 of 5:**
    
    📚 **What is your major?**
    
    Please tell me your field of study or major (e.g., Nursing, Business, Engineering, Liberal Arts, etc.)
    """

    st.session_state.messages.append({"role": "assistant", "content": welcome_message})
    st.session_state.conversation_stage = "major"
    st.session_state.student_profile = {}

bedrock = setup_bedrock()
kb_id = os.getenv('KNOWLEDGE_BASE_ID')

# Check if required environment variables are set
if not kb_id:
    st.error("⚠️ KNOWLEDGE_BASE_ID is not set in your .env file. Please add your AWS Bedrock Knowledge Base ID.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Tell me about your major, background, or ask about scholarships..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Update student profile based on conversation stage
    if 'student_profile' not in st.session_state:
        st.session_state.student_profile = {}
    
    current_stage = st.session_state.get('conversation_stage', 'major')
    
    if current_stage == "major":
        st.session_state.student_profile['major'] = prompt
        st.session_state.conversation_stage = "gender"
    elif current_stage == "gender":
        st.session_state.student_profile['gender'] = prompt
        st.session_state.conversation_stage = "first_gen"
    elif current_stage == "first_gen":
        st.session_state.student_profile['first_generation'] = prompt
        st.session_state.conversation_stage = "veteran"
    elif current_stage == "veteran":
        st.session_state.student_profile['veteran_status'] = prompt
        st.session_state.conversation_stage = "fafsa"
    elif current_stage == "fafsa":
        st.session_state.student_profile['fafsa_eligible'] = prompt
        st.session_state.conversation_stage = "complete"
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call Bedrock Knowledge Base
                response = bedrock.retrieve_and_generate(
                    input={
                        'text': (
                            "You are Scholi, a helpful scholarship matching assistant for community college students at Foothill-De Anza Community College District. "
                            "Your purpose is to help students find scholarships they qualify for by asking standard scholarship eligibility questions. "
                            "This is similar to filling out a scholarship application form. "
                            
                            "You need to ask exactly 5 standard scholarship eligibility questions in this order: "
                            "1. What is your field of study/major? "
                            "2. What gender do you identify as? (for gender-specific scholarships) "
                            "3. Are you a first-generation college student? (many scholarships target first-gen students) "
                            "4. Are you a military veteran? (for veteran-specific scholarships) "
                            "5. Do you qualify for federal financial aid (FAFSA)? (for need-based scholarships) "
                            
                            f"Current conversation stage: {st.session_state.get('conversation_stage', 'major')}\n"
                            f"Student information collected so far: {str(st.session_state.get('student_profile', {}))}\n\n"
                            
                            f"Student's response: {prompt}\n\n"
                            
                            "Instructions based on conversation progress: "
                            "- If they just answered about their major, thank them and ask question 2 about gender identity for gender-specific scholarships "
                            "- If they just answered about gender, thank them and ask question 3 about first-generation status "
                            "- If they just answered about first-generation status, thank them and ask question 4 about veteran status "
                            "- If they just answered about veteran status, thank them and ask question 5 about FAFSA eligibility "
                            "- If they've answered all 5 questions, search the scholarship database for matching opportunities and provide specific recommendations "
                            
                            "Always be encouraging and professional. Explain that these questions help match them with relevant scholarships. "
                            "Keep responses brief and focused. When providing final recommendations, cite specific scholarships from the knowledge base."
                        )
                    },
                    retrieveAndGenerateConfiguration={
                        'type': 'KNOWLEDGE_BASE',
                        'knowledgeBaseConfiguration': {
                            'knowledgeBaseId': kb_id,
                            'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}',
                            'generationConfiguration': {
                                'inferenceConfig': {
                                    'textInferenceConfig': {
                                        'temperature': 0.1,
                                        'maxTokens': 300
                                    }
                                }
                            }
                        }
                    },
                )
                
                answer = response['output']['text']
                st.write(answer)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {e}")