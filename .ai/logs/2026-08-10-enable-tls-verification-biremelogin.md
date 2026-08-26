# Enable TLS verification in BIREME login

Date: 2026-08-10

## Problem

Every login attempt emitted:

```
/usr/local/lib/python3.10/site-packages/urllib3/connectionpool.py:1110: InsecureRequestWarning:
Unverified HTTPS request is being made to host 'accounts.bireme.org'. Adding certificate
verification is strongly advised.
```

## Cause

`src/biremelogin/authenticate.py` called the accounts API with `verify=False`, disabling
certificate validation. This was the only occurrence of `verify=False` in the codebase and
appears to be legacy from when the host served an untrusted certificate.

## Change

Removed the `verify=False` argument so `requests` performs normal certificate verification
(the default). This eliminates the warning by fixing its cause rather than silencing it, and
restores protection against man-in-the-middle attacks on the credential exchange.

`src/biremelogin/authenticate.py:32`

```python
r = requests.post(api_uri, data=json.dumps(data), headers=headers)
```

Also added a generic `dev_exec` target to the Makefile for running one-off commands in the
dev container:

```
make dev_exec cmd="python -c '...'"
```

## Verification

- `accounts.bireme.org` certificate chain validates from the host (`curl` reported
  `ssl_verify_result 0`).
- Confirmed inside the dev container that `requests` verifies successfully against the live
  endpoint: the POST completed with HTTP 401 (expected for dummy credentials), with no
  `SSLError` and no `InsecureRequestWarning`. `certifi` bundle in use:
  `/usr/local/lib/python3.10/site-packages/certifi/cacert.pem`.
- `make dev_test_app app=biremelogin` — 1 test, OK.

## Note

If `accounts.bireme.org` ever presents a self-signed or internal-CA certificate again, the
correct fix is to point `REQUESTS_CA_BUNDLE` at the CA file rather than reinstating
`verify=False`.
