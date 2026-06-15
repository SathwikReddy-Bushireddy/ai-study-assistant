import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

def get_llm(google_api_key, model_name="gemini-2.5-flash", temperature=0.2):
    """
    Initializes and returns the Gemini Chat Model.
    """
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=google_api_key,
        temperature=temperature
    )

def answer_question(llm, query, context_chunks, chat_history):
    """
    Generates a RAG-grounded answer for the user query based on retrieved context chunks.
    Maintains chat history for a coherent conversation.
    
    Args:
        llm: ChatGoogleGenerativeAI instance
        query: Current user question
        context_chunks: List of retrieved Document chunks
        chat_history: List of dicts [{"role": "user"/"assistant", "content": "..."}]
        
    Returns:
        A tuple of (answer_text, citations_list).
    """
    # 1. Prepare citations
    citations = []
    context_text_blocks = []
    
    for idx, chunk in enumerate(context_chunks):
        source_name = chunk.metadata.get("source", "Unknown Document")
        page_num = chunk.metadata.get("page", "?")
        context_text_blocks.append(
            f"[Source {idx+1}] File: {source_name}, Page: {page_num}\nContent: {chunk.page_content}"
        )
        citations.append({
            "id": idx + 1,
            "source": source_name,
            "page": page_num,
            "content": chunk.page_content
        })
        
    context_str = "\n\n".join(context_text_blocks)
    
    # 2. Build system instruction
    system_instruction = (
        "You are an expert AI Study Assistant acting as a personal tutor. "
        "Your goal is to answer the user's query using the provided document context blocks. "
        "Strictly follow these rules:\n"
        "1. Prioritize answering using the provided document context.\n"
        "2. Ground your facts in the sources. Use inline citations like [Source 1], [Source 2], etc. "
        "corresponding to the sources in the context.\n"
        "3. If the answer cannot be found in the provided context, clearly state that the information is "
        "not explicitly mentioned in the uploaded documents. After stating this, you may provide a helpful answer "
        "using your general knowledge, but clearly demarcate it by starting the section with: "
        "'[General Knowledge Supplement]'.\n"
        "4. Maintain a friendly, clear, and encouraging educational tone."
    )
    
    # 3. Build messages list (System + Chat History + Context & Query)
    messages = [SystemMessage(content=system_instruction)]
    
    # Add history
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    # Add current prompt with context
    current_prompt = (
        f"Retrieved Document Context:\n"
        f"---------------------\n"
        f"{context_str}\n"
        f"---------------------\n"
        f"User Query: {query}\n"
    )
    messages.append(HumanMessage(content=current_prompt))
    
    # 4. Generate answer
    response = llm.invoke(messages)
    return response.content, citations

def generate_summary(llm, documents):
    """
    Generates a structured study guide summary from the extracted document pages.
    """
    if not documents:
        return "No document text available to summarize."
        
    # Concatenate the first few thousand words to build a context-rich summary
    # (prevents hitting API limits for extremely large textbooks, while covering key content)
    full_text = ""
    for doc in documents[:30]:  # Limit to first 30 pages for summary to ensure quick response
        full_text += f"\n--- Page {doc.metadata.get('page', '')} ---\n{doc.page_content}"
        if len(full_text) > 40000:
            full_text = full_text[:40000] + "\n... [Content Truncated for Summary] ..."
            break
            
    prompt = (
        "You are a master educator. Analyze the provided study material and generate a comprehensive "
        "Study Guide Summary. Use Markdown formatting and structure the output exactly as follows:\n\n"
        "# 📘 Study Guide Summary\n"
        "## 🔍 Executive Overview\n"
        "Provide a high-level, 3-4 sentence overview of the core subject matter.\n\n"
        "## 🔑 Key Concepts & Definitions\n"
        "Create a Markdown table with columns: **Concept/Term** | **Description / Significance**.\n\n"
        "## 📌 Detailed Breakdown & Core Topics\n"
        "Create bullet points outlining the main arguments, chapters, or topic sub-sections. Explain them clearly.\n\n"
        "## 💡 Study Tips & Recommendations\n"
        "Provide 3 actionable tips for learning or memorizing these materials.\n\n"
        f"Here is the study material:\n{full_text}"
    )
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

