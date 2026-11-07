# Telecom Troubleshooter

A small AI agent that answers telecom questions by combining **document search (RAG)** with **calculator tools**. Ask why indoor 5G coverage is weak and it retrieves the relevant theory from the documents; ask for a path-loss figure and it calls a tool to compute it.

## How it works

1. **Load and chunk:** `.txt` and `.pdf` files in `docs/` are split into overlapping chunks, with source and page metadata. Table-of-contents chunks are filtered out.
2. **Embed:** chunks are embedded locally with `sentence-transformers/all-MiniLM-L6-v2`, so there are no embedding rate limits.
3. **Search:** an in-memory vector store returns the top matching chunks for a question. The index is cached in `store.json`.
4. **Agent loop:** Gemini decides whether to search the documents or call a tool, the code runs the tool, and the result goes back to the model until it can answer.

### Tools

| Tool | What it does |
|---|---|
| `search_telecom_docs` | Retrieves relevant passages with their source |
| `dbm_to_watts` | Converts power from dBm to watts |
| `wavelength_m` | Wavelength in metres from frequency in Hz |
| `free_space_path_loss_db` | Free-space path loss from distance (km) and frequency (MHz) |

## Project structure

```
main.py        # embeddings, chunking, vector store, search
tools.py       # calculator functions
agent.py       # tool calling and the agent loop
test_tools.py  # pytest tests for the calculators
docs/          # your documents (.txt and .pdf)
```

## Setup

```
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a `.env` file containing your Gemini API key:

```
GEMINI_API_KEY=your_key_here
```

Add documents to `docs/`. For example, ITU-R P.1238 (indoor propagation) and ITU-R M.2083 (IMT-2020 vision) are free to download from itu.int. The PDFs are not included in this repo.

## Run

```
python agent.py
```

The first run downloads the embedding model (about 90 MB) and builds `store.json`. Later runs load the saved index. Delete `store.json` after changing anything in `docs/`.

## Tests

```
python -m pytest
```

## Example

```
Question: Why does 5G signal drop indoors, and what is the free-space path loss for 50 m at 3500 MHz?

[tool] search_telecom_docs {'question': 'Why does 5G signal drop indoors?'}
[tool] free_space_path_loss_db {'distance_km': 0.05, 'freq_mhz': 3500}

Answer: penetration loss and frequency effects, with sources cited. Path loss: 77.30 dB.
```

## Limitations and next steps

- The in-memory index is rebuilt from scratch whenever the documents change.
- A small local embedding model ranks results less accurately than larger ones.
- Next: a Streamlit demo, Docker, GitHub Actions running the tests, and a retrieval evaluation script.