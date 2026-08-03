FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Install CPU-only PyTorch FIRST — sentence-transformers depends on
# torch, and without this, pip grabs the full GPU/CUDA build (several
# GB of NVIDIA libraries this container will never use, since it has
# no GPU).
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]