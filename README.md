# SCA Task: Vulnerable npm Package Scanner

This project provides a Dockerized tool to scan npm repositories for vulnerable dependencies using open-source tools, and transforms the results into actionable JSON output.

## Features

- Scans `package-lock.json` for vulnerable npm packages using [`osv-scanner`](https://github.com/google/osv-scanner).
- Parses and structures scan results with Python.
- Outputs findings in a structured JSON format.
- Includes pytest tests for direct, transitive, and multiple introduction paths.

## Usage

1. **Build the Docker image:**
   ```sh
   docker build -t sca-task .
   ```

2. **Run the scanner:**
   ```sh
   docker run --rm -v $PWD:/scaapp sca-task
   ```
   This will scan the `package-lock.json` in your current directory and output `findings.json`.

3. **Run tests:**
   ```sh
   docker run --rm -v $PWD:/scaapp --entrypoint pytest sca-task test.py
   ```
## Output Format

The results are saved to `findings.json`.
