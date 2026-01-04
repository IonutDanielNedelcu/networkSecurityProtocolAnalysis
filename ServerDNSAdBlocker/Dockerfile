FROM python:3
WORKDIR /app
COPY serverdns.py blacklist.txt ./
EXPOSE 53/udp
CMD ["python3", "serverdns.py"]