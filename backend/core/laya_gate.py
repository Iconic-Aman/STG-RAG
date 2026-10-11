from typing import Optional

_router = None

HEALTH_HINTS = [
    "malaria", "treatment", "medicine", "drug", "dose", "dosage", "clinical",
    "fever", "symptom", "disease", "patient", "diagnosis", "therapy", "syndrome",
    "emergency", "prescription", "essential", "adverse", "infection", "child", "pediatric"
]

def get_laya_router():
    global _router
    if _router is None:
        try:
            from laya import Router
            _router = Router()
        except Exception as e:
            print(f"Laya router init failed: {e}")
            _router = None
    return _router

def laya_decide_intent(query: str) -> str:
    cleaned = query.strip().lower()
    
    # 1. Zero-latency exact pattern matching
    if cleaned in {"hi", "hello", "hey", "greetings", "hi there", "hello there"}:
        return "greeting"
    if any(p in cleaned for p in ["what is your name", "what your name", "who are you", "your name"]):
        return "identity"

    # 2. Healthcare keyword guard to guarantee clinical retrieval
    if any(k in cleaned for k in HEALTH_HINTS):
        return "retrieve"

    # 3. Laya System 1 decision engine for ambiguous/off-topic classification
    router = get_laya_router()
    if router is not None:
        try:
            questions = {
                "intent": {
                    "type": "choice",
                    "instructions": "Is the user asking about healthcare/medicine, or something unrelated?",
                    "criteria": {
                        "retrieve": "medical questions, diseases, drugs, patient treatment, clinical guidance",
                        "greeting": "user says hello, hi, how are you, thanks, goodbye",
                        "off_topic": "weather, coding, sports, movies, politics, recipes, general non-medical trivia"
                    }
                }
            }
            res = router.predict(query, questions)
            choice = res["answers"]["intent"]["choice"]
            print(f"[Laya Router Decision]: query='{query}' -> intent='{choice}'")
            return choice
        except Exception as e:
            print(f"Laya inference error: {e}")

    # Default to retrieve for safe coverage
    return "retrieve"
