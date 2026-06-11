INTERVIEW_ROLES = {
    "ai_engineer": {
        "label": "AI Engineer",
        "topics": ["machine learning", "deep learning", "LLMs", "MLOps", "NLP"],
    },
    "ml_engineer": {
        "label": "Machine Learning Engineer",
        "topics": ["supervised learning", "unsupervised learning", "feature engineering", "model evaluation", "deployment"],
    },
    "data_scientist": {
        "label": "Data Scientist",
        "topics": ["statistics", "data analysis", "visualization", "hypothesis testing", "experimental design"],
    },
    "mern_developer": {
        "label": "MERN Developer",
        "topics": ["MongoDB", "Express", "React", "Node.js", "REST API"],
    },
    "backend_engineer": {
        "label": "Backend Engineer",
        "topics": ["API design", "databases", "caching", "scalability", "authentication"],
    },
    "system_design": {
        "label": "System Design",
        "topics": ["distributed systems", "load balancing", "databases", "microservices", "scalability"],
    },
}

DIFFICULTIES = ["beginner", "intermediate", "advanced"]

STATIC_QUESTIONS = {
    ("ai_engineer", "beginner"): [
        "What is overfitting in machine learning?",
        "What is the difference between supervised and unsupervised learning?",
        "What is gradient descent?",
    ],
    ("ai_engineer", "intermediate"): [
        "How does backpropagation work in neural networks?",
        "What is dropout and why is it used?",
        "Explain the bias-variance tradeoff.",
    ],
    ("ai_engineer", "advanced"): [
        "How would you reduce hallucination in a production RAG system?",
        "Explain how LoRA fine-tuning works.",
        "How do you evaluate an LLM-based application?",
    ],
    ("ml_engineer", "beginner"): [
        "What is cross-validation?",
        "How do you handle imbalanced datasets?",
        "What is feature scaling and why is it important?",
    ],
    ("ml_engineer", "intermediate"): [
        "How does random forest work?",
        "What is the difference between bagging and boosting?",
        "Explain precision, recall, and F1-score.",
    ],
    ("ml_engineer", "advanced"): [
        "How would you design a real-time fraud detection system?",
        "Explain model monitoring and drift detection.",
        "How do you optimize inference latency for a production model?",
    ],
    ("data_scientist", "beginner"): [
        "What is p-value in hypothesis testing?",
        "What is the difference between correlation and causation?",
        "What is A/B testing?",
    ],
    ("data_scientist", "intermediate"): [
        "How do you handle missing data in a dataset?",
        "What is feature importance and how do you compute it?",
        "Explain the difference between L1 and L2 regularization.",
    ],
    ("data_scientist", "advanced"): [
        "How would you design an experimentation platform?",
        "Explain causal inference methods.",
        "How do you validate a recommendation system?",
    ],
    ("system_design", "beginner"): [
        "Design a URL shortening service like TinyURL.",
        "Design a chat application.",
    ],
    ("system_design", "intermediate"): [
        "Design a distributed key-value store.",
        "Design a real-time leaderboard system.",
    ],
    ("system_design", "advanced"): [
        "Design a RAG chatbot for university documents.",
        "Design a model monitoring and alerting system.",
    ],
}


def get_questions_for_role(role: str, difficulty: str) -> list[str]:
    return STATIC_QUESTIONS.get((role, difficulty), [
        f"Tell me about your experience with {role.replace('_', ' ')}.",
    ])
