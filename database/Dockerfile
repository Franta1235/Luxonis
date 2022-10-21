FROM postgres:latest
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_USER=username
ENV POSTGRES_DB=database
COPY create_table.sql /docker-entrypoint-initdb.d/create_table.sql
