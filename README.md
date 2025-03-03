# Ollama GGUF Downloader

A Python utility to download GGUF model files directly from the Ollama library without installing Ollama.

## Overview

GGUF is the model format required by tools based on llama.cpp.
This utility allows you to:

- Browse and download models from Ollama's library directly in GGUF format
- Download models without needing to install Ollama
- Get properly formatted files ready to use with llama.cpp-based tools

## Installation

```bash
# Clone the repository
git clone https://github.com/iven86/ollama_gguf_downloader.git

# Navigate to the directory
cd ollama-gguf-downloader

# Install dependencies
pip install -r requirements.txt
```

## Usage

Simply run the script and follow the prompts:

```bash
python ollama_gguf_downloader.py
```

The script will:
1. Ask for a model name (e.g., 'phi3')
2. Ask for model parameters (e.g., '3.8b')
3. Fetch the model information from Ollama
4. Prompt for a filename (or use the default)
5. Download the GGUF file with progress tracking

## Example

```
$ python ollama_gguf_downloader.py

  _____       _                           _   _  __ _
 / ____|     | |                         | | | |/ _| |
| |  __  ___ | |_   _ __ ___   __ _ _ __ | |_| | |_| | _____  __
| | |_ |/ _ \| | | | | '_ ` _ \ / _` | '_ \| __| |  _| |/ _ \ \/ /
| |__| | (_) | | |_| | | | | | | (_| | | | | |_| | | | |  __/>  <
 \_____|\___/|_|\__, |_| |_| |_|\__,_|_| |_|\__|_|_| |_|\___/_/\_\
                 __/ |
                |___/

Welcome to the Ollama GGUF Model Downloader!
This script helps you download models directly from the Ollama library in GGUF format.

You'll need to provide:
- Model name (e.g., 'phi3')
- Model parameters (e.g., '3.8b')

Let's get started!

Enter the model name (e.g., 'phi3'): phi3
Enter the model parameters (e.g., '3.8b'): 3.8b

🛠  Fetching model information...
✅ Successfully retrieved model digest: 3e38718d00bb...

📝 Enter output filename (default: phi3-3.8b-Q4_0.gguf):

⬇️  Starting download...
Downloaded: 1560.23 MB / 1560.23 MB (100.0%)

🎉 All done! Happy AI experimenting!
You can now use this model with llama.cpp based tools like koboldcpp.
```

## Available Models

You can find available models on the [Ollama Library page](https://ollama.ai/library).

## Requirements

- Python 3.6+
- requests package

## How It Works

1. The script queries the Ollama registry manifest for your specified model
2. It extracts the digest for the GGUF model file
3. It downloads the file directly from Ollama's registry blob storage

## License

GPL-3.0 License

## Credits

Created by Iven L.F.

Inspired by the article: "Downloading GGUF Models from Ollama" on [learningdeeplearning.com](https://learningdeeplearning.com)
