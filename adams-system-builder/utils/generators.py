"""
Output generators — AI-powered via Anthropic API.
Falls back to static templates if no API key is configured.
"""
import json
import uuid
import requests
from datetime import datetime


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-20250514"


# ─── Claude API helper ────────────────────────────────────────────────────────

def _call_claude(api_key: str, system: str, user: str, max_tokens: int = 4096) -> str:
    """Call Claude API and return the text response."""
    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": MODEL,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
            timeout=60,
        )
        data = resp.json()
        if resp.status_code != 200:
            raise Exception(data.get("error", {}).get("message", "API error"))
        return data["content"][0]["text"]
    except Exception as e:
        raise Exception(f"Claude API error: {e}")


def _project_context(business_name, industry, agents, goal, requirements, tech_stack) -> str:
    """Build a reusable project context block for prompts."""
    agents_str = "\n".join([f"  {i+1}. {a}" for i, a in enumerate(agents)])
    return f"""
Business: {business_name}
Industry: {industry}
Primary Goal: {goal or f'Automate the top workflows for {business_name}'}
Tech Stack: {', '.join(tech_stack)}
Agents to build:
{agents_str}
Requirements:
{requirements or 'Use industry best practices.'}
Stack constraints: Self-hosted on Hostinger VPS via Coolify. n8n for orchestration. Supabase for DB. No cloud-lock tools.
""".strip()


# ─── n8n JSON ─────────────────────────────────────────────────────────────────

def generate_n8n_json(business_name: str, industry: str, agents: list,
                      n8n_url: str = "", api_key: str = "",
                      goal: str = "", requirements: str = "",
                      tech_stack: list = None) -> str:
    if tech_stack is None:
        tech_stack = ["n8n", "Supabase", "Coolify"]

    if api_key:
        try:
            context = _project_context(business_name, industry, agents, goal, requirements, tech_stack)
            system = """You are an expert n8n workflow architect. You output ONLY valid, importable n8n workflow JSON — no explanation, no markdown, no code fences. Just raw JSON.

The JSON must follow n8n's exact import format with: name, nodes (array), connections (object), active (false), settings, tags, meta fields.

Every node must have: id (uuid), name, type, typeVersion, position ([x,y]), parameters.

Use these real n8n node types:
- Trigger: n8n-nodes-base.webhook
- AI Agent: @n8n/n8n-nodes-langchain.agent  
- LLM Chain: @n8n/n8n-nodes-langchain.chainLlm
- Claude model: @n8n/n8n-nodes-langchain.lmAnthropicClaude
- Supabase: n8n-nodes-base.supabase
- Send Email: n8n-nodes-base.emailSend
- HTTP Request: n8n-nodes-base.httpRequest
- Twilio SMS: n8n-nodes-base.twilio
- IF condition: n8n-nodes-base.if
- Error Trigger: n8n-nodes-base.errorTrigger
- Respond to Webhook: n8n-nodes-base.respondToWebhook
- Slack: n8n-nodes-base.slack
- Set: n8n-nodes-base.set

Build a complete, production-ready workflow with proper connections between all nodes. Include error handling nodes. Space nodes at 200px intervals."""

            user = f"""Build a complete importable n8n workflow JSON for this project:

{context}

Requirements:
- Include a webhook trigger
- Build separate sub-flows for each agent
- Connect all nodes properly in the connections object  
- Include a Supabase logging node for every interaction
- Add error handling that alerts via Slack or HTTP webhook
- Use Claude (Anthropic) as the AI model in all LLM nodes
- Add descriptive names to every node
- Production-ready, not a demo

Output ONLY the raw JSON. No explanation."""

            result = _call_claude(api_key, system, user, max_tokens=8192)
            # Strip any accidental markdown fences
            result = result.strip()
            if result.startswith("```"):
                result = result.split("\n", 1)[1]
                result = result.rsplit("```", 1)[0]
            # Validate it's real JSON
            json.loads(result)
            return result
        except Exception:
            pass  # Fall back to template

    return _template_n8n_json(business_name, industry, agents)


