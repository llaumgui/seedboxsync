---
title: OAuth2
summary: SeedboxSyncFront  — The seedboxsync frontend
---

# OAuth2 / OpenID Connect (OIDC) Setup Guide

SeedboxSync supports authentication via **OpenID Connect** (OIDC) providers such as Authelia, Keycloak, or Authentik.

---

## Configuration Parameters

Set these via the Web UI (`Settings` > `Authentication`) or environment variables:

| Parameter | Description |
| --- | --- |
| **`oauth_enabled`** | Enables/disables OIDC authentication (`true`/`false`). |
| **`oauth_auto_create_user`** | Automatically provisions a local user on first login (`true`/`false`). |
| **`oauth_disable_builtin_authentication`** | Hides local password login form (`true`/`false`). |
| **`oauth_name`** | Provider identifier (e.g., `authelia`). |
| **`oauth_client_id`** | OAuth Client ID. |
| **`oauth_client_secret`** | Plaintext OAuth Client Secret. |
| **`oauth_server_metadata_url`** | OpenID discovery URL (e.g., `https://auth.example.ltd/.well-known/openid-configuration`). |

## Prerequisites & Redirect URIs

Configure your Identity Provider (IdP) with:

* **Flow:** Authorization Code Flow with PKCE (`S256`).
* **Token Auth Method:** `client_secret_post`.
* **Scopes:** `openid`, `profile`, `email`.
* **Redirect URI:**

```text
https://seedbox.example.ltd/oauth2/oidc/callback

```

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
