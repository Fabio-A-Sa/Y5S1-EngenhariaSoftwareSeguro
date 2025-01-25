# Project

## Students

- André Costa Lima (up202008169)
- Eduardo Luís Tronjo Ramos (up201906732)
- Fábio Araújo de Sá (up202007658)
- Inês Sá Pereira Estêvão Gaspar (up202007210)

## Documentation

- [Report](./docs/report.pdf)

## Local Development

1. Clone the repository
2. Run the containers using Docker Compose with `docker compose up --force-recreate --build --watch`. On Windows, you need to use `docker compose up --force-recreate --build --wait setup_workspace_script; docker compose up --force-recreate --build --watch` instead.
3. The containers will automatically restart when you make changes to the source code, including to the respective dependencies.

## Code Editor Support

Dependencies installed in containers are not detected by your IDE.
As such, you will need to install the dependencies locally.

To do that, run the following commands:

1. Create a virtual environment

   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment

   ```bash
   source .venv/bin/activate
   ```

3. Install poetry

   ```bash
   pip install -r poetry-requirements.txt
   ```

4. Install the dependencies for each of the applications and packages

   ```bash
   poetry install --no-root -C packages/cert_manager
   poetry install --no-root -C packages/nonce
   poetry install --no-root -C packages/secure_endpoints
   poetry install --no-root -C packages/utils
   
   # Remove lockfiles from the packages
   rm packages/cert_manager/poetry.lock
   rm packages/nonce/poetry.lock
   rm packages/secure_endpoints/poetry.lock
   rm packages/utils/poetry.lock

   poetry install -C apps/authentication_server
   poetry install -C apps/authorization_server
   poetry install -C apps/resource_server
   poetry install -C apps/web_server
   ```

5. Use the virtual environment in `.venv` as your Python interpreter in your IDE.

# Installing new dependencies

Dependencies are managed using [Poetry](https://python-poetry.org/).

To add a new dependency to a package or app:

1. Create a new virtual environment
   
   ```bash
   python -m venv .venv
   ```

2. Activate the virtual environment
   
   ```bash
   source .venv/bin/activate
   ```

3. Install poetry

   ```bash
   pip install -r poetry-requirements.txt
   ```

4. Go to the package you want to add the dependency to

   ```bash
   cd apps/authentication_server
   ```

5. Install the dependency using poetry

   ```bash
   # poetry add <dependency>
   poetry add Flask # example for a PyPI dependency
   poetry add ../../packages/cert_manager -e # example for a local dependency
   ```

6. If the installed dependency is a local dependency, you will need to:
   
   1. update `deploy/apps.containerfile` to include the new dependency.

      ```diff
      FROM local_packages AS authentication_server_local_packages
      + COPY ./packages/cert_manager ./packages/cert_manager/
      ```

   2. update `compose.yml` and `compose.prod.yml` to include the new dependency.

      ```diff
      services:
        authentication_server:
          ...
          develop:
            watch:
              ...  
              - path: ./apps/authentication_server/poetry.lock
                target: /app/apps/authentication_server/poetry.lock
                action: rebuild
      +       - path: ./packages/cert_manager
      +         target: /app/packages/cert_manager
      +         action: sync # Or `sync+restart`, if in compose.prod.yml
      ```
