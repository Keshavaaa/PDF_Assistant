summary_prompt = """
You are an expert summarizer. Summarize the following document in a concise and readable way:

{text}
"""


mcq_prompt = """
You are a smart question generator. From the text below, generate 3 multiple-choice questions (MCQs).
Each question must have:

- 4 options labeled (A), (B), (C), and (D), each on a new line.
- Each option (A), (B), (C), and (D) **must appear on a new line**.
- Make sure every option starts on a new line.
- Do not reveal the correct answer immediately after options. Place it only in the "Answer:" line. The "Answer:" to all questions should 
  be together at end of all questions.

Example:
Q1. What is the capital of France?  
(A) Berlin
(B) Paris 
(C) Madrid  
(D) Rome 


Q2. ...
...

Text:
{text}
Strictly adhere to above format
"""

plan_prompt = """
You are a learning assistant. From the following document, create a 7-day study or action plan by breaking down the content into daily portions with focus areas.

{text}
"""
