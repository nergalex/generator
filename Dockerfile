FROM python:3-slim

# to be able to use "nano" with shell on "docker exec -it [CONTAINER ID] bash"
ENV TERM xterm
ENV PYTHONUNBUFFERED=1

COPY generator.py /
COPY /routes /routes

EXPOSE 8080

RUN pip install requests
RUN apt install curl net-tools

WORKDIR /
CMD ["python", "generator.py"]
HEALTHCHECK --interval=5s --timeout=3s --retries=3 CMD curl -f http://localhost:80 || exit 1


