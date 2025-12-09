import os
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# Import your actual src modules
# Ensure these imports match your folder structure (e.g., from src.graph import ...)
from graph import create_retirement_graph
from tools_rag import rag_search_tool

# --- CONFIGURATION ---
sample_context_questions = [
    "What is my RMD?",
    "How much must I withdraw?",
    "Explain the Windfall Elimination Provision.",
    "How does Social Security work with pensions?",
    "What is the difference between Social Security and Medicare?",
]

sample_outcontext_questions = [
    "What is the capital of France?",
    "Who won the World Series in 2020?",
    "How to bake a cake?",
    "What is the latest news on technology?",
    "Tell me about the history of ancient Egypt.",
]

unanswered_indicators = [
    "I don't know",
    "I don't have that information",
    "I am not sure",
    "I cannot answer",
    "does not appear to be in my knowledge base",
    "I specialize in retirement-related questions. If you have any inquiries about retirement benefits, savings, or planning, feel free to ask!",
    "No relevant docs were retrieved using the relevance score threshold 0.4",
    "I do not have that information in my knowledge base. Would you like me to look it up for you?",
    "I specialize in retirement planning and benefits. If you have any questions related to retirement, Social Security, or financial planning, feel free to ask!",
    "I do not have that information in my knowledge base.",
    "I do not have that information in my knowledge base. If you have any questions related to retirement planning, social security, medicare, taxes, or financial wellness, feel free to ask!",


]

# --- HELPER FUNCTIONS ---

def parse_tool_output(tool_output: str):
    """
    Splits the tool output into 'Answer' and 'Context'.
    Adjust the 'split_marker' below to match EXACTLY what your rag_search_tool prints.
    """


    if tool_output is None:
        return "No Answer Generated", "No Context Found (Tool returned None)"
    
    if not isinstance(tool_output, str):
        tool_output = str(tool_output)

    # Check what your tool actually prints. Usually it's "Sources:" or "Source Documents:"
    split_marker = "Sources:" 
    
    if split_marker in tool_output:
        parts = tool_output.split(split_marker, 1)
        answer = parts[0].strip()
        context = parts[1].strip()
        return answer, context
    else:
        # If no sources found, treat whole text as answer and context as empty
        return tool_output.strip(), "No Context Provided"

def call_llm_judge(question, bot_answer, context):
    """
    LLM-as-a-Judge: Checks if the Answer is supported by the Context.
    """
    # If there is no context, the answer cannot be grounded (unless it admitted it didn't know)
    if context == "No Context Provided":
        return 0
        
    judge_llm = ChatOpenAI(model="gpt-4", temperature=0)

    prompt = f"""
    You are a RAG evaluator.
    
    QUESTION: {question}
    GENERATED ANSWER: {bot_answer}
    RETRIEVED CONTEXT: {context}
    
    Task: Check if the Answer is supported by the Context.
    - If the answer is fully supported by the context, score 1.
    - If the answer contradicts or hallucinates info not in context, score 0.
    
    Return ONLY the integer (0 or 1).
    """
    try:
        response = judge_llm.invoke(prompt).content.strip()
        return int(response)
    except:
        return 0

# --- METRIC 1: UNANSWERED RATE ---

def run_unanswered_rate_test(app):
    print("\n--- Metric 1: Unanswered Query Rate ---")
    
    # 1. Test In-Domain Questions (Should be Answered)
    failed_context_count = 0
    for q in sample_context_questions:
        print(f"Asking (In-Domain): {q}")
        res = app.invoke({"messages": [HumanMessage(content=q)]})
        final_response = res["messages"][-1].content
        print(f"--"*30)
        print(f"   [BOT REPLIED]: {final_response}")
        print(f"--"*30)
        
        # Check if any indicator phrase is inside the response
        if any(indicator.lower() in final_response.lower() for indicator in unanswered_indicators):
            failed_context_count += 1
            
    # 2. Test Out-of-Domain Questions (Should be Unanswered)
    success_outcontext_count = 0
    for q in sample_outcontext_questions:
        print(f"Asking (Out-Domain): {q}")
        res = app.invoke({"messages": [HumanMessage(content=q)]})
        final_response = res["messages"][-1].content
        print(f"--"*30)
        print(f"  [BOT REPLIED]: {final_response}")
        print(f"--"*30)
        
        # Here, "Unanswered" is actually a SUCCESS for out-of-domain
        if any(indicator.lower() in final_response.lower() for indicator in unanswered_indicators):
            success_outcontext_count += 1

    # Calculate Rates
    # Rate of FAILURE for in-domain (Lower is better)
    in_domain_fail_rate = (failed_context_count / len(sample_context_questions)) * 100
    
    # Rate of SUCCESS for out-domain (Higher is better - means we correctly refused)
    out_domain_refusal_rate = (success_outcontext_count / len(sample_outcontext_questions)) * 100

    # Print Rates
    print(f"Failed Context Count: {failed_context_count}")
    print(f"Success Out-Context Count: {success_outcontext_count}")

    print(f"Total In-Domain Questions: {len(sample_context_questions)}")
    print(f"Total Out-of-Domain Questions: {len(sample_outcontext_questions)}")

    print(f"\nIn-Domain Failure Rate (Lower is better): {in_domain_fail_rate}%")
    print(f"Out-Domain Refusal Rate (Higher is better): {out_domain_refusal_rate}%")

    return in_domain_fail_rate, out_domain_refusal_rate

# --- METRIC 2: GROUNDEDNESS ---

def run_groundedness_test():
    print("\n--- Metric 2: Groundedness (LLM Judge) ---")
    total_score = 0
    
    # Only test in-domain questions for groundedness
    for q in sample_context_questions:
        print(f"Judging: {q}")
        
        # A. Call Tool DIRECTLY (Bypass Router to test RAG quality purely)
        # Note: We assume rag_search_tool returns a string. If it returns a Document object, access .page_content
        tool_output = rag_search_tool.invoke(q)

        print(f"   [DEBUG] Tool Output Type: {type(tool_output)}")
        
        # B. Parse
        generated_answer, retrieved_context = parse_tool_output(tool_output)
        
        # C. Judge
        score = call_llm_judge(q, generated_answer, retrieved_context)
        print(f"  -> Score: {score}/1")
        total_score += score

    avg_score = (total_score / len(sample_context_questions)) * 100
    print(f"\nFinal Groundedness Score: {avg_score}%")

    return avg_score

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    # Initialize Graph for Metric 1
    graph_app = create_retirement_graph()
    
    # Run Metric 1 (Router Behavior)
    in_domain_fail_rate, out_domain_refusal_rate = run_unanswered_rate_test(graph_app)

    # Run Metric 2 (RAG Quality)
    # avg_score = run_groundedness_test()

    print(f"\nIn-Domain Failure Rate (Lower is better): {in_domain_fail_rate}%")
    print(f"Out-Domain Refusal Rate (Higher is better): {out_domain_refusal_rate}%")
    # print(f"Final Groundedness Score: {avg_score}%")
    