def parse_json_from_response(text):
    """
    Cleans and parses a JSON response from the LLM, handling markdown code blocks.
    """
    # Remove markdown code blocks if present
    cleaned = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"```\s*$", "", cleaned)
    cleaned = cleaned.strip()
    
    # Attempt to locate the JSON array or object structure
    start_idx = cleaned.find('[')
    end_idx = cleaned.rfind(']')
    
    if start_idx != -1 and end_idx != -1:
        cleaned = cleaned[start_idx:end_idx + 1]
    else:
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}')
        if start_idx != -1 and end_idx != -1:
            cleaned = cleaned[start_idx:end_idx + 1]
            
    return json.loads(cleaned)

def generate_quiz(llm, documents, num_questions=5):
    """
    Generates a list of multiple-choice questions from the document chunks.
    Returns a list of dicts.
    """
    if not documents:
        return []
        
    # Gather sample text chunks (up to ~15000 characters) to ground the quiz
    sample_text = ""
    for doc in documents[:15]:
        sample_text += f"\n{doc.page_content}"
        if len(sample_text) > 15000:
            sample_text = sample_text[:15000]
            break
            
    prompt = (
        f"Generate {num_questions} high-quality multiple-choice questions (MCQs) from the following study material. "
        "The quiz should test key concepts and facts. You MUST return ONLY a JSON array, with no other text, conversational intro/outro, or code blocks. "
        "Format the JSON array as follows:\n"
        "[\n"
        "  {\n"
        "    \"question\": \"Question text here...\",\n"
        "    \"options\": [\"Option A\", \"Option B\", \"Option C\", \"Option D\"],\n"
        "    \"answer\": \"Option A\",\n"
        "    \"explanation\": \"Detailed explanation explaining why Option A is correct and why other options are incorrect.\"\n"
        "  }\n"
        "]\n\n"
        f"Study Material:\n{sample_text}"
    )
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return parse_json_from_response(response.content)
    except Exception as e:
        print(f"Error generating or parsing quiz: {e}")
        # Return fallback quiz structure
        return [
            {
                "question": "An error occurred generating the quiz. Please upload documents and try again.",
                "options": ["Error detail 1", "Error detail 2", "Error detail 3", "Error detail 4"],
                "answer": "Error detail 1",
                "explanation": f"The model returned a parse error: {e}"
            }
        ]

def generate_flashcards(llm, documents, num_cards=5):
    """
    Generates a list of study flashcards (front/back concepts) from the document chunks.
    """
    if not documents:
        return []
        
    sample_text = ""
    for doc in documents[:15]:
        sample_text += f"\n{doc.page_content}"
        if len(sample_text) > 15000:
            sample_text = sample_text[:15000]
            break
            
    prompt = (
        f"Generate {num_cards} interactive study flashcards from the following study material. "
        "Each flashcard should contain a core term or question on the front, and its definition or answer on the back. "
        "You MUST return ONLY a JSON array, with no other text, conversational intro/outro, or code blocks. "
        "Format the JSON array as follows:\n"
        "[\n"
        "  {\n"
        "    \"front\": \"Core term / Concept name / Question...\",\n"
        "    \"back\": \"Short, digestible definition / Answer / Formula...\"\n"
        "  }\n"
        "]\n\n"
        f"Study Material:\n{sample_text}"
    )
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return parse_json_from_response(response.content)
    except Exception as e:
        print(f"Error generating or parsing flashcards: {e}")
        return [
            {
                "front": "Oops!",
                "back": f"There was an error generating flashcards: {e}. Please try again."
            }
        ]
