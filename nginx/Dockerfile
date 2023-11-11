# Utilizamos la imagen oficial de Nginx
FROM nginx:alpine

# Eliminamos el archivo de configuración por defecto de Nginx
RUN rm /etc/nginx/conf.d/*

# Copiamos nuestro archivo de configuración personalizado
COPY ./default.conf /etc/nginx/conf.d/

# Exponemos el puerto 80 en el contenedor
EXPOSE 80

# Comando para iniciar Nginx cuando el contenedor se ejecute
CMD ["nginx", "-g", "daemon off;"]
