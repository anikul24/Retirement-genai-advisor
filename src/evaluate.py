# Simple Evaluation Concept
def evaluate_answer(question, bot_answer, ground_truth):
    prompt = f"""
    Question: {question}
    Bot Answer: {bot_answer}
    Correct Answer: {ground_truth}
    
    Grade the Bot Answer on a scale of 1-5 based on accuracy. 
    Output ONLY the number.
    """
    # Call OpenAI with this prompt to get a score
    # score = llm.invoke(prompt)
    # return score