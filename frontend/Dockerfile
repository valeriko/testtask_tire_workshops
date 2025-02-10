# Use the Node.js LTS image
FROM node:18

# Set the working directory inside the container
WORKDIR /app

# Install global packages
#RUN npm install -g npm@latest

# Copy dependency files (package.json and yarn.lock) first for better caching
COPY package.json ./

# Install dependencies
RUN yarn install
RUN yarn add -D @vitejs/plugin-vue
RUN yarn add vue-router


# Copy the application source code into the container
COPY . .

# Expose the port Vite uses
EXPOSE 8080

# Build the application
#RUN yarn build

# Start the application using Yarn
# CMD ["yarn", "serve"]
CMD ["yarn", "dev", "--host", "0.0.0.0"]
