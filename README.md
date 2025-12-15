# Trace Gadgets: Context-Aware Code Slicing for Efficient Vulnerability Detection

This project implements a **Small Language Model (SLM)** based approach to detect **Stack-Based Buffer Overflows (CWE-121)** in C/C++ code. It leverages **Joern** for graph-based code slicing (extracting "gadgets") and a fine-tuned **Qwen2.5-Coder-7B** model for classification.

## 🚀 Key Features
*   **Graph-Based Slicing**: Uses Joern to extract only relevant code (Data Flow from Source -> Sink), removing noise.
*   **Context-Aware**: Automatically retrieves variable definitions (e.g., buffer sizes) even across function boundaries.
*   **Small Language Model**: optimized for efficient training on consumer GPUs (T4) using Q-LoRA.
*   **Automated Pipeline**: End-to-end Python scripts for data generation, dataset preparation, and inference.

---

## 🛠️ Prerequisites

### System Requirements
*   **OS**: Windows 10/11 (project is designed for **WSL 2** integration).
*   **WSL Distro**: Ubuntu 20.04 or later.
*   **Java**: JDK 11 or later (required for Joern).
*   **Python**: 3.8+ (Windows side).

### Software Tools
1.  **Joern**: Must be installed inside your WSL environment.
    *   Installation: `curl -L "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" | bash`
    *   Ensure `joern` command is accessible in WSL path.
2.  **Linux Utilities**: `indent` (for code formatting inside WSL).
    *   `sudo apt-get install indent`

---

## 📂 Installation

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd <project-folder>
    ```

2.  **Download Juliet Test Suite**:
    *   This project uses the specific **CWE-121** test cases.
    *   Clone or download: [NIST Juliet Test Suite v1.3 for C/C++](https://samate.nist.gov/SRD/testsuite.php)
    *   Place it in: `juliet-test-suite-c/`

3.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Project Structure**:
    ```text
    Project_Root/
    ├── automation/                  # Python & Scala scripts
    │   ├── generate_training_data.py # Phase 1: Raw Extraction
    │   ├── prepare_dataset.py       # Phase 2: Sanitization & Splitting
    │   ├── generate_inference_data.py # Phase 3: Inference Prep
    │   ├── query_gadgets.sc         # Joern Taint Analysis Query (Scala)
    │   ├── colab_training.ipynb     # Jupyter Notebook for Training
    │   └── ... (utils, config, etc)
    ├── juliet-test-suite-c/         # Vulnerability Dataset
    ├── gadgets_results/             # Output of raw extraction
    ├── dataset/                     # Final ML-ready datasets (jsonl)
    └── README.md
    ```

---

## 🔬 Usage Guide

### Phase 1: Data Generation (Extraction)
Run the extraction script on the Juliet Test Suite to generate "gadgets". This script invokes Joern in WSL automatically.

```powershell
python automation/generate_training_data.py juliet-test-suite-c/testcases/CWE121_Stack_Based_Buffer_Overflow/s01
```
*Output*: `gadgets_results/gadgets_s01.jsonl`

### Phase 2: Dataset Preparation
Once you have extracted gadgets from multiple subdirectories, combine and sanitize them.

```powershell
python automation/prepare_dataset.py
```
*   **What it does**:
    *   Consolidates all `.jsonl` files in `gadgets_results/`.
    *   **Sanitizes** code (masks variable names like `dataBadBuffer` to prevent cheating).
    *   **Deduplicates** logic (removes identical test cases).
    *   Splits into `train.jsonl` (80%), `val.jsonl` (10%), `test.jsonl` (10%).
*Output*: `dataset/train.jsonl`, `dataset/test.jsonl`

### Phase 3: Model Training (Google Colab)
We use Google Colab for GPU training.

1.  Upload `automation/colab_training.ipynb` to Google Colab.
2.  Upload your generated `dataset/train.jsonl` and `dataset/test.jsonl` to the Colab runtime.
3.  **Run All Cells**: The notebook handles:
    *   Installing `unsloth`, `transformers`, `trl`.
    *   Loading Qwen2.5-Coder-7B.
    *   Fine-Tuning with LoRA.
    *   Saving the model adapters.

### Phase 4: Inference (Detection)
to test the model on a new, unknown C file:

1.  **Generate Inference Data**:
    ```powershell
    python automation/generate_inference_data.py path/to/my_code.c
    ```
    *Output*: `inference_ready.jsonl` (contains the sliced gadget + instructions).

2.  **Get Verdict**:
    *   Load your trained model (in Colab or local GPU environment).
    *   Run prediction on `inference_ready.jsonl`.
    *   Model output **"Vulnerable"** or **"Safe"** determines the result.

---