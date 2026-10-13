import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]

TIMEOUT = 5 


def short_error(exc):
    """Transformă o excepție din requests într-un mesaj scurt."""
    if isinstance(exc, requests.exceptions.Timeout):
        return "timeout"
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "connection error"
    return type(exc).__name__


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    return "https://" + host + "/" + path.lstrip("/")


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type", "unknown"))
    except requests.exceptions.RequestException as exc:
        print("Eroare:", short_error(exc))


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        return {"status": None, "error": short_error(exc)}


    content_type = response.headers.get("Content-Type", "unknown").split(";")[0]
    return {
        "status": response.status_code,
        "content_type": content_type,
        "length": len(response.content),
        "server": response.headers.get("Server", "unknown"),
    }


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    results = []
    for url in SITES:
        info = check_site(url)
        info["url"] = url
        results.append(info)


    working = [r for r in results if r["status"] == 200]
    working.sort(key=lambda r: r["length"], reverse=True)

    for r in working:
        print(f"{r['url']} -> {r['status']}, {r['length']} octeți")

    ok = len(working)
    failed = len(results) - ok
    print(f"Reușite: {ok} | Eșuate: {failed}")


def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        response = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.RequestException as exc:
        return {"status": None, "error": short_error(exc)}

    present = []
    missing = []
    for header in SECURITY_HEADERS:
        # response.headers nu ține cont de majuscule
        if header in response.headers:
            present.append(header)
        else:
            missing.append(header)

    score = len(present) * 100 // len(SECURITY_HEADERS)
    return {"present": present, "missing": missing, "score": score}


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    status = None
    error = None
    made = 0

    for _ in range(attempts):
        made += 1
        try:
            response = requests.get(url, timeout=TIMEOUT)
        except requests.exceptions.RequestException as exc:
            status = None
            error = short_error(exc)
            continue  

        status = response.status_code
        error = None
        if status < 500:
            break  

    result = {"status": status, "attempts": made}
    if error is not None:
        result["error"] = error
    return result
