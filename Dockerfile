FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy bot script and .env file
COPY bot.py . 
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir discord.py python-dotenv requests

# Run the bot
CMD ["python", "bot.py"]
