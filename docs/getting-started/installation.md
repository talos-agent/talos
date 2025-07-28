# Installation

This guide will help you install and set up Talos on your system.

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`
- Git

## Installation Methods

### Using uv (Recommended)

Talos uses `uv` for dependency management, which provides faster and more reliable package installation.

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/talos-agent/talos.git
   cd talos
   ```

3. **Create a virtual environment**:
   ```bash
   uv venv
   ```

4. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

5. **Install dependencies**:
   ```bash
   ./scripts/install_deps.sh
   ```

### Using pip

If you prefer to use pip instead of uv:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/talos-agent/talos.git
   cd talos
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

## Environment Variables

Talos requires several API keys to function properly. Set up the following environment variables:

### Required for Basic Functionality
```bash
export OPENAI_API_KEY="your-openai-api-key"
export PINATA_API_KEY="your-pinata-api-key"
export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
```

### Required for Full Functionality
```bash
export GITHUB_API_TOKEN="your-github-token"
export TWITTER_BEARER_TOKEN="your-twitter-bearer-token"
```

!!! tip "Environment File"
    You can create a `.env` file in the project root with these variables for convenience:
    ```bash
    OPENAI_API_KEY=your-openai-api-key
    PINATA_API_KEY=your-pinata-api-key
    PINATA_SECRET_API_KEY=your-pinata-secret-api-key
    GITHUB_API_TOKEN=your-github-token
    TWITTER_BEARER_TOKEN=your-twitter-bearer-token
    ```

## Docker Installation

### Building and Running with Docker

1. **Build the Docker image**:
   ```bash
   docker build -t talos-agent .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     -e OPENAI_API_KEY="your-openai-api-key" \
     -e GITHUB_API_TOKEN="your-github-token" \
     -e TWITTER_BEARER_TOKEN="your-twitter-bearer-token" \
     -e PINATA_API_KEY="your-pinata-api-key" \
     -e PINATA_SECRET_API_KEY="your-pinata-secret-api-key" \
     --name talos-agent \
     talos-agent
   ```

### Using Docker Compose

1. **Create a `.env` file** with your API keys (see above)

2. **Start the service**:
   ```bash
   docker-compose up -d
   ```

3. **View logs**:
   ```bash
   docker-compose logs -f
   ```

4. **Stop the service**:
   ```bash
   docker-compose down
   ```

## Verification

To verify your installation is working correctly:

1. **Run the interactive CLI**:
   ```bash
   uv run talos
   ```

2. **Run a simple test**:
   ```bash
   uv run talos "Hello, what can you do?"
   ```

If everything is set up correctly, Talos should respond with information about its capabilities.

## Troubleshooting

### Common Issues

**Missing API Keys**: Ensure all required environment variables are set. The agent will not function without valid API keys.

**Permission Errors**: Make sure you have the necessary permissions for the directories and that your virtual environment is activated.

**Network Issues**: Some features require internet access for API calls to OpenAI, GitHub, Twitter, and IPFS services.

**Docker Issues**: Ensure Docker is running and you have sufficient permissions to build and run containers.

For more help, check the [Development](../development/contributing.md) section or open an issue on GitHub.
