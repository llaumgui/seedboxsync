---
title: OAuth2 / OIDC
summary: SeedboxSyncFront  — The seedboxsync frontend
---

# OAuth2 / OpenID Connect (OIDC) Setup Guide

SeedboxSync supports authentication via **OpenID Connect** (OIDC) providers such as Authelia, Keycloak, or Authentik.

## Configuration Parameters

Set these via the Web UI (`Settings` > `Authentication`).

## Prerequisites & Redirect URIs

Configure your Identity Provider (IdP) with:

* **Flow:** Authorization Code Flow with PKCE (`S256`).
* **Token Auth Method:** `client_secret_post`.
* **Scopes:** `openid`, `profile`, `email`.
* **Redirect URI:**

```text
https://seedbox.example.ltd/oauth2/oidc/callback
```

### User identity requirements

SeedboxSync requires the OIDC provider to return an `email` claim. This email address is used as the stable identifier for matching the OIDC identity with a local SeedboxSync user.

The displayed username is selected from the first available claim:

1. `preferred_username`
2. `name`
3. `email`

When **Auto-create users** is enabled, SeedboxSync creates a local user during the first successful OIDC login.

When **Auto-create users** is disabled, a local SeedboxSync user with the same email address must already exist. Otherwise, authentication will fail.

> :warning: Test OIDC login successfully before disabling built-in authentication. We recommend keeping an active local administrator account until the OIDC configuration has been fully validated, preferably using a private browser session.

When SeedboxSync is hosted behind a reverse proxy, ensure that the original host and protocol are forwarded correctly. In particular, the proxy should forward the `Host`, `X-Forwarded-Proto`, `X-Forwarded-Host`, and
`X-Forwarded-Port` headers so that SeedboxSync generates the expected HTTPS callback URL.

The OIDC client secret is stored in the SeedboxSync database. Protect the database file and its backups accordingly.

## Example Configuration

### Authelia

#### Step 1: Generate Client Secret Hash

Authelia requires a hashed secret in its configuration file:

```bash
docker run --rm authelia/authelia:latest authelia crypto hash generate pbkdf2 --variant sha512

```

* **Password:** `MySecret123!` *(plaintext secret to keep)*
* **Output:** `$pbkdf2-sha512$310000$xxxx...` *(hashed string for Authelia)*

#### Step 2: Update Authelia (`configuration.yml`)

```yaml
identity_providers:
  oidc:
    clients:
      - client_id: 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx'
        client_name: 'SeedboxSync'
        client_secret: '$pbkdf2-sha512$310000$xxxx...' # Hashed secret
        public: false
        authorization_policy: one_factor
        require_pkce: true
        pkce_challenge_method: 'S256'
        token_endpoint_auth_method: 'client_secret_post'
        userinfo_signed_response_alg: 'none'
        redirect_uris:
          - 'https://seedbox.example.ltd/oauth2/oidc/callback'
        scopes:
          - 'openid'
          - 'profile'
          - 'email'
        response_types:
          - 'code'
        grant_types:
          - 'authorization_code'

```

#### Step 3: Configure SeedboxSync

In SeedboxSync (`/settings/authentication`):

* **OAuth Provider Name:** `authelia`
* **OAuth Client ID:** `dc731fbd-ef73-4c13-88ad-1d9d080b04ec`
* **OAuth Client Secret:** `MySecret123!` *(plaintext)*
* **OpenID Metadata URL:** `https://auth.example.ltd/.well-known/openid-configuration`
* **Auto-create users:** Enabled

#### Step 4: Validate the Configuration

1. Keep built-in authentication enabled.
2. Sign out from SeedboxSync.
3. Open SeedboxSync in a private browser window.
4. Select **Login with authelia**.
5. Verify that the expected user is created or matched.
6. Verify that the user can access the application after logging out and back in.

Only disable built-in authentication after this validation succeeds.
