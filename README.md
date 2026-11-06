# ConvoSniper

**A social listening and engagement automation prototype powered by NLP and machine learning.**

ConvoSniper collects public community discussions, analyzes their sentiment and engagement, identifies potentially notable posts, and generates context-aware response drafts. The prototype integrates Reddit and Discord data sources, a DistilBERT-based sentiment classifier, engagement-based anomaly detection, MongoDB persistence, and a Flask dashboard.

> **Project status:** Academic / experimental prototype. The repository contains platform-specific integrations and automation code, but the current implementation needs credential management, path configuration, dependency updates, and end-to-end testing before deployment. Generated responses should be reviewed by a human before being posted.

## Highlights

- **Multi-platform ingestion:** Collects recent submissions and comment activity from Reddit and messages/reactions from Discord.
- **Sentiment classification:** Uses a locally stored fine-tuned DistilBERT sequence-classification model to label text as Positive, Neutral, or Negative.
- **Conversation-aware analysis:** For Reddit submissions, analyzes comments and incorporates child-comment sentiment into the parent discussion's score.
- **Trend / outlier detection:** Uses engagement signals and sentiment scores with scikit-learn's `IsolationForest` to flag unusual posts.
- **Persistent storage:** Uses Redis as an ingestion cache and MongoDB to store analyzed social posts and generated responses.
- **Response generation:** Includes a fine-tuned GPT-2 response-generation component conditioned on post text and sentiment.
- **Platform integration:** Includes Reddit and Discord response-injection modules.
- **Dashboard and visualizations:** Provides a Flask interface and scripts for engagement charts.

## Architecture

```text
                  ┌──────────────────┐
                  │  Reddit stream   │
                  └────────┬─────────┘
                           │
                  ┌────────▼─────────┐
                  │                  │
                  │   Redis cache    │◄──────── Discord messages
                  │                  │
                  └────────┬─────────┘
                           │
                  ┌────────▼─────────┐
                  │ Sentiment engine │
                  │   DistilBERT     │
                  └────────┬─────────┘
                           │
              ┌────────────▼────────────┐
              │ Engagement / outlier    │
              │ detection (Isolation    │
              │ Forest)                 │
              └────────────┬────────────┘
                           │
                  ┌────────▼─────────┐
                  │     MongoDB      │
                  │ analyzed posts   │
                  └────────┬─────────┘
                           │
                  ┌────────▼─────────┐
                  │ Post retrieval & │
                  │ GPT-2 generation │
                  └────────┬─────────┘
                           │
                  ┌────────▼─────────┐
                  │ Response storage│
                  │ and platform    │
                  │ integration     │
                  └──────────────────┘

             Flask dashboard / chart generation
```

### Processing flow

1. `backend/redit.py` streams Reddit submissions from the configured subreddit feed and stores post/comment data in Redis.
2. `backend/discord_sniper.py` listens for recent Discord messages and reaction updates and stores them in Redis.
3. `backend/analyze_sentiment.py` polls Redis, runs DistilBERT inference, and computes sentiment labels and scores. It also uses `IsolationForest` to flag outliers in batches.
4. `backend/db.py` persists normalized analysis records in MongoDB.
5. `backend/Generate_response/retrieve.py` reads stored posts and filters candidate posts based on sentiment and engagement.
6. `backend/Generate_response/response_generator.py` loads the local GPT-2 model, generates a response, stores it in MongoDB, and invokes the platform injector.
7. `frontend/app.py` serves the Flask dashboard. `backend/visualize_engagement.py` generates chart images from MongoDB data.

`backend/x_sniper.py` contains a standalone X/Twitter recent-search example; it is not connected to the main orchestrated pipeline.

## Tech stack

| Area | Technologies |
|---|---|
| Language | Python |
| Social data collection | PRAW (Reddit), discord.py (Discord) |
| Cache / message handoff | Redis |
| Database | MongoDB, PyMongo |
| NLP / sentiment | Hugging Face Transformers, DistilBERT, PyTorch |
| Response generation | GPT-2, Hugging Face Transformers |
| Trend detection | scikit-learn Isolation Forest, NumPy |
| Dashboard | Flask, HTML, CSS, JavaScript |
| Visualization | Matplotlib, Seaborn, Pandas |

## Repository structure

```text
ConvoSniper/
├── backend/
│   ├── main.py                    # Starts the data and analysis workers
│   ├── redit.py                   # Reddit ingestion
│   ├── discord_sniper.py          # Discord ingestion
│   ├── x_sniper.py                # Standalone X/Twitter example
│   ├── analyze_sentiment.py       # DistilBERT inference and outlier detection
│   ├── analytics_engine.py        # MongoDB trend scoring
│   ├── db.py                      # MongoDB persistence
│   ├── train_bert.py              # Sentiment model training
│   ├── visualize_engagement.py    # Engagement chart generation
│   ├── Generate_response/
│   │   ├── retrieve.py            # Candidate post retrieval
│   │   ├── response_generator.py  # GPT-2 response generation
│   │   └── final_train.py         # GPT-2 fine-tuning
│   ├── inject/
│   │   ├── inject.py              # Platform routing
│   │   ├── reddit_inject.py       # Reddit posting integration
│   │   └── discord_inject.py      # Discord posting integration
│   └── reinforcement/             # Experimental feedback/retraining code
├── frontend/
│   ├── app.py                    # Flask application
│   ├── templates/                 # Dashboard pages
│   └── static/                   # CSS, JavaScript, chart images
├── conversniper_bert/             # Local DistilBERT model/tokenizer files
├── company_data_db/               # Local ChromaDB data (if used by experiments)
├── data.csv                       # Project data
└── requirements.txt
```

