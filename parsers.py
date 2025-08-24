import json
import os
import sys
import subprocess
from collections import deque

LOCKFILE = 'package-lock.json'

def scan_dep():
    if not os.path.exists(LOCKFILE):
        print(f"Error: {LOCKFILE} not found.")
        sys.exit(1)

    results = subprocess.run(
        ["osv-scanner", "scan", "-L", LOCKFILE, "--format", "json"],
        capture_output=True, text=True, encoding="utf-8"
    )

    return json.loads(results.stdout)

def transforms_result(scan_data):
    # load lockfile
    with open(LOCKFILE, "r", encoding="utf-8") as f:
        lock = json.load(f)

    packages = lock.get("packages", {})
    graph = {}
    for path, meta in packages.items():
        if path == "":
            continue
        name = path.split("node_modules/")[-1]
        deps = list((meta.get("dependencies") or {}).keys())
        graph[name] = deps

    roots = list((packages.get("") or {}).get("dependencies", {}).keys())

    findings = []
    for result in scan_data.get("results", []):
        for pkg in result.get("packages", []):
            pkg_name = pkg.get("package", {}).get("name")
            version = pkg.get("package", {}).get("version")
            for vuln in pkg.get("vulnerabilities", []):
                cve = (vuln.get("aliases") or [vuln.get("id")])[0]

                # BFS to find all paths from roots to pkg_name
                paths = []
                for r in roots:
                    queue = deque([[r]])
                    while queue:
                        path = queue.popleft()
                        last = path[-1]
                        if last == pkg_name:
                            paths.append(path)
                        else:
                            for nxt in graph.get(last, []):
                                if nxt not in path:
                                    queue.append(path + [nxt])

                if not paths:
                    paths = [[pkg_name]]

                for path in paths:
                    if len(path) == 1:
                        dep_graph = pkg_name
                    else:
                        dep_graph = " -> ".join(path)
                    findings.append({
                        "CVE": cve,
                        "name": pkg_name,
                        "version": version,
                        "dependency_graph": dep_graph
                    })

    return {"results": findings}

if __name__ == '__main__':
    raw = scan_dep()
    results = transforms_result(raw)
    with open("findings.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Wrote out_results.json with", len(results["results"]), "findings")
