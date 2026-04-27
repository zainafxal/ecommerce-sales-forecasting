# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user required by Hugging Face Spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# ---
ENV HF_HOME=/tmp/.cache/huggingface
ENV TRANSFORMERS_CACHE=/tmp/.cache/huggingface

# Copy the requirements file into the container
COPY --chown=user:user requirements.txt .

# Install dependencies, clearing cache to save memory/storage
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY --chown=user:user . .

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application (Hugging face uses 7860 usually)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
