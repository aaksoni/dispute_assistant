# AI-Powered Dispute Assistant

A comprehensive system for classifying payment disputes and suggesting appropriate resolutions using machine learning and rule-based approaches.

## Project Overview

This project provides reconciliation and settlement services for fintechs and banks by building an AI assistant that helps resolve payment disputes raised by customers (e.g., failed payments, chargebacks, duplicate transactions, missing credits).

### Key Features

- **(Task 1) Dispute Classification**: Automatically categorizes disputes into 5 categories using hybrid approach (rule based + semantic + fuzzy matching)
- **(Task 2) Resolution Suggestion**:Rule based recommendations for dispute resolution
- **(Task 3) Intelligent Query Processing**: GPT-4 powered natural language to pandas query conversion
- **(Bonus) Interactive Web Interface**: Streamlit app for easy querying and visualization
## Project Structure

```
dispute_assistant/
├── README.md
├── requirements.txt
├── classified_disputes.csv        # Output from Task 1
├── resolutions.csv               # Output from Task 2
├── disputes.csv                  # Input dispute data
├── transactions.csv              # Transaction data for validation
├── constants.py                  # API keys and configuration
├── dispute_assistant.log         # Application logs
├── T1_Dispute_classification.ipynb  # Task 1 implementation
├── T2_Resolution_Suggestion.ipynb  # Task 2 implementation
├── Task3.py                      # GPT-4 powered query processor (core)
├── T3_streamlit_app.py           # Streamlit web interface for Task 3
├── task1_dispute_trends.png      # Visualization output
└──  task2_resolution_trends.png   # Visualization output
```

## Requirements and Dependencies

### Python Dependencies

Install all required packages using:

```bash
pip install -r requirements.txt
```

Key dependencies include:
- `pandas>=2.3.2` - Data manipulation
- `streamlit` - Web interface for Task 3
- `plotly` - Interactive visualizations
- `openai` - GPT-4 API integration
- `python-dotenv` - Environment variable management
- `transformers>=4.56.0` - Hugging Face models (for Task 1)
- `sentence-transformers>=5.1.0` - Semantic embeddings (for Task 1)
- `scikit-learn>=1.7.1` - ML utilities
- `matplotlib>=3.10.6` - Plotting
- `seaborn>=0.13.2` - Statistical visualizations
- `fuzzywuzzy>=0.18.0` - Fuzzy string matching
- `jupyter>=1.0.0` - Notebook environment

## Setup Instructions

### 1. Environment Setup

```bash
# Clone or download the project
cd /path/to/dispute_assistant

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root with your API credentials:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL= you_base_url # Optional: custom base URL
```

### 3. Data Preparation
- `disputes.csv` - Contains dispute records
- `transactions.csv` - Contains transaction data for validation

## Task Implementation

### Task 1: Dispute Classification

**File**: `T1_Dispute_classification.ipynb`

#### Approach
Implemented a **hybrid classification system** combining:
1. **Rule-based classification** (40% weight) - Keyword matching with fuzzy logic
2. **Semantic similarity** (60% weight) - Using sentence-transformers for vector embeddings

#### Categories
- DUPLICATE_CHARGE
- FAILED_TRANSACTION  
- FRAUD
- REFUND_PENDING
- OTHERS

#### Execution Steps

```bash
# Open Jupyter notebook
jupyter notebook T1_Dispute_classification.ipynb

# Run all cells to:
# 1. Load dispute and transaction data
# 2. Apply hybrid classification
# 3. Validate against transaction status
# 4. Generate classified_disputes.csv
# 5. Create visualization plots
```

**Expected Output**:
- `classified_disputes.csv` with columns: dispute_id, predicted_category, confidence, explanation
- `task1_dispute_trends.png` - Classification visualization

<img width="4362" height="2955" alt="task1_dispute_trends" src="https://github.com/user-attachments/assets/58dadf3c-db86-45f6-bb30-c2c31d366315" />


### Task 2: Resolution Suggestion

**File**: `T2_Resolution_Suggestion.ipynb`

#### Resolution Actions
- **Auto-refund**: Low-risk, high-confidence cases
- **Manual review**: Moderate amounts requiring verification
- **Escalate to bank**: High-value fraud cases (≥5000)
- **Mark as potential fraud**: High-confidence fraud detection
- **Ask for more info**: Unclear or low-confidence cases

#### Execution Steps

