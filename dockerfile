FROM python:3.11 

WORKDIR /server/paios

# Copia todos los archivos al contenedor
COPY . .

# Ejecuta el script de configuración de entorno
RUN python scripts/setup_environment.py
# RUN pip install --upgrade virtualenv

# Define el comando por defecto para ejecutar la aplicación
WORKDIR /server
COPY entrypoint.sh .


CMD ["bash", "entrypoint.sh"]