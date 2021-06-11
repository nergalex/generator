FROM python:3-slim

# to be able to use "nano" with shell on "docker exec -it [CONTAINER ID] bash"
ENV TERM xterm

COPY generator.py /

EXPOSE 8080

WORKDIR /
CMD ["python", "generator.py"]
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD curl -f http://localhost:8080 || exit 1


