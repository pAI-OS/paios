# Personal Artificial Intelligence Operating System (pAI-OS) for creating an Assistant

## Getting Started

|❗ The server binds to localhost without authentication for the time being; this is a security issue that will be fixed before release to end users. You can use any username and password for the time being.|
|--|

### Users

An easy to use release is coming soon, but for now you can follow the instructions below to get started.

### Early Adopters

> 💡 **Tip:** Download and install [Python](https://www.python.org/downloads/) if you can't run it from the terminal.

Open the Terminal application.

## Setting up your backend to create an Assistant

Clone the repository

```sh
git clone https://github.com/pAI-OS/paios.git
```
Then change to the __fix/indexing-async__ branch from the repository:

```sh
git checkout -b fix/indexing-async origin/fix/indexing-async
```

Setup and run the server. This will create a virtual environment for the project:

_POSIX (Linux/macOS/etc.)_

```sh
python3 paios/scripts/setup_environment.py (only on first run)
source paios/.venv/bin/activate
```

_Windows_

```sh
python .\paios\scripts\setup_environment.py (only on first run)
.\paios\.venv\Scripts\Activate.ps1
```

Run the uvicorn server:

```sh
python -m paios
```
Example of commands execution:
```ps
PS C:\Users\annie\Documents\MyProjects> .\paios\.venv\Scripts\Activate.ps1
(.venv) PS C:\Users\annie\Documents\MyProjects> 
```
```ps
PS C:\Users\annie\Documents\MyProjects> .\paios\.venv\Scripts\Activate.ps1
(.venv) PS C:\Users\annie\Documents\MyProjects> python -m paios
INFO:     Creating the app.
INFO:     Initializing database.
INFO:     Context impl SQLiteImpl.
INFO:     Will assume non-transactional DDL.
INFO:     Running the app with uvicorn.
INFO:     Will watch for changes in these directories: ['C:\\Users\\annie\\Documents\\MyProjects\\paios\\backend']
INFO:     Uvicorn running on http://localhost:3080 (Press CTRL+C to quit)
INFO:     Started reloader process [31592] using WatchFiles
INFO:     Initializing database.
INFO:     Context impl SQLiteImpl.
INFO:     Will assume non-transactional DDL.
INFO:     Started server process [14492]
INFO:     Waiting for application startup.
C:\Users\annie\Documents\MyProjects\paios\.venv\Lib\site-packages\pydantic\_internal\_config.py:341: UserWarning: Valid config keys have changed in V2:
* 'orm_mode' has been renamed to 'from_attributes'
  warnings.warn(message, UserWarning)
INFO:     Application startup complete.
```

To visit [http://localhost:3080/](http://localhost:3080/)


If you want to explore the API Docs visit [http://localhost:3080/api/v1/ui/](http://localhost:3080/api/v1/ui/)

### Setting up the ```.env``` file

1. Create a ```.env``` file
    In the root directory of your project, create a new file named ```.env```   

2. Add your environment variables    
    Open the ```.env``` file in a text editor and add the required environment variables. Each variable should be on a new line in the format:

Example of ```.env```:

```
CHUNK_SIZE=10000
CHUNK_OVERLAP=200
ADD_START_INDEX=True
MAX_TOKENS=1000000
SYSTEM_PROMPT="You are an assistant for question-answering tasks.Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know."
TEMPERATURE=0.2
EMBEDDER_MODEL="llama3:latest"
XI_API_KEY="sk_******" 
XI_CHUNK_SIZE=1024
TOP_K=10
TOP_P=0.5
```
__TEMPERATURE__: 
The temperature of the model. Increasing the temperature will make the model answer more creatively. (Default: 0.8)

__TOP_K__: Reduces the probability of generating nonsense. A higher value (e.g. 100) will give more diverse answers, while a lower value (e.g. 10) will be more conservative.

__TOP_P__: Works together with top-k. A higher value (e.g., 0.95) will lead to more diverse text, while a lower value (e.g., 0.5) will generate more focused and conservative text. (Default: 0.9)

__CHUNK_SIZE__: The maximum size of a chunk.
__CHUNK_OVERLAP__: Target overlap between chunks. Overlapping chunks helps to mitigate loss of information when context is divided between chunks.

__ADD_START_INDEX__: We set add_start_index=True so that the character index at which each split Document starts within the initial Document is preserved as metadata attribute “start_index”.

__EMBEDDER_MODEL__: Check the final ❗ note.

__XI_CHUNK_SIZE__:Size of chunks to read/write at a time

__MAX_TOKENS__: Maximum number of tokens to predict when generating text. (Default: 128, -1 = infinite generation, -2 = fill context). Common lengths might be:

    - A maximum of 50 tokens for very concise answers
    - A maximum of 200 tokens for more substantial responses

### Instructions to Obtain an Eleven Labs API Key
Follow these steps to get an API key from Eleven Labs:
1. Create an Eleven Labs Account

    If you don't already have an account, go to [Eleven Labs](https://elevenlabs.io/app/sign-up) and sign up for a free or paid plan. You'll need an active account to access the API.

2. Log In to Your Account

    Once you have an account, log in to the Eleven Labs dashboard using your credentials.

3. Navigate to the API Section

    After logging in, go to the API section of the dashboard. You can typically find this in the main navigation or giving click on your User name and then on API Keys option.

4. Generate and copy Your API Key 

    In the API section, you'll see an option to generate or view your API key. Click the button to generate a new API key if one isn’t already created. Once generated, your API key will be displayed. Copy it and store it securely, because you will not be able to display it again.

5. Store the API Key in Your Project’s ```.env``` File
    To securely use the API key in your project, add it to your ```.env``` file like this:
    ```
    XI_API_KEY="sk_******"
    ```

### Install Ollama
In order to create an assistant, you will need to download [Ollama](https://ollama.com/download)

__macOS__

[Download](https://ollama.com/download/Ollama-darwin.zip)

__Windows preview__

[Download](https://ollama.com/download/OllamaSetup.exe)

__Linux__

```
curl -fsSL https://ollama.com/install.sh | sh
```

[Manual install instructions](https://github.com/ollama/ollama/blob/main/docs/linux.md)


After installing Ollama, Ollama will run in the background and the `ollama` command line is available in `cmd`, `powershell` or your favorite terminal application. As usual the Ollama api will be served on
`http://localhost:11434`.

You should see the message:  "_Ollama is running_"

#### Common Ollama comands

__Download a model__

```
ollama run llama3.2
```
__Pull a model__

This command can also be used to update a local model. Only the diff will be pulled.
```
ollama pull llama3.2
```

__List all the installed models__

This list contains the available models for you to choose from and set as the Large Language Model (LLM) for your Assistant.
```
ollama list
```
__Remove a model__

Keep in mind that once you delete a model from your computer, it will no longer be available for setting up with your Assistant.
```
ollama rm llama3.2
```

#### Model library

Ollama supports a list of models available on [ollama.com/library](https://ollama.com/library 'ollama model library')

Here are some example models that can be downloaded:

| Model              | Parameters | Size  | Download                       |
| ------------------ | ---------- | ----- | ------------------------------ |
| Llama 3.2          | 3B         | 2.0GB | `ollama run llama3.2`          |
| Llama 3.2          | 1B         | 1.3GB | `ollama run llama3.2:1b`       |
| Llama 3.1          | 8B         | 4.7GB | `ollama run llama3.1`          |
| Llama 3.1          | 70B        | 40GB  | `ollama run llama3.1:70b`      |
| Llama 3.1          | 405B       | 231GB | `ollama run llama3.1:405b`     |
| Phi 3 Mini         | 3.8B       | 2.3GB | `ollama run phi3`              |
| Phi 3 Medium       | 14B        | 7.9GB | `ollama run phi3:medium`       |
| Gemma 2            | 2B         | 1.6GB | `ollama run gemma2:2b`         |
| Gemma 2            | 9B         | 5.5GB | `ollama run gemma2`            |
| Gemma 2            | 27B        | 16GB  | `ollama run gemma2:27b`        |
| Mistral            | 7B         | 4.1GB | `ollama run mistral`           |
| Moondream 2        | 1.4B       | 829MB | `ollama run moondream`         |
| Neural Chat        | 7B         | 4.1GB | `ollama run neural-chat`       |
| Starling           | 7B         | 4.1GB | `ollama run starling-lm`       |
| Code Llama         | 7B         | 3.8GB | `ollama run codellama`         |
| Llama 2 Uncensored | 7B         | 3.8GB | `ollama run llama2-uncensored` |
| LLaVA              | 7B         | 4.5GB | `ollama run llava`             |
| Solar              | 10.7B      | 6.1GB | `ollama run solar`             |



|❗ Note: Currently, the Assistant's embbeder model cannot be configured through the Assistant's UI. This means that whatever model you specify in the ```.env``` file under the variable name __EMBEDDER_MODEL__ must already be installed on your computer. You can verify the models installed by running the command ```ollama list``` |
|--|


