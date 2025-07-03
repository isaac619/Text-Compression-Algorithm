import random
import json
import os
from dataclasses import dataclass
from enum import Enum
import google.generativeai as genai
from gemini_prompts import RECONSTRUCT_PROMPT
import string



class Tone(Enum):
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    NEUTRAL = "neutral"
    POLITE = "polite"
    DIRECT = "direct"

class Formality(Enum):
    INFORMAL = "informal"
    SEMI_FORMAL = "semi-formal"
    FORMAL = "formal"

class Type(Enum):
    INVITATION = "invitation"
    REQUEST = "request"
    STATEMENT = "statement"
    QUESTION = "question"
    GREETING = "greeting"
    FAREWELL = "farewell"
    APOLOGY = "apology"
    THANK_YOU = "thank_you"
    CONFIRMATION = "confirmation"
    SUGGESTION = "suggestion"

@dataclass
class SemanticAttributes:
    sent_type: object = None
    tone: object = None
    formality: object = None
    action: object = None
    subject: object = None
    object: object = None

class SemanticCompressor:
    def __init__(self):
        self.formal_words = {
            "polite_requests": ["please", "kindly", "would you", "could you", "might you", "if you could"],
            "formal_greetings": ["dear", "sir", "madam", "regards", "respectfully", "to whom it may concern"],
            "formal_connectors": ["regarding", "concerning", "with respect to", "in reference to", "pertaining to"],
            "formal_closings": ["sincerely", "yours truly", "best regards", "cordially", "faithfully"],
            "formal_indicators": ["therefore", "thus", "hence", "consequently", "accordingly"]
        }
        
        self.informal_words = {
            "casual_greetings": ["hey", "yo", "sup", "what's up", "howdy", "hiya"],
            "slang": ["dude", "bro", "man", "guy", "buddy", "pal", "mate", "chum"],
            "contractions": ["gonna", "wanna", "gotta", "lemme", "dunno", "y'know", "c'mon"],
            "casual_closings": ["later", "peace", "catch ya", "see ya", "take it easy", "cheers"],
            "casual_indicators": ["like", "you know", "sort of", "kind of", "basically"]
        }
        
        self.tone_words = {
            "friendly": ["hey", "hi", "hello", "buddy", "friend", "great", "nice", "welcome", "glad"],
            "formal": ["regarding", "respectfully", "dear", "sir", "madam", "concerning", "properly"],
            "casual": ["yo", "dude", "bro", "sup", "man", "guy", "cool", "awesome"],
            "enthusiastic": ["amazing", "fantastic", "wonderful", "great", "awesome", "excellent", "brilliant", "outstanding"],
            "polite": ["please", "thank you", "kindly", "would you", "could you", "appreciate", "grateful"],
            "direct": ["now", "immediately", "just", "simply", "directly", "straightforward", "clearly"],
            "urgent": ["urgent", "asap", "immediately", "right away", "now", "quickly", "hurry"],
            "apologetic": ["sorry", "apologize", "excuse me", "pardon", "regret", "my bad", "my mistake"],
            "confident": ["definitely", "certainly", "absolutely", "surely", "obviously", "clearly"]
        }
        
        self.type_words = {
            "invitation": ["let's", "lets", "join", "come", "meet", "invite", "how about", "would you like to", "care to"],
            "request": ["please", "could you", "can you", "would you", "send", "confirm", "let me know", "need", "require"],
            "question": ["?", "what", "when", "where", "how", "why", "who", "which", "whose", "is", "are", "do", "does"],
            "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "greetings"],
            "farewell": ["bye", "goodbye", "see you", "take care", "have a good day", "until next time", "farewell"],
            "apology": ["sorry", "apologize", "excuse me", "pardon", "regret", "my bad", "my mistake", "forgive me"],
            "thank_you": ["thank you", "thanks", "appreciate", "grateful", "obliged", "thankful"],
            "confirmation": ["yes", "confirm", "agree", "okay", "sure", "absolutely", "definitely", "certainly"],
            "suggestion": ["maybe", "suggest", "how about", "what if", "consider", "perhaps", "might want to"],
            "command": ["do", "make", "get", "find", "bring", "take", "go", "come", "stop", "start"]
        }
        
        self.action_verbs = {
            "communication": ["send", "call", "text", "email", "message", "contact", "reach", "notify", "inform", "tell"],
            "movement": ["meet", "come", "go", "join", "attend", "visit", "travel", "arrive", "leave", "return"],
            "cognition": ["think", "know", "understand", "remember", "forget", "realize", "believe", "consider"],
            "emotion": ["love", "like", "hate", "want", "need", "hope", "wish", "enjoy", "appreciate"],
            "action": ["make", "do", "create", "build", "fix", "solve", "work", "complete", "finish"],
            "possession": ["get", "have", "take", "bring", "grab", "find", "buy", "obtain", "receive"]
        }
        
        self.subject_pronouns = ["i", "you", "we", "they", "he", "she", "it", "this", "that", "these", "those", "me", "us", "them"]
        
        self.common_nouns = {
            "time": ["time", "day", "week", "month", "year", "hour", "minute", "moment", "period", "schedule"],
            "place": ["place", "location", "office", "home", "restaurant", "meeting", "room", "area", "space"],
            "thing": ["thing", "item", "object", "stuff", "material", "equipment", "tool", "device"],
            "person": ["person", "people", "friend", "colleague", "manager", "team", "group", "individual"],
            "document": ["report", "document", "file", "paper", "email", "message", "letter", "note"]
        }
        
        self.function_words = ["the", "and", "but", "for", "with", "from", "to", "in", "on", "at", "by", "of", "a", "an", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "must"]

    def analyze_sentence(self, sentence):
        s = sentence.lower()
        words = s.split()
        
        formality_score = 0
        for category, word_list in self.formal_words.items():
            for word in word_list:
                if word in s:
                    formality_score += 2  
        
        for category, word_list in self.informal_words.items():
            for word in word_list:
                if word in s:
                    formality_score -= 2  
        
        if any(word in s for word in ["would you", "could you", "might you"]):
            formality_score += 1
        if any(word in s for word in ["gonna", "wanna", "gotta"]):
            formality_score -= 1
            
        if formality_score > 1:
            formality = Formality.FORMAL
        elif formality_score < -1:
            formality = Formality.INFORMAL
        else:
            formality = Formality.SEMI_FORMAL
        
        tone_scores = {k: 0 for k in self.tone_words}
        for tone, twords in self.tone_words.items():
            for word in twords:
                if word in s:
                    tone_scores[tone] += 1
                    if s.count(word) > 1:
                        tone_scores[tone] += 0.5
        
        if tone_scores["formal"] > 0 and tone_scores["casual"] > 0:
            if tone_scores["formal"] > tone_scores["casual"]:
                tone_scores["casual"] = 0
            else:
                tone_scores["formal"] = 0
        
        if tone_scores["enthusiastic"] > 0:
            for tone in ["friendly", "casual"]:
                if tone_scores[tone] < tone_scores["enthusiastic"]:
                    tone_scores[tone] = 0
        
        tone = max(tone_scores, key=lambda k: tone_scores[k]) if any(tone_scores.values()) else "neutral"
        if tone not in Tone.__members__:
            tone = Tone.NEUTRAL
        else:
            tone = Tone[tone.upper()]
        
        type_scores = {k: 0 for k in self.type_words}
        for t, twords in self.type_words.items():
            for word in twords:
                if word in s:
                    type_scores[t] += 1
                    if t == "question" and "?" in s:
                        type_scores[t] += 2
                    if t in ["invitation", "enthusiastic"] and "!" in s:
                        type_scores[t] += 1
        
        sent_type = max(type_scores, key=lambda k: type_scores[k]) if any(type_scores.values()) else "statement"
        sent_type = Type[sent_type.upper()] if sent_type.upper() in Type.__members__ else Type.STATEMENT
        
        action = None
        subject = None
        obj = None
        
        all_verbs = []
        for category in self.action_verbs.values():
            all_verbs.extend(category)
        
        for w in words:
            if w in all_verbs and not action:
                action = w
                break
        
        for w in words:
            if w in self.subject_pronouns and not subject:
                subject = w
                break
        
        if not subject:
            for w in words:
                if w not in all_verbs and w not in self.function_words and len(w) > 2 and w not in ["please", "kindly"]:
                    subject = w
                    break
        
        important_objects = [
            "lunch", "dinner", "breakfast", "report", "document", "file", "email", "message", "meeting", "event", "attendance", "confirmation", "response", "answer", "feedback", "review", "comment", "suggestion", "idea", "thought", "opinion", "plan", "project", "task", "assignment", "homework", "presentation", "proposal", "contract", "agreement", "offer", "request", "question", "solution", "result", "decision", "option", "possibility", "opportunity"
        ]
        clean_words = [w.strip(string.punctuation) for w in words]
        for w in clean_words:
            if w in important_objects:
                obj = w
                break
        if not obj:
            for w in clean_words:
                if w not in self.subject_pronouns and w != action and w not in self.function_words and w not in ["please", "kindly", "man", "guy", "buddy", "pal"]:
                    if len(w) > 2 and not w in all_verbs and w != subject:
                        if w not in ["time", "thing", "place", "stuff", "item", "object"]:
                            obj = w
                            break
        
        return SemanticAttributes(
            sent_type=sent_type,
            tone=tone,
            formality=formality,
            action=action,
            subject=subject,
            object=obj
        )

    def compress(self, sentence):
        attributes = self.analyze_sentence(sentence)
        return {
            "type": attributes.sent_type.value,
            "tone": attributes.tone.value,
            "formality": attributes.formality.value,
            "action": attributes.action,
            "subject": attributes.subject,
            "object": attributes.object
        }

class GeminiAISentenceReconstructor:
    def __init__(self, api_key = None):
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable in bashrc or pass it using export in your terminal.")
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def reconstruct(self, compressed_data):
        prompt = RECONSTRUCT_PROMPT.format(data=json.dumps(compressed_data, indent=2))
        response = self.model.generate_content(prompt)
        return response.text.strip()

def main():
    api_key = os.getenv('GEMINI_API_KEY')
    compressor = SemanticCompressor()
    reconstructor = GeminiAISentenceReconstructor(api_key=api_key)
    test_sentences = [
        "Hey man, let's meet for lunch!",
    ]
    for i, sentence in enumerate(test_sentences, 1):
        print(f"Original {i}: {sentence}")
        compressed = compressor.compress(sentence)
        print(f"Compressed: {compressed}")
        reconstructed = reconstructor.reconstruct(compressed)
        print(f"Reconstructed: {reconstructed}")
        print("-" * 50)
    

if __name__ == "__main__":
    main() 
