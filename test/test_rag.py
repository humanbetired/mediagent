from agents.medical_rag import MedicalRAGAgent

agent = MedicalRAGAgent()

questions = [
    "What are the normal ranges for SpO2 and what happens below 88%?",
    "What protocol should be followed for hypertensive crisis?",
    "How should diabetic patients be monitored differently?"
]

for q in questions:
    result = agent.query(q)
    print("\n" + "="*60)
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
    print(f"Sources: {[s['file'] for s in result['sources']]}")
    print("="*60)