import json
import os
import sys
import subprocess

LOCKFILE = 'package-lock.json'

def scan_dep():
    if not os.path.exists(LOCKFILE):
        print(f"Error: {LOCKFILE} not found.")
        sys.exit(1)

    results = subprocess.run(
        ["osv-scanner", "scan", "-L", LOCKFILE, "--format", "json"],
        capture_output=True, text=True
    )

    # if results.returncode != 0:
    #     print(f"Error running osv-scanner: {results.stderr.strip()}")
    #     sys.exit(results.returncode)

    return json.loads(results.stdout)

def transforms_result(scan_data):
    findings = []
    for result in scan_data.get("results", []):
        for pkg in result.get("packages", []):
            pkg_name = pkg.get("package", {}).get("name")
            version = pkg.get("package", {}).get("version")
            dependencies = pkg.get("dependencies", [])
            dependency_graph = pkg_name
            if dependencies:
                dependency_graph = " → ".join([pkg_name] + [dep.get("name") for dep in dependencies])
            for i in pkg.get("vulnerabilities", []):
                if i.get("aliases"):
                    cve = str(i.get("aliases")[0])
                else:
                    cve = i.get("id")
                findings.append({
                    "cve": cve,
                    "name": pkg_name,
                    "version": version,
                    "dependency_graph": dependency_graph
                })
    return {"results": findings}

if __name__ == '__main__':
    raw = scan_dep()
    structured_data = transforms_result(raw)
    with open('findings.json', 'w') as f:
        json.dump(structured_data, f, indent=2)
    print("Scan completed successfully. Findings saved to findings.json.")