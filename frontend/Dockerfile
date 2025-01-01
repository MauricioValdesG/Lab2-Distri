# Etapa de construcción
FROM node:18 AS build

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios
COPY package*.json ./

# Instala las dependencias
RUN npm install

# Copia el resto del proyecto
COPY . .

# Construye la aplicación para producción
RUN npm run build

# Etapa de producción
FROM nginx:stable-alpine

# Copia los archivos estáticos generados al servidor
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Inicia el servidor Nginx
CMD ["nginx", "-g", "daemon off;"]
