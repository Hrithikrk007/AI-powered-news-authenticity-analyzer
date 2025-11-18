# nlp_engine.py
import os
import traceback
from typing import Dict
from keybert import KeyBERT

# Transformers imports guarded to allow safe fallback
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    import torch.nn.functional as F
    TRANSFORMERS_AVAILABLE = True
except Exception:
    TRANSFORMERS_AVAILABLE = False

# Lightweight fallback keyword method for fake detection (if transformers fail)
def heuristic_fake_detection(text: str) -> Dict:
    text_l = text.lower()
    fake_signals = ["clickbait", "conspiracy", "miracle", "secret", "shocking", "unbelievable", "will explode", "aliens", "hoax"]
    score = sum(1 for k in fake_signals if k in text_l)
    fake_prob = min(0.95, 0.2 + 0.15 * score)
    real_prob = 1.0 - fake_prob
    label = "FAKE NEWS ❌" if fake_prob > real_prob else "REAL NEWS ✔️"
    return {"label": label, "real_prob": float(real_prob), "fake_prob": float(fake_prob)}

# Initialize models if possible
if TRANSFORMERS_AVAILABLE:
    try:
        summarizer = pipeline("summarization", model=os.environ.get("SUM_MODEL", "facebook/bart-large-cnn"))
        sentiment_analyzer = pipeline("sentiment-analysis", model=os.environ.get("SENT_MODEL", "cardiffnlp/twitter-roberta-base-sentiment"))
        emotion_analyzer = pipeline("text-classification", model=os.environ.get("EMO_MODEL", "j-hartmann/emotion-english-distilroberta-base"), top_k=None)
        topic_classifier = pipeline("zero-shot-classification", model=os.environ.get("TOPIC_MODEL", "facebook/bart-large-mnli"))
        nli_tokenizer = AutoTokenizer.from_pretrained("roberta-large-mnli")
        nli_model = AutoModelForSequenceClassification.from_pretrained("roberta-large-mnli")
    except Exception:
        TRANSFORMERS_AVAILABLE = False
        traceback.print_exc()

# KeyBERT (may be heavy but used with try/except)
try:
    kw_model = KeyBERT()
except Exception:
    kw_model = None

def safe_summarize(text: str) -> str:
    try:
        if not TRANSFORMERS_AVAILABLE or len(text.split()) < 30:
            return "Text too short or summarizer not available."
        max_len = min(150, max(30, int(len(text.split()) * 0.6)))
        out = summarizer(text, max_length=max_len, min_length=20, do_sample=False)
        if isinstance(out, list) and out and "summary_text" in out[0]:
            return out[0]["summary_text"]
        return str(out)[:500]
    except Exception:
        return "Summary failed."

def fake_detection(text: str) -> Dict:
    if not text:
        return {"label":"UNKNOWN","real_prob":0.0,"fake_prob":0.0}
    if TRANSFORMERS_AVAILABLE:
        try:
            t = text.strip()[:1500]
            real_h = "This text describes factual news."
            fake_h = "This text describes fake or misleading news."

            inp_real = nli_tokenizer(t, real_h, return_tensors="pt", truncation=True)
            out_real = nli_model(**inp_real)
            prob_real = F.softmax(out_real.logits, dim=1)[0][2].item()

            inp_fake = nli_tokenizer(t, fake_h, return_tensors="pt", truncation=True)
            out_fake = nli_model(**inp_fake)
            prob_fake = F.softmax(out_fake.logits, dim=1)[0][2].item()

            total = prob_real + prob_fake
            if total <= 0:
                return heuristic_fake_detection(text)
            real_p = prob_real / total
            fake_p = prob_fake / total
            label = "REAL NEWS ✔️" if real_p > fake_p else "FAKE NEWS ❌"
            return {"label": label, "real_prob": float(real_p), "fake_prob": float(fake_p)}
        except Exception:
            return heuristic_fake_detection(text)
    else:
        return heuristic_fake_detection(text)

def analyze_sentiment(text: str) -> Dict:
    try:
        if TRANSFORMERS_AVAILABLE:
            out = sentiment_analyzer(text[:400])
            if isinstance(out, list) and out:
                item = out[0]
                return {"label": item.get("label"), "score": float(item.get("score", 0.0))}
        return {"label":"UNKNOWN","score":0.0}
    except Exception:
        return {"label":"UNKNOWN","score":0.0}

def analyze_emotion(text: str) -> Dict:
    try:
        if TRANSFORMERS_AVAILABLE:
            out = emotion_analyzer(text[:400])
            if isinstance(out, dict):
                out = [out]
            out = sorted(out, key=lambda x: x.get("score",0.0), reverse=True)
            top = out[0]
            scores = {d.get("label"): float(d.get("score",0.0)) for d in out}
            return {"top_emotion": top.get("label"), "scores": scores}
        return {"top_emotion":"neutral","scores":{}}
    except Exception:
        return {"top_emotion":"neutral","scores":{}}

TOPIC_LABELS = ["politics","technology","sports","health","finance","science","entertainment","world news","crime","education"]
def classify_topics(text: str) -> Dict:
    try:
        if TRANSFORMERS_AVAILABLE:
            out = topic_classifier(text[:400], TOPIC_LABELS)
            labels = out.get("labels",[]) if isinstance(out, dict) else []
            scores = out.get("scores",[]) if isinstance(out, dict) else []
            return {"top_topic": labels[0] if labels else "unknown", "scores": list(zip(labels, scores))}
        return {"top_topic":"unknown","scores":[(t,0.0) for t in TOPIC_LABELS]}
    except Exception:
        return {"top_topic":"unknown","scores":[(t,0.0) for t in TOPIC_LABELS]}

def extract_keywords(text: str, top_n:int=8):
    try:
        if kw_model:
            kws = kw_model.extract_keywords(text, top_n=top_n)
            return [k[0] for k in kws]
    except Exception:
        pass
    # fallback: simple frequent words
    tokens = [w.strip(".,()\"'") for w in text.split() if len(w)>4]
    seen=[]
    for t in tokens:
        if t.lower() not in seen:
            seen.append(t.lower())
        if len(seen)>=top_n:
            break
    return seen

def analyze_article(text: str) -> Dict:
    text = (text or "").strip()
    if not text:
        return {
            "summary": "",
            "fake": {"label":"UNKNOWN","real_prob":0.0,"fake_prob":0.0},
            "sentiment": {"label":"UNKNOWN","score":0.0},
            "emotion": {"top_emotion":"neutral","scores":{}},
            "topics": {"top_topic":"unknown","scores":[]},
            "keywords": []
        }
    summary = safe = ""
    try:
        summary = safe_summarize(text) if 'safe_summarize' in globals() else safe_summarize(text)
    except Exception:
        try:
            summary = safe_summarize(text)
        except:
            summary = "Summary unavailable."
    fake = fake_detection(text)
    sentiment = analyze_sentiment(text)
    emotion = analyze_emotion(text)
    topics = classify_topics(text)
    keywords = extract_keywords(text)
    return {
        "summary": summary,
        "fake": fake,
        "sentiment": sentiment,
        "emotion": emotion,
        "topics": topics,
        "keywords": keywords
    }
