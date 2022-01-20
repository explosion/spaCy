FROM node:11.15.0 

WORKDIR /spacy-io

RUN npm install -g gatsby-cli@2.7.4

COPY package.json .
COPY package-lock.json . 

RUN npm install

# This is so the installed node_modules will be up one directory
# from where a user mounts files, so that they don't accidentally mount
# their own node_modules from a different build
# https://nodejs.org/api/modules.html#modules_loading_from_node_modules_folders
WORKDIR /spacy-io/website/
