# Mini RAG – Construction Marketplace AI

# Assistant

## Overview

This project implements a Retrieval Augmented Generation (RAG) pipeline for a construction
marketplace AI assistant. The system answers user questions strictly using internal
documents such as policies, FAQs, and specification sheets, rather than relying on the
language model’s general knowledge.
The goal of this project is to ensure that responses are grounded, transparent, and reliable,
making the assistant suitable for both customer facing and internal support use cases.

## Repository Structure

```text
mini-rag/
│
├── data/
│   ├── doc1.md
│   ├── doc2.md
│   ├── doc3.md
│
├── rag.py
├── requirements.txt
└── README.md
```


## How to Run the Project Locally

### Prerequisites

The project requires Python 3.9 or higher and Ollama installed on the local machine. Ollama
is used to serve the local language model.
Ollama can be installed from:
https://ollama.com/


### Install Dependencies

Install all required Python packages using:
pip install -r requirements.txt

### Pull the Local LLM (One-Time Setup)

The system uses a local open source LLM served through Ollama. Pull the model once
using:
ollama pull phi3:mini
Ensure Ollama is running in the background:
ollama run phi3:mini

### Run the RAG System

Execute the main script:
python rag.py
When run, the script retrieves relevant document chunks, displays the retrieved context, and

## generates a grounded answer based only on that context.

### Choosing Embedding Models

The system applies the all MiniLM-L6-v2 model from the Sentence Transformers library for
the generation of semantic embeddings.
This model is chosen for its open source nature, light architecture, and popularity as a robust
baseline method for semantic search problems. It generates excellent semantic embeddings
and is CPU friendly and computationally efficient, so it is well suited for internal policy and
specification documents. Additionally, all the vectors are normalized, and an inner product
search based on cosine similarity is supported.


## Language Model Selection

In answering questions, the system relies on phi3:mini through Ollama.
This particular model is completely open source and works locally without depending on paid
APIs or external systems whatsoever. It follows instructions accurately and has been
observed to have less hallucination rates than larger models, this is highly desirable for a
grounded RAG model system like Ollama. By using Ollama, it ensures that the system is
always cost free and offline friendly and allows for reproducibility.

### Document Chunking

internal files are stored in Markdown format, which undergoes paragraph level chunking. The
files are chunked based on blank lines, and this ensures that every chunk has a sufficient
context. Fragments that are too small are removed for reduction of noise while retrieving.
The reason for choosing paragraph level chunking is that it has natural segmentation points
in these documents, which will allow for semantic completeness while improving relevance in
document retrieval. These chunks are stored with additional metadata, including file name
and chunk identifier.

### Vector Search and Retrieval

All the chunks of the documents are embedded and indexed using FAISS with an inner
product index. As the embeddings are normalized, the inner product similarity is a cosine
similarity search.
For a user query, the query itself is represented as an embedding using the same model,
and this is contrasted with the document embeddings in the indexed repository. The system
identifies the top k most semantically similar chunks, which are used as the context for
answering within the language model.

### Grounding and Hallucination Control

Grounding is strictly enforced through the usage of strong constraints on the considered
prompts. The language model is directly told to respond only within the limits of the retrieved
document context and not use any additional information. When the needed information is
not within the retrieved pieces of text, the model is told to say:


“Unfortunately, I do not possess adequate information under the available documents.”
In order to make transparency and explainability possible, it is necessary for the system to
print out pieces of the document that have been retrieved before it proceeds to show the
final result.

### Quality Analysis (Summary)

The system was tested for quality using relevant questions formulated from the internal
sources.
**Retrieval relevance:**
Highly ranked segments were invariably relevant, with similarity values ranging roughly from
0.45 to 0.80.
**Groundedness:**
Answers were consistent to the retrieved information without any critical hallucinations.
**Out of scope handling:**
In the unsupported queries, the system properly refused to respond.
**Answer quality:**
Feedback was direct, to the point, and consistent with documentation terminology.

### Example:

QUERY: What post-construction maintenance support is offered?
Retrieved Context:
[1] Source: doc3.md | Score: 0.
## 4) Maintenance Program (Post-Construction Support)
### Zero Cost Maintenance Program (Coverage Themes)


The brochure describes a “zero cost maintenance” program intended to keep the home in
good condition post-handover.
[2] Source: doc1.md | Score: 0.
10) Maintenance

- Post-handover maintenance support as part of Indecimal’s long-term care positioning.
[3] Source: doc1.md | Score: 0.
## 3) What We Strive For (Operating Principles)
1. Smooth Construction Experience
- Step-by-step support throughout the project.
2. Best and Competitive Pricing
- Fair pricing with no hidden charges.
3. Quality Assurance (445+ checks)
- Strict quality control at every construction stage.
4. Stage-Based Contractor Payments
- Payments released only after verified completion.
5. Transparent and Live Tracking
- Clear agreements and real-time online project monitoring.
Final Answer:
The brochure describes a "zero cost maintenance" program intended to keep the home in
good condition after handover, as part of Indecimal’selong-term care positioning. This
includes step-by-step post-handover construction support and stage-based contractor
payments released only upon verified completion for quality assurance purposes.



