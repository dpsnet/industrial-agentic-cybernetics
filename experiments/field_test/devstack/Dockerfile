FROM python:3.11-slim
WORKDIR /srv
RUN pip install --no-cache-dir requests fastapi prometheus-client
COPY auditor.py sniffer.py gate.py validator.py crystallizer.py hotfix_gen.py field_audit.py ./
CMD ["python", "-u", "auditor.py"]
