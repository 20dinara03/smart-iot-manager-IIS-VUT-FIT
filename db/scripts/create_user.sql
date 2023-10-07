CREATE USER grafita;
CREATE DATABASE grafitadb;
GRANT ALL PRIVILEGES ON DATABASE grafitadb TO grafita;

\c grafitadb
GRANT ALL PRIVILEGES ON SCHEMA public TO grafita;
