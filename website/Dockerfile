FROM node:18

USER node

# This is so the installed node_modules will be up one directory
# from where a user mounts files, so that they don't accidentally mount
# their own node_modules from a different build
# https://nodejs.org/api/modules.html#modules_loading_from_node_modules_folders
WORKDIR /home/node
COPY --chown=node package.json .
COPY --chown=node package-lock.json .
RUN npm install

WORKDIR /home/node/website/