## Requirements

- Python 3.10 or 3.11 recommended. The pinned dependency versions in the repository are old and may require compatibility adjustments.
- Redis server
- MongoDB server
- Reddit API application credentials
- Discord bot application and permissions
- Model artifacts:
  - Fine-tuned DistilBERT directory: `conversniper_bert/`
  - Fine-tuned GPT-2 directory: `backend/Generate_response/final_model/` (not included in every repository copy)

## Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ConvoSniper
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux / macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The current `requirements.txt` pins older versions of Transformers and PyTorch. If installation fails on your Python version or hardware, update and test a compatible dependency set rather than assuming the original pins will work unchanged.

### 4. Start Redis and MongoDB

Make sure both services are running locally:

- Redis: `localhost:6379`
- MongoDB: `mongodb://localhost:27017/`

The current code uses these local connection addresses directly.

### 5. Configure API credentials

**Do not commit API keys, bot tokens, passwords, or other secrets to source control.** The uploaded project copy contains credentials embedded in source files. Revoke/rotate those credentials before using or publishing the repository, then replace hardcoded values with environment-variable configuration.

The code should be updated to read credentials from environment variables (for example, `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`, `DISCORD_BOT_TOKEN`, and `X_BEARER_TOKEN`) before running the integrations. Merely creating a `.env` file will not make the current code read it unless environment loading is implemented.

Example PowerShell session variables:

```powershell
$env:REDDIT_CLIENT_ID = "your-client-id"
$env:REDDIT_CLIENT_SECRET = "your-client-secret"
$env:REDDIT_USER_AGENT = "ConvoSniper/1.0"
$env:DISCORD_BOT_TOKEN = "your-discord-bot-token"
$env:X_BEARER_TOKEN = "your-x-bearer-token"
```

Also review the Reddit posting module and all injector code before enabling automated posting. Use a test subreddit/server and human approval during development.

### 6. Verify model paths

The sentiment analyzer currently loads the DistilBERT model from a machine-specific absolute Windows path. Change it to a path relative to the repository or configure it through an environment variable.

The response generator expects a fine-tuned GPT-2 model under:

```text
backend/Generate_response/final_model/
```

Ensure that model directory exists and contains the required model and tokenizer files. The training script also contains a machine-specific dataset path that must be changed before training.

## Running

The following commands describe the intended entry points. Run only after credentials, model paths, dependencies, and external services have been configured.

### Start the backend pipeline

From the repository root:

```bash
python -m backend.main
```

The orchestrator is intended to start Reddit ingestion, Discord ingestion, analytics, response generation, and sentiment analysis workers.

### Start the Flask dashboard

In a separate terminal:

```bash
python -m frontend.app
```

Then open:

```text
http://127.0.0.1:5001
```

### Generate engagement visualizations

```bash
python -m backend.visualize_engagement
```

The visualizer currently saves chart files to a relative `static/` directory. Confirm that this resolves to the frontend's static directory, or update the output path to `frontend/static/` before running it.

## Model training

### DistilBERT sentiment classifier

Training script:

```bash
python -m backend.train_bert
```

The script expects a CSV containing:

| Column | Description |
|---|---|
| `text` | Input post/comment text |
| `sentiment` | One of `Positive`, `Neutral`, or `Negative` |

The script maps sentiment labels to class IDs and fine-tunes DistilBERT for sequence classification. Update the dataset and output paths in the script before execution.

### GPT-2 response generator

Training script:

```bash
python -m backend.Generate_response.final_train
```

The training data is expected to contain:

| Column | Description |
|---|---|
| `Post` | Original social-media post |
| `Response` | Example response |

The script fine-tunes GPT-2 on post/response pairs. Update the CSV path and model output path before training.

## Limitations and known implementation gaps

This repository is a prototype, not a production-ready autonomous engagement platform. In particular:

- API credentials and machine-specific paths are hardcoded in parts of the current source and must be removed.
- Some modules use different data schemas and storage paths; validate the complete pipeline with test data.
- The main orchestrator assumes Redis, MongoDB, and both platform integrations are available.
- The response-generation component expects a local fine-tuned GPT-2 artifact that may not be present in the repository.
- The current response flow can post generated content directly through injectors. Human review, rate limits, duplicate prevention, and platform-policy checks should be added before enabling this behavior.
- The analytics engine uses a simple engagement-weighted score; it should not be interpreted as a validated measure of virality.
- `IsolationForest` flags statistical outliers, which are not automatically meaningful trends.
- The Flask frontend includes simulated loading behavior and should be treated as a lightweight prototype UI.
- X/Twitter collection is a standalone script and is not part of the main pipeline.

## Responsible use

- Respect Reddit, Discord, and other platform terms, API policies, rate limits, and community rules.
- Collect and process only data you are authorized to access.
- Avoid storing unnecessary personal information.
- Do not automatically publish model-generated replies without review.
- Provide a clear way to stop collection and posting workers.

## Future improvements

- Centralize configuration with environment variables and a validated settings module.
- Add structured logging, retries, graceful shutdown, and worker health checks.
- Add a human-in-the-loop approval queue before response injection.
- Evaluate sentiment classification with precision, recall, F1-score, and a held-out dataset.
- Evaluate generated responses for relevance, factuality, tone, and safety.
- Add tests for ingestion, schema validation, retrieval, sentiment inference, and platform integrations.
- Containerize Redis, MongoDB, backend workers, and the dashboard with Docker Compose.
- Replace hardcoded local paths with repository-relative configuration.

## License

Add a license before distributing or accepting external contributions. Until a license is included, all rights remain with the copyright holder.
