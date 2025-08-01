# Use an official Node.js runtime as a parent image
FROM node:20-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json first to leverage Docker layer caching.
# This step is more explicit and robust than using a wildcard.
COPY package.json ./

# Install app dependencies. This creates a separate layer that is only
# rebuilt if package.json changes.
RUN npm install --omit=dev --legacy-peer-deps

# Bundle the rest of your app's source code
COPY . .

# Your app binds to port 8080
EXPOSE 8080

# Define the command to run your app
CMD [ "npm", "start" ]