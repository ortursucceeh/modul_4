FROM python:latest
#Create a working directory
WORKDIR /src
#Copy toml in workdir
COPY ["pyproject.toml", "/src/"]
#install dependecies from .toml
# RUN pip install -e .
#copy other files in workdir
COPY . /src
#run out code
CMD ["python", "main.py"]