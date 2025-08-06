import streamlit as st
import boto3
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup
st.set_page_config(page_title="Simple RAG Chatbot", page_icon="🤖")
st.title("Simple RAG Chatbot")


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
if "current_question" not in st.session_state:
    st.session_state.current_question = 1

bedrock = setup_bedrock()
kb_id = os.getenv('KNOWLEDGE_BASE_ID')

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Define questions
                questions = [
                    "What is your current cumulative GPA? (e.g., 3.2)",
                    "What is your declared major or intended field of study?",
                    "How many college-level units have you completed?",
                    "Are you enrolled full-time or part-time?",
                    "Do you plan to transfer to a 4-year university?",
                    "Have you completed the FAFSA application?",
                    "Do you identify with any specific communities?",
                    "Are you a California resident?",
                    "What are your educational and career goals?",
                    "Tell me about your clubs, certifications, and awards."
                ]
                
                # Determine next question or analyze eligibility
                if len(st.session_state.messages) <= 1:
                    next_question = questions[0]
                    prompt_text = f"You are a scholarship assistant. Ask: '{next_question}'"
                elif st.session_state.current_question < len(questions):
                    st.session_state.current_question += 1
                    next_question = questions[st.session_state.current_question - 1]
                    prompt_text = f"You are a scholarship assistant. Acknowledge the user's answer: '{prompt}' and then ask: '{next_question}'"
                else:
                    # All questions completed - analyze eligibility
                    user_answers = []
                    for i, msg in enumerate(st.session_state.messages):
                        if msg["role"] == "user":
                            question_num = (i + 1) // 2
                            if question_num <= len(questions):
                                user_answers.append(f"Q{question_num}: {questions[question_num-1]} A: {msg['content']}")
                    
                    answers_summary = "\n".join(user_answers)
                    prompt_text = f"""Based on these student answers, find ONLY scholarships they are eligible for from the knowledge base. Do not mention scholarships they don't qualify for.

Student Profile:
{answers_summary}

Analyze the knowledge base and list only the scholarships this student qualifies for, with specific eligibility requirements they meet."""
                
                # Retry logic for throttling
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Call Bedrock Knowledge Base
                        response = bedrock.retrieve_and_generate(
                            input={
                                'text': prompt_text
                            },
                            retrieveAndGenerateConfiguration={
                                'type': 'KNOWLEDGE_BASE',
                                'knowledgeBaseConfiguration': {
                                    'knowledgeBaseId': kb_id,
                                    'modelArn': f'arn:aws:bedrock:{os.getenv("AWS_DEFAULT_REGION")}::foundation-model/{os.getenv("BEDROCK_MODEL_ID")}'
                                }
                            }
                        )
                        
                        answer = response['output']['text']
                        st.write(answer)
                        break
                        
                    except Exception as e:
                        if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                            time.sleep((attempt + 1) * 2)
                            continue
                        elif "ThrottlingException" in str(e) and attempt == max_retries - 1:
                            st.error("Service is currently overloaded. Please try again later.")
                            st.stop()
                        else:
                            raise e
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {e}")
