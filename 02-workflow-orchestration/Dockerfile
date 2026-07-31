FROM kestra/kestra:v1.3.29-no-plugins

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
    && rm -rf /var/lib/apt/lists/*

# RUN /app/kestra plugins install io.kestra.plugin:plugin-script-shell:1.9.6 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-jdbc-postgresql:1.15.4 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-gcp:2.10.0 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-script-python:1.9.6 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-script:1.9.6 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-jdbc-duckdb:1.15.4 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-ansible:1.6.1 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-git:2.0.10 && \
#     /app/kestra plugins install io.kestra.plugin:plugin-dbt:1.7.3