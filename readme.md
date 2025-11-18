AI-Powered News Authenticity Analyzer: Project Structure

======================================================



This is a full-stack machine learning application for news verification, organized into four primary layers: Core Application, Machine Learning, Data Storage, and Presentation.



---



I. Core Application Layer (Backend)

----------------------------------

The core logic is built with Python and Flask.



| Sub-System           | Description                                                 | Key Technologies        |

|----------------------|-------------------------------------------------------------|-------------------------|

| Data Ingestion       | Handles input processing (text, URL, files).                | Flask, PyPDF2, python-docx |

| NLP Pipeline         | Executes all text analysis tasks sequentially.              | Python, HuggingFace Transformers |

| Fact-Checking Module | Interfaces with Google for external verification.           | Google Search API       |

| Database Manager     | Manages storing and retrieving analysis history.            | SQLite3                 |

| API Endpoints        | Defines the routes for front-end/back-end communication.    | Flask                   |



---



II. Machine Learning Models

---------------------------

Specialized models for deep textual analysis.



| Analysis Feature      | Model/Library               | Core Function                       |

|-----------------------|-----------------------------|-------------------------------------|

| Fake News Detection   | RoBERTa Large MNLI          | Natural Language Inference (NLI) for probability. |

| Summarization         | Transformer-based models    | Condensing articles into key points. |

| Sentiment/Emotion     | State-of-the-art NLP models | Identifying tone and dominant feelings. |

| Topic/Keyword         | Specialized NLP models      | Extracting meaningful keywords and classifying topics. |



---



III. Data and Storage Layer

---------------------------

Managing internal records and external data sources.



| Data Type             | Storage/Source                      | Purpose                             |

|-----------------------|-------------------------------------|-------------------------------------|

| Analysis History      | SQLite3 Database                    | Storing past analysis summaries and predictions. |

| External References   | Google Programmable Search Engine   | Fact-checking and claims verification. |

| Input Documents       | Local File System (Temporary)       | Handling uploaded files (PDF, DOCX, TXT). |



---



IV. Presentation Layer (Frontend)

---------------------------------

The user interface for interaction and visualization.



| Component             | Technology                  | Key Features                        |

|-----------------------|-----------------------------|-------------------------------------|

| Styling/Design        | TailwindCSS                 | Utility-first CSS for responsive, modern look. |

| User Interface        | Custom HTML/JS/CSS          | Clean dashboard, auto dark-mode toggle. |

| Dashboard View        | Custom HTML/JS/CSS          | Visualization of analysis results.    |

| History View          | Custom HTML/JS/CSS          | Displaying and managing stored analysis records. |