```bash
# Open Jupyter notebook
jupyter notebook T2_Resolution_Suggestion.ipynb

# Run all cells to:
# 1. Load classified disputes
# 2. Apply business rules for resolution
# 3. Generate resolutions.csv
# 4. Create resolution trend visualizations
```

**Expected Output**:
- `resolutions.csv` with columns: dispute_id, suggested_action, justification
- `task2_resolution_trends.png` - Resolution action distribution

<img width="4732" height="3540" alt="task2_resolution_trends" src="https://github.com/user-attachments/assets/41b39374-3d92-449a-add4-4c5fb8c8ff0a" />


### Task 3: Intelligent Query Processing

**Files**: 
- `Task3.py` - Core GPT-4 powered query processor
- `T3_streamlit_app.py` - Web interface for interactive queries

#### Features
- **Dual Interface**: Both CLI/programmatic and web-based interfaces
- **GPT-4 Integration**: Uses OpenAI's GPT-4 for natural language to pandas query conversion
- **Query Execution**: pandas query execution
- **Real-time Processing**: Live query processing with code generation display

#### Architecture
- `DisputeAnalyzer` class in `Task3.py` handles core query processing
- `T3_streamlit_app.py` provides web interface using the analyzer
- Automatic data loading and merging from all CSV files
- Dynamic system prompt generation based on actual data schema
- Intelligent pandas code extraction and validation

#### Execution Options

**Option 1: Streamlit Web Interface (Recommended)**
```bash
# Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Run the Streamlit web interface
streamlit run T3_streamlit_app.py

# Access at: http://localhost:8501
```
<img width="987" height="589" alt="Screenshot 2025-09-02 at 3 03 58 PM" src="https://github.com/user-attachments/assets/e35ebdb2-a614-4da2-9440-c2ebf6b9611f" />


**Option 2: CLI/Programmatic Interface**
```bash
# Run the core analyzer directly
python Task3.py

# Or import and use in your code
from Task3 import DisputeAnalyzer
analyzer = DisputeAnalyzer()
response = analyzer.process_query("How many fraud disputes today?")
```

#### Supported Query Examples
The system intelligently converts natural language to pandas operations:

- "How many duplicate charges on 2nd august 2025?" 
- "List unresolved fraud disputes"
- "Break down disputes by type"
- "Count all disputes"
- "Show fraud disputes"
- "What are the high confidence disputes?"
- "Show me manual review cases"

#### Query Processing Flow
1. **Natural Language Input**: User provides query via web interface or CLI
2. **Schema-Aware Prompt**: System creates context-aware prompt with data schema
3. **GPT-4 Generation**: AI generates appropriate pandas code
4. **Code Display**: Generated code is shown to user for transparency
5. **Execution**: Code is executed 
6. **Results**: Results are displayed in tables

## Usage Examples

### Example Query Processing

**Web Interface Usage:**
```bash
# Start the Streamlit app
streamlit run T3_streamlit_app.py

# Use the web interface to:
# 1. Select example queries from sidebar
# 2. Enter custom natural language queries
# 3. View generated pandas code
# 4. See interactive results
```
<img width="766" height="531" alt="Screenshot 2025-09-02 at 3 13 48 PM" src="https://github.com/user-attachments/assets/01e86aef-2eaa-4046-921b-6409ca4a4c20" />


**Programmatic Usage:**
```python
# Initialize the analyzer
analyzer = DisputeAnalyzer()

# Process various queries
queries = [
    "How many duplicate charges on 2nd august 2025?",
    "List unresolved fraud disputes", 
    "Break down disputes by type",
    "Count all disputes",
    "Show fraud disputes"
]

for query in queries:
    response = analyzer.process_query(query)
    print(f"Query: {query}")
    print(f"Generated Code: {response['generated_code']}")
    print(f"Result: {response['result']}")
```
## Assignment Completion Status

### Core Requirements ✅
- [x] Task 1: Dispute classification with 5 categories
- [x] Task 2: Resolution suggestions with business rules  
- [x] Task 3: Interactive query interface with Streamlit web app + GPT-4 backend
- [x] Output files: classified_disputes.csv, resolutions.csv

### Bonus Features ✅
- [x] Fuzzy matching for duplicate detection
- [x] Dispute trend visualizations
- [x] Transaction validation logic
- [x] Streamlit web interface 
- [x] Advanced NLP query processing (GPT-4)
- [x] LLM integration using OpenAI API
