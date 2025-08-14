FROM python:3.13-slim
WORKDIR /opt/lifechecker
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl cron \
    && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:/root/.cargo/bin:${PATH}"
COPY . .
RUN uv pip install --system .
# So logs appear instantly in docker logs
ENV PYTHONUNBUFFERED=1

# Remove the static cron file creation since we'll do it dynamically
# in the startup script to capture environment variables

# Create startup script that captures environment and sets up cron
RUN echo '#!/bin/bash\n\
# Create cron job with environment variables\n\
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin:/root/.cargo/bin" > /tmp/cronfile\n\
# Add environment variables to cron file\n\
printenv | grep -E "^NAMECHEAP_|^PYTHON" >> /tmp/cronfile\n\
# Add the actual cron job with output redirection to stdout/stderr\n\
echo "*/15 * * * * /usr/local/bin/python3 /opt/lifechecker/src/namecheap_lifechecks/main.py >> /proc/1/fd/1 2>> /proc/1/fd/2" >> /tmp/cronfile\n\
\n\
# Install the cron job\n\
crontab /tmp/cronfile\n\
\n\
printenv | grep -E "^NAMECHEAP_" || echo "No NAMECHEAP_ variables found"\n\
crontab -l\n\
# Start cron in foreground\n\
exec cron -f' > /start.sh && chmod +x /start.sh

CMD ["/start.sh"]