FROM nginx

WORKDIR /usr/share/react

RUN echo "Package: nodejs" >> /etc/apt/preferences.d/preferences && \
    echo "Pin: origin deb.nodesource.com" >> /etc/apt/preferences.d/preferences && \
    echo "Pin-Priority: 1001" >> /etc/apt/preferences.d/preferences

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs
    
COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

COPY nginx.conf /etc/nginx/nginx.conf

RUN rm -r /usr/share/nginx/html/*

RUN cp -a build/. /usr/share/nginx/html

