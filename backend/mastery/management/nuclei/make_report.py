import json
from html import escape

with open("results.json") as f:
    findings = json.load(f)

rows = []
for fnd in findings:
    info = fnd.get("info", {})
    ftype = fnd.get("type", "")

    # Derive HTTP method
    method = ""

    # 1) For normal HTTP templates, parse the first token of the HTTP request line
    if ftype == "http":
        req = fnd.get("request") or ""
        if req:
            # Example: "GET /api/groups/ HTTP/1.1\r\nHost: ..."
            method = req.split()[0]

    # 2) Fallback: try to parse from curl-command ("curl -X GET ...")
    if not method:
        curl = fnd.get("curl-command") or ""
        if "-X" in curl:
            parts = curl.split()
            for i, p in enumerate(parts):
                if p == "-X" and i + 1 < len(parts):
                    candidate = parts[i + 1].strip("'\"").upper()
                    if candidate in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
                        method = candidate
                    break

    rows.append({
        "severity": info.get("severity", ""),
        "template_id": fnd.get("template-id", ""),
        "name": info.get("name", ""),
        "method": method,
        "url": fnd.get("url", ""),
        "host": fnd.get("host", ""),
        "type": ftype,
        "timestamp": fnd.get("timestamp", ""),
    })

# Build table rows
html_rows = "\n".join(
    "<tr>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "<td>{}</td>"
    "</tr>".format(
        escape(r["severity"] or ""),
        escape(r["template_id"] or ""),
        escape(r["name"] or ""),
        escape(r["method"] or ""),
        escape(r["url"] or ""),
        escape(r["host"] or ""),
        escape(r["type"] or ""),
        escape(r["timestamp"] or ""),
    )
    for r in rows
)

# HTML template
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Nuclei Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; padding: 1rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 4px 8px; font-size: 13px; }}
  th {{ cursor: pointer; background: #f2f2f2; }}
  th:hover {{ background: #e0e0e0; }}
</style>
</head>
<body>
<h1>Nuclei Findings</h1>
<table id="results">
  <thead>
    <tr>
      <th onclick="sortTable(0)">Severity</th>
      <th onclick="sortTable(1)">Template ID</th>
      <th onclick="sortTable(2)">Name</th>
      <th onclick="sortTable(3)">Method</th>
      <th onclick="sortTable(4)">URL</th>
      <th onclick="sortTable(5)">Host</th>
      <th onclick="sortTable(6)">Type</th>
      <th onclick="sortTable(7)">Timestamp</th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>

<script>
function sortTable(col) {{
  var table = document.getElementById("results");
  var switching = true;
  var dir = "asc";
  var switchcount = 0;

  while (switching) {{
    switching = false;
    var rows = table.rows;

    for (var i = 1; i < rows.length - 1; i++) {{
      var shouldSwitch = false;
      var x = rows[i].getElementsByTagName("TD")[col];
      var y = rows[i + 1].getElementsByTagName("TD")[col];

      var xVal = x.innerText.toLowerCase();
      var yVal = y.innerText.toLowerCase();

      if ((dir === "asc" && xVal > yVal) || (dir === "desc" && xVal < yVal)) {{
        shouldSwitch = true;
        break;
      }}
    }}

    if (shouldSwitch) {{
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      switchcount++;
    }} else {{
      if (switchcount === 0 && dir === "asc") {{
        dir = "desc";
        switching = true;
      }}
    }}
  }}
}}
</script>

</body>
</html>
"""

html = html_template.format(rows=html_rows)

with open("report.html", "w") as f:
    f.write(html)

print("Wrote report.html")
