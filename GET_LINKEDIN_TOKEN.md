# How to Get Your LinkedIn API Token (Free)

## Step 1 — Create a LinkedIn Developer App
1. Go to https://www.linkedin.com/developers/apps
2. Click **Create app**
3. App name: `My Content Bot` (anything)
4. LinkedIn page: link your personal profile page
5. Click **Create app**

## Step 2 — Request the right permission
1. In your app → **Products** tab
2. Enable **Share on LinkedIn** (gives `w_member_social`)
3. Wait ~1 minute for approval (instant for personal use)

## Step 3 — Get your Access Token
1. Go to **Auth** tab in your app
2. Copy your **Client ID** and **Client Secret**
3. In the **OAuth 2.0 tools** section → click **OAuth token tools**
4. Select scopes: `openid`, `profile`, `w_member_social`
5. Click **Request access token**
6. Copy the token — save it as `LINKEDIN_ACCESS_TOKEN`

> ⚠️ Token expires after 60 days. Set a calendar reminder to refresh it.

## Step 4 — Get your Person URN
Run this in your terminal after setting your token:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://api.linkedin.com/v2/userinfo
```

Look for `"sub"` in the response — your URN is `urn:li:person:<sub value>`.
Save this as `LINKEDIN_PERSON_URN`.

## Step 5 — Add to GitHub Secrets
1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:
   - `ANTHROPIC_API_KEY`
   - `GEMINI_API_KEY`
   - `LINKEDIN_ACCESS_TOKEN`
   - `LINKEDIN_PERSON_URN`

Done! Your pipeline is fully configured.
