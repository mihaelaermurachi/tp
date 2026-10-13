from checker import build_url, is_https, show_response, check_site, scan_sites, check_headers, retry_check

# Partea 1: build_url și is_https
print("Partea 1, build_url (fără /):", build_url("example.com", "login"))
print("Partea 1, build_url (cu /):", build_url("example.com", "/login"))
print("Partea 1, is_https (https):", is_https("https://example.com"))
print("Partea 1, is_https (http):", is_https("http://example.com"))

# Partea 2: show_response
print("\nPartea 2, show_response pe https://example.com:")
show_response("https://example.com")
print("Partea 2, show_response pe adresă inexistentă:")
show_response("http://this-site-does-not-exist.invalid")

# Partea 3: check_site
print()
print("Partea 3, check_site (merge):", check_site("https://example.com"))
print("Partea 3, check_site (404):", check_site("https://httpbin.org/status/404"))
print("Partea 3, check_site (inexistent):", check_site("http://this-site-does-not-exist.invalid"))
print("Partea 3, check_site (prea lent):", check_site("https://httpbin.org/delay/10"))

# Partea 4: scan_sites
print("\nPartea 4, scan_sites:")
scan_sites()

# Partea 5: check_headers
print()
print("Partea 5, check_headers (2 antete):",
      check_headers("https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff"))
print("Partea 5, check_headers (litere mici):",
      check_headers("https://httpbin.org/response-headers?x-frame-options=DENY"))
print("Partea 5, check_headers (fără antete):", check_headers("https://httpbin.org/html"))
print("Partea 5, check_headers (inexistent):",
      check_headers("http://this-site-does-not-exist.invalid"))

# Partea 6: retry_check
print()
print("Partea 6, retry_check 200:", retry_check("https://httpbin.org/status/200"))
print("Partea 6, retry_check 404:", retry_check("https://httpbin.org/status/404"))
print("Partea 6, retry_check 500:", retry_check("https://httpbin.org/status/500"))
print("Partea 6, retry_check 500, attempts=2:", retry_check("https://httpbin.org/status/500", attempts=2))
print("Partea 6, retry_check inexistent:", retry_check("http://this-site-does-not-exist.invalid"))
print("Partea 6, retry_check aleatoriu:", retry_check("https://httpbin.org/status/200,500"))
