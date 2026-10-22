# 桥接导出器（prod-net）：指标快照 + SHA-256 → bridge-volume
FROM python:3.11-slim
WORKDIR /srv
COPY exporter.py .
CMD ["python", "-u", "exporter.py"]