def _template_n8n_json(business_name: str, industry: str, agents: list) -> str:
    nodes = [
        {
            "id": str(uuid.uuid4()),
            "name": "Webhook Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [240, 300],
            "parameters": {
                "path": f"{industry.lower().replace(' ', '-')}-agent",
                "responseMode": "responseNode",
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "AI Agent Router",
            "type": "@n8n/n8n-nodes-langchain.agent",
            "typeVersion": 1,
            "position": [480, 300],
            "parameters": {
                "systemMessage": f"You are an AI agent for {business_name} in the {industry} sector. Route incoming requests to the correct automation workflow. Available agents: {', '.join(agents[:5])}",
                "options": {}
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Supabase - Log Interaction",
            "type": "n8n-nodes-base.supabase",
            "typeVersion": 1,
            "position": [720, 300],
            "parameters": {
                "operation": "insert",
                "tableId": "interactions",
                "dataToSend": "autoMapInputData",
            }
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Respond to Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [960, 300],
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{ {status: 'ok', agent: $json.output} }}"
            }
        }
    ]
    for i, agent in enumerate(agents[:3]):
        nodes.append({
            "id": str(uuid.uuid4()),
            "name": f"Agent: {agent[:30]}",
            "type": "@n8n/n8n-nodes-langchain.chainLlm",
            "typeVersion": 1,
            "position": [480, 480 + (i * 120)],
            "parameters": {
                "prompt": f"Execute the following task for {business_name}: {agent}. Use all available tools and return a structured response.",
            }
        })
    workflow = {
        "name": f"{business_name} — Agentic AI System",
        "nodes": nodes,
        "connections": {
            "Webhook Trigger": {"main": [[{"node": "AI Agent Router", "type": "main", "index": 0}]]},
            "AI Agent Router": {"main": [[{"node": "Supabase - Log Interaction", "type": "main", "index": 0}]]},
            "Supabase - Log Interaction": {"main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]},
        },
        "active": False,
        "settings": {"executionOrder": "v1", "saveManualExecutions": True},
        "tags": [industry, "agentic", "adam-system-builder"],
        "meta": {
            "generatedBy": "Adam's System Builder",
            "generatedAt": datetime.utcnow().isoformat(),
            "businessName": business_name,
            "industry": industry,
        }
    }
    return json.dumps(workflow, indent=2)


# ─── Antigravity / Claude Code Prompt ────────────────────────────────────────

def generate_antigravity_prompt(business_name: str, industry: str, agents: list,
                                 tech_stack: list, requirements: str = "", goal: str = "",
                                 api_key: str = "") -> str:
    if api_key:
        try:
            context = _project_context(business_name, industry, agents, goal, requirements, tech_stack)
            system = """You are an expert agentic AI systems architect. You write precise, detailed build prompts for Claude Code / Antigravity IDE that result in production-ready systems being built autonomously. Your prompts are specific, technical, and leave nothing to guesswork."""

            user = f"""Write a complete Antigravity / Claude Code build prompt for this project:

{context}

The prompt must include:
1. Clear mission statement
2. Full tech stack with versions
3. Numbered list of every agent to build with exact specifications
4. All requirements from the questionnaire
5. Exact deliverables (n8n JSON, SQL schema, deploy commands, env vars, agent system prompts, testing checklist)
6. Constraints (self-hosted, no cloud-lock, error handling on every workflow, Code Rabbit review on every file)
7. n8n node naming conventions and style guide
8. Supabase schema conventions (snake_case, uuid PKs, timestamps)
9. Security requirements (all secrets via env vars, never hardcoded)
10. Cook OS model: Skills + Context + Tools structure

Be specific to {business_name} in the {industry} industry. Make it immediately actionable."""

            return _call_claude(api_key, system, user, max_tokens=4096)
        except Exception:
            pass

    return _template_antigravity_prompt(business_name, industry, agents, tech_stack, requirements, goal)


def _template_antigravity_prompt(business_name, industry, agents, tech_stack, requirements, goal):
    agents_str = "\n".join([f"  {i+1}. {a}" for i, a in enumerate(agents)])
    stack_str = ", ".join(tech_stack)
    return f"""# Build Prompt — {business_name} Agentic AI System
# Generated by Adam's System Builder | {datetime.utcnow().strftime('%Y-%m-%d')}

## Mission
You are an expert n8n Senior Developer and Agentic AI Systems Architect.
Build a complete, production-ready agentic AI system for **{business_name}** in the **{industry}** sector.

## Tech Stack
{stack_str}
- Self-hosted on Hostinger VPS via Coolify
- n8n for workflow orchestration
- Supabase for database + auth + storage
- Claude Code / Antigravity for autonomous agent execution
- Code Rabbit CLI for automated bug fixing + PR reviews

## Agents to Build
{agents_str}

## Requirements
{requirements or 'See industry playbook defaults.'}

## Primary Goal
{goal or f'Create a fully autonomous AI system that handles the top 3 agent workflows for {business_name} with minimal human intervention.'}

## Deliverables Required
1. **n8n Workflow JSON** — importable, production-ready, all nodes connected
2. **Supabase Schema SQL** — tables, RLS policies, indexes
3. **Coolify Deploy Commands** — exact commands to deploy to Hostinger
4. **Environment Variables List** — all .env vars needed
5. **Agent System Prompts** — optimised prompts for each AI node
6. **Testing Checklist** — how to verify each agent works

## Constraints
- Self-hosted only — no cloud-lock tools
- All secrets via environment variables (never hardcoded)
- Every workflow must have error handling + alerting
- Code Rabbit must review every generated code file
- Follow Cook OS model: Skills + Context + Tools

Build it. Make it autonomous. Make it fast to deploy.
"""


# ─── Coolify Deploy Commands ──────────────────────────────────────────────────

def generate_coolify_commands(business_name: str, coolify_url: str = "",
                               coolify_token: str = "", domain: str = "",
                               api_key: str = "", industry: str = "",
                               agents: list = None) -> str:
    if api_key and domain:
        try:
            system = """You are a DevOps expert specialising in self-hosted deployments on Linux VPS using Coolify and Docker. You write precise bash scripts and deployment commands. Output only the deployment script — no preamble."""

            user = f"""Write complete Coolify deployment commands for:

Business: {business_name}
Industry: {industry}
Domain: {domain}
Coolify URL: {coolify_url or 'https://YOUR_COOLIFY_URL'}
Agents: {', '.join((agents or [])[:5])}

Include:
1. SSH connection command
2. Coolify installation check / install command
3. Complete docker-compose.yml for n8n with all required environment variables
4. Coolify API deploy command with correct headers
5. n8n workflow import instructions
6. Health check verification commands
7. SSL/HTTPS setup via Coolify
8. Firewall rules (ports 22, 80, 443, 8000, 5678)
9. Backup configuration for n8n data volume
10. Troubleshooting commands if deployment fails

Use {domain} as the domain throughout. Make every command copy-paste ready."""

            return _call_claude(api_key, system, user, max_tokens=3000)
        except Exception:
            pass

    return _template_coolify_commands(business_name, coolify_url, coolify_token, domain)


def _template_coolify_commands(business_name, coolify_url, coolify_token, domain):
    slug = business_name.lower().replace(" ", "-").replace("/", "-")
    return f"""# Coolify Deploy Commands — {business_name}
# Generated by Adam's System Builder

# ─── 1. Connect to your Hostinger VPS ───────────────────────────────────────
ssh root@{domain or 'YOUR_VPS_IP'}

# ─── 2. Install Coolify (if not already installed) ───────────────────────────
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash

# ─── 3. Deploy n8n via Coolify Dashboard ─────────────────────────────────────
# 1. Open https://{domain or 'YOUR_VPS_IP'}:8000
# 2. New Resource → Docker Compose
# 3. Paste the docker-compose.yml below
# 4. Set all environment variables in the Coolify UI
# 5. Click Deploy

# ─── 4. docker-compose.yml ───────────────────────────────────────────────────
cat > docker-compose-{slug}.yml << 'EOF'
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${{N8N_HOST}}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://{domain or 'YOUR_DOMAIN'}/
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${{N8N_USER}}
      - N8N_BASIC_AUTH_PASSWORD=${{N8N_PASSWORD}}
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=${{SUPABASE_HOST}}
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=${{SUPABASE_USER}}
      - DB_POSTGRESDB_PASSWORD=${{SUPABASE_PASSWORD}}
      - N8N_ENCRYPTION_KEY=${{N8N_ENCRYPTION_KEY}}
    volumes:
      - n8n_data:/home/node/.n8n
volumes:
  n8n_data:
EOF

# ─── 5. Verify deployment ─────────────────────────────────────────────────────
curl https://{domain or 'YOUR_DOMAIN'}/healthz
# Expected: {{"status":"ok"}}
"""


# ─── Supabase Schema SQL ──────────────────────────────────────────────────────

def generate_supabase_sql(business_name: str, industry: str,
                           agents: list = None, api_key: str = "",
                           requirements: str = "") -> str:
    if api_key:
        try:
            system = """You are a Supabase / PostgreSQL database architect. You write production-ready SQL schemas. Output ONLY raw SQL — no explanation, no markdown fences, just the SQL statements."""

            user = f"""Write a complete Supabase SQL schema for:

Business: {business_name}
Industry: {industry}
Agents: {', '.join((agents or [])[:8])}
Requirements: {requirements or 'Standard agentic AI system tables.'}

Include:
1. Enable uuid-ossp extension
2. Core tables: projects, interactions, settings
3. Industry-specific tables relevant to {industry} (e.g. for healthcare: patients, appointments; for real estate: properties, leads)
4. Agent-specific tables for each of the agents listed
5. Row Level Security (RLS) enabled on all tables
6. RLS policies for service role (full access) 
7. Indexes on all foreign keys and commonly queried columns
8. created_at / updated_at timestamps on every table
9. auto-update trigger function for updated_at
10. Useful views for reporting

Use snake_case for all table and column names. UUID primary keys everywhere. JSONB for flexible metadata columns."""

            return _call_claude(api_key, system, user, max_tokens=4096)
        except Exception:
            pass

    return _template_supabase_sql(business_name, industry)


def _template_supabase_sql(business_name, industry):
    slug = industry.lower().replace(" ", "_").replace("/", "_")
    return f"""-- Supabase Schema — {business_name}
-- Generated by Adam's System Builder

create extension if not exists "uuid-ossp";

create table if not exists projects (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  industry text,
  business_type text,
  status text default 'active',
  config jsonb default '{{}}',
  owner text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

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

create table if not exists settings (
  key text primary key,
  value text,
  updated_at timestamptz default now()
);

create table if not exists {slug}_clients (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  email text,
  phone text,
  metadata jsonb default '{{}}',
  created_at timestamptz default now()
);

alter table projects enable row level security;
alter table interactions enable row level security;
alter table settings enable row level security;

create policy "Service role access" on projects for all using (true);
create policy "Service role access" on interactions for all using (true);
create policy "Service role access" on settings for all using (true);

create index if not exists idx_interactions_project on interactions(project_id);
create index if not exists idx_interactions_created on interactions(created_at desc);
create index if not exists idx_projects_owner on projects(owner);

create or replace function update_updated_at()
returns trigger as $$ begin new.updated_at = now(); return new; end; $$ language plpgsql;

create trigger projects_updated_at before update on projects
  for each row execute procedure update_updated_at();
"""


# ─── Client Handover Document ─────────────────────────────────────────────────

def generate_client_handover(business_name: str, industry: str, agents: list,
                              goal: str = "", integrations: dict = None,
                              tech_stack: list = None, api_key: str = "",
                              requirements: str = "") -> str:
    integrations = integrations or {}
    tech_stack = tech_stack or ["n8n", "Supabase", "Coolify"]
    active_integrations = [k for k, v in integrations.items() if v]

    if api_key:
        try:
            context = _project_context(business_name, industry, agents, goal, requirements, tech_stack)
            system = """You are a professional technical writer specialising in AI system documentation for non-technical business owners. You write clear, friendly, jargon-free handover documents that make clients feel confident using their new system."""

            user = f"""Write a complete client handover document for this project:

{context}
Active integrations: {', '.join(active_integrations) or 'Standard stack'}

The document must include these sections:

# {business_name} — AI System Handover Document

## Welcome & What We Built
Plain English explanation of what the system does and the value it delivers.

## Your Agents — What Each One Does
For every agent, explain in 2-3 plain English sentences what it does, when it runs, and what the output is. No tech jargon.

## How to Use Your System Day-to-Day
Step-by-step guide for daily use. What does the client need to do (if anything)? What happens automatically?

## Logging In & Access
Where to log in, what credentials they need, who has access.

## What's Automated vs What Needs a Human
Clear table: Left column = "Handled automatically", Right column = "You need to action this"

## What to Do If Something Stops Working
Simple 5-step troubleshooting guide. Plain English. When to contact Adam.

## Your Tech Stack — Plain English
Brief explanation of each tool (n8n, Supabase, etc.) in one sentence each. What it does, why it's there.

## Contact & Support
Leave placeholders for Adam's contact details.

## Glossary
10 key terms explained simply.

Write in a warm, professional tone. Use headers, bullet points, and short paragraphs. The client should feel confident and empowered after reading this."""

            return _call_claude(api_key, system, user, max_tokens=4096)
        except Exception as e:
            return _template_client_handover(business_name, industry, agents, goal, active_integrations, str(e))

    return _template_client_handover(business_name, industry, agents, goal, active_integrations)


def _template_client_handover(business_name, industry, agents, goal, integrations, error=""):
    agents_str = "\n".join([f"- **{a}** — Handles {a.lower()} automatically." for a in agents])
    note = f"\n\n> ⚠️ Add your Anthropic API key in Settings to generate a fully personalised AI version of this document. Error: {error}" if error else \
           "\n\n> 💡 Add your Anthropic API key in Settings to generate a fully personalised AI version of this document."
    return f"""# {business_name} — AI System Handover Document
Generated by Adam's System Builder | {datetime.utcnow().strftime('%Y-%m-%d')}
{note}

---

## Welcome & What We Built

We have built a custom agentic AI system for **{business_name}** in the **{industry}** sector.

**Primary Goal:** {goal or f'Automate the key workflows for {business_name} to save time and reduce manual effort.'}

Your system runs 24/7 automatically — handling tasks, sending communications, and logging everything without you needing to be involved.

---

## Your Agents — What Each One Does

{agents_str}

---

## How to Use Your System Day-to-Day

1. Log in to your n8n dashboard to monitor active workflows
2. Check the Supabase dashboard to view all logged interactions
3. Receive alerts via your configured notification channel (Slack/SMS/Email)
4. Review the weekly summary report (sent automatically)

---

## What's Automated vs What Needs a Human

| ✅ Handled Automatically | 👤 You Need to Action |
|---|---|
| Incoming enquiry responses | Reviewing escalated complex cases |
| Data logging & reporting | Approving large transactions |
| Routine notifications & reminders | Updating business rules / content |
| Standard workflow execution | Monthly system review with Adam |

---

## What to Do If Something Stops Working

1. Check your n8n dashboard for any failed executions (shown in red)
2. Check that your VPS is running (ping your domain)
3. Verify your API keys haven't expired in the Settings page
4. Check the error log in Supabase → interactions table
5. Contact Adam if the issue persists

---

## Contact & Support

**Your System Builder:** Adam Cross
**Email:** [adam@example.com]
**Response time:** Within 24 hours on business days

---
*Built with Adam's System Builder — n8n · Supabase · Coolify · Claude AI*
"""
