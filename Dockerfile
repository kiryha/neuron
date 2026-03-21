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

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# FIX 1: Change 'neuron.py' or 'app.py' to 'main.py'
COPY --chown=user main.py .
COPY --chown=user --from=build-stage /frontend/dist ./dist

# FIX 2: Change the entry point to 'main:app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]