FROM python:3.7

# Add project folder to the virtual machine
ADD . /

# Install any necessary dependencies
RUN pip install --upgrade pip && \
    pip install -r environment.yml

# Open port 8880 for serving the websocket
EXPOSE 8880

# Run app.py when the container launches
CMD ["python", "app.py"]