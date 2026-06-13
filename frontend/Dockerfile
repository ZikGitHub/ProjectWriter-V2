FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Ensure binaries are in the path
ENV PATH /app/node_modules/.bin:$PATH

CMD ["npm", "run", "dev", "--", "--host"]
