FROM nginx:1.13
RUN rm /etc/nginx/conf.d/default.conf
COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/app.conf
EXPOSE 80
CMD nginx -g "daemon off;"
