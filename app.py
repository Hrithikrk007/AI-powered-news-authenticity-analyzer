# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from nlp_engine import analyze_article
from file_utils import allowed_file, save_upload, extract_text
from url_utils import extract_text_from_url
from search_utils import google_fact_check
from database import init_db, save_analysis, get_all_history

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "devsecretkey")
app.config['MAX_CONTENT_LENGTH'] = 30 * 1024 * 1024  # 30 MB

# Ensure DB exists
init_db()


def render_index(**kwargs):
    """Helper to always provide app_name to templates"""
    kwargs.setdefault("app_name", "AI-Powered News Authenticity Analyzer")
    return render_template("index.html", **kwargs)


@app.route("/")
def home():
    return render_index()


@app.route("/analyze_text", methods=["POST"])
def analyze_text_route():
    text = request.form.get("news", "") or ""
    if not text.strip():
        flash("Please enter text to analyze.")
        return redirect(url_for("home"))

    try:
        results = analyze_article(text)
        # small claim for fact-check
        fact_check = google_fact_check(text[:200])
        save_analysis("TEXT", (text[:180] + "..."), results)
        return render_index(results=results, fact_check=fact_check, article_text=text)
    except Exception as e:
        app.logger.exception("analyze_text failed")
        flash("Internal error during analysis. See console.")
        return redirect(url_for("home"))


@app.route("/analyze_url", methods=["POST"])
def analyze_url_route():
    url = request.form.get("url", "") or ""
    if not url.strip():
        flash("Please enter a URL.")
        return redirect(url_for("home"))

    try:
        extracted = extract_text_from_url(url)
        if not extracted or len(extracted.split()) < 20:
            flash("Could not extract enough text from the URL.")
            return redirect(url_for("home"))

        results = analyze_article(extracted)
        fact_check = google_fact_check(extracted[:200])
        save_analysis("URL", url, results)
        return render_index(results=results, fact_check=fact_check, article_text=extracted, article_url=url)
    except Exception:
        app.logger.exception("analyze_url failed")
        flash("Internal error during URL analysis.")
        return redirect(url_for("home"))


@app.route("/upload_file", methods=["POST"])
def upload_file_route():
    f = request.files.get("file")
    if not f or f.filename == "":
        flash("No file selected.")
        return redirect(url_for("home"))

    if not allowed_file(f.filename):
        flash("Unsupported file type. Use PDF / DOCX / TXT.")
        return redirect(url_for("home"))

    try:
        path = save_upload(f)
        text, ext = extract_text(path)
        if not text or len(text.split()) < 20:
            flash("Could not extract readable text from the uploaded file.")
            return redirect(url_for("home"))

        results = analyze_article(text)
        fact_check = google_fact_check(text[:200])
        save_analysis(f"FILE ({ext})", f.filename, results)
        return render_index(results=results, fact_check=fact_check, article_text=text, uploaded_filename=f.filename)
    except Exception:
        app.logger.exception("upload_file failed")
        flash("Internal error handling uploaded file.")
        return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    try:
        history = get_all_history()
        return render_template("dashboard.html", history=history, app_name="AI-Powered News Authenticity Analyzer")
    except Exception:
        app.logger.exception("dashboard failed")
        flash("Could not load dashboard.")
        return redirect(url_for("home"))


if __name__ == "__main__":
    print("Starting AI-Powered News Authenticity Analyzer on http://127.0.0.1:5000")
    app.run(debug=True)
