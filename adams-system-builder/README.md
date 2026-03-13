# ⚡ Adam's System Builder — Online Deployment Guide

> Full-stack agentic AI webapp factory. Runs on Coolify (Hostinger VPS).
> Google Login • Dark UI • n8n JSON • Antigravity Prompts • Coolify Commands

---

## 🚀 Deploy in 4 Steps

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Adam's System Builder v2 — online"
git remote add origin https://github.com/YOUR_USERNAME/adams-system-builder.git
git push -u origin main
```

---

### Step 2 — Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project → **APIs & Services → Credentials**
3. Click **Create Credentials → OAuth 2.0 Client ID**
4. Application type: **Web application**
5. Add Authorised redirect URI: `https://builder.YOURDOMAIN.com`
   *(or your Coolify-assigned URL)*
6. Copy the **Client ID** and **Client Secret**

---

### Step 3 — Deploy on Coolify (Hostinger VPS)

#### 3a. SSH into your VPS and install Coolify (if not done yet):
```bash
ssh root@YOUR_VPS_IP
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

#### 3b. Open Coolify at `http://YOUR_VPS_IP:8000`

#### 3c. Add new resource:
- **New → Application → GitHub Repository**
- Select your `adams-system-builder` repo
- Build Pack: **Dockerfile**
- Port: `8501`
- Domain: `builder.yourdomain.com`

#### 3d. Add Environment Variables in Coolify UI:

| Variable | Value |
|---|---|
| `GOOGLE_CLIENT_ID` | `your-id.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | `GOCSPX-your-secret` |
| `REDIRECT_URI` | `https://builder.yourdomain.com` |
| `ALLOWED_EMAILS` | `your@gmail.com` |
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJh...` |

#### 3e. Click **Deploy** ✅

---

### Step 4 — Set Up Supabase Tables

1. Go to your [Supabase project](https://supabase.com)
2. Open **SQL Editor**
3. Paste and run this:

```sql
-- Enable UUID
create extension if not exists "uuid-ossp";

-- Projects
create table if not exists projects (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  industry text,
  business_type text,
  status text default 'active',
  config jsonb default '{}',
  owner text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Interactions
create table if not exists interactions (
  id uuid default uuid_generate_v4() primary key,
  project_id uuid references projects(id) on delete cascade,
  agent_name text,
  input jsonb,
  output jsonb,
  status text default 'pending',
  duration_ms int,
  error text,
  created_at timestamptz default now()
);

-- Settings
create table if not exists settings (
  key text primary key,
  value text,
  updated_at timestamptz default now()
);

-- RLS (service role full access)
alter table projects enable row level security;
alter table interactions enable row level security;
alter table settings enable row level security;
create policy "Service role" on projects for all using (true);
create policy "Service role" on interactions for all using (true);
create policy "Service role" on settings for all using (true);
```

---

## 📂 File Structure

```
adams-system-builder/
├── app.py                    # Main app + routing
├── Dockerfile                # Coolify deployment
├── requirements.txt          # Python deps
├── .env.example              # All required env vars
├── .streamlit/
│   └── config.toml           # Dark theme config
├── utils/
│   ├── auth.py               # Google OAuth
│   ├── styles.py             # Dark theme + red/green CSS
│   ├── storage.py            # Supabase save/load
│   ├── playbooks.py          # Industry playbooks
│   └── generators.py         # n8n JSON, Antigravity, Coolify, SQL
└── pages/
    ├── dashboard.py          # Home + quick prompts
    ├── intake.py             # New customer form
    ├── questionnaire.py      # Adaptive industry questions
    ├── agent_builder.py      # Choose agent architecture
    ├── generate.py           # One-click generate all outputs
    └── settings.py           # All server credentials
```

---

## 🔑 The Two Prompts

### AI Reminder Prompt (paste into any AI session to restore context):
```
You are Adam's (adman_cross) dedicated System Builder AI. Your single mission is
to power his Python/Streamlit app that creates custom agentic AI webapps for any
industry using: n8n (Hostinger + Coolify), Supabase, Antigravity + Claude Code
(with n8n expert skill packs), Code Rabbit CLI for bug fixing. Mirror Cook OS
(Skills + Context + Tools), webprodigies workflows, n8n agent tutorials, and Dan
Martell one-stop GTM. Always output ready-to-import n8n JSON, Antigravity-ready
prompts, Coolify commands, or Streamlit code updates. Prioritise speed-to-live
for high-ticket clients (Catholic Archdiocese, SaaS, healthcare, etc.). Never
suggest cloud-only tools. Stay agentic and autonomous.
```

### Customer Build Prompt (use in Agent Builder or Antigravity):
```
Build a complete agentic AI webapp for [Business Name] in the [Industry] sector.
Requirements: [paste questionnaire answers]. Core stack: n8n self-hosted on
Hostinger/Coolify, Supabase DB, Antigravity + Claude Code for autonomous
execution, Code Rabbit for every PR. Include [voice / donation / CRM] flows.
Output: 1) importable n8n JSON, 2) Supabase schema SQL, 3) Antigravity skill
prompt, 4) Coolify deploy command. Make it fully autonomous like Cook OS.
```

---

## 🏗️ App Flow

```
Login (Google) → Dashboard → New Customer → Questionnaire
    → Agent Builder → Generate & Deploy
         ├── n8n JSON (download)
         ├── Antigravity Prompt (download)
         ├── Coolify Commands (download)
         ├── Supabase SQL (download)
         └── .env.example (download)
```

---

## 🔒 Security Notes

- All credentials entered via **Settings** page are stored in Supabase (encrypted at rest)
- Google OAuth restricts login to your email(s) only via `ALLOWED_EMAILS`
- Supabase Service Key is never exposed to frontend — server-side only
- No secrets in Git — all via Coolify environment variables

---

## 🆘 Support

- Streamlit issues: https://docs.streamlit.io
- Coolify issues: https://coolify.io/docs
- n8n community: https://community.n8n.io
- Supabase docs: https://supabase.com/docs
