FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
# El builder de Angular emite en dist/<proyecto>/browser, no en dist/ directamente.
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
