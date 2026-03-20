# --- Build Frontend ---
FROM node:20 AS build-stage
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# --- Build Backend ---
FROM python:3.10
WORKDIR /app

# Create a user to avoid permission issues on HF
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy backend code and the built frontend
COPY --chown=user app.py .
COPY --chown=user --from=build-stage /frontend/dist ./dist

# Port 7860 is the Hugging Face default
CMD ["uvicorn", "neuron:app", "--host", "0.0.0.0", "--port", "7860"]