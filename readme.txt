Radiant Launch: Open-Source xAI Campaign Agent
Streamlit Grok License: MIT Python 3.12+
Radiant Launch is a standalone, open-source AI agent powered by Grok (xAI) that empowers small businesses—especially dental clinics and service providers—to launch personalized marketing campaigns in minutes. From "Dental Glow Up" service bookings to future product upsells like whitening kits, it generates responsive landing pages, syncs leads (mock CRM default, optional MCP for HubSpot/Salesforce), and mocks deployments (Netlify/WordPress).
No complex setups: Edit config.yaml for custom hooks (e.g., dental templates with diverse smile images). Fork and contribute—make it your own!
Features

Grok-Powered Personalization: AI generates descriptions, features, and CTAs tailored to your brief (e.g., "Diverse smiles for men/women in whitening campaigns").
Dual Mode: Services (booking-focused) or Products (shoppable)—future-proof for retail.
CRM Hooks: Mock for testing; optional MCP middleware for real syncs (HubSpot, Salesforce, Sugar).
Landing Pages: Bootstrap HTML with hero images, feature cards, CTAs—SEO-ready, mobile-responsive.
Error-Resilient: Logging, fallbacks for API fails—keeps running.
Open-Source Extensible: YAML config for templates/overrides; add tools like X posting.

Quick Start

Clone/Fork Repo:textgit clone https://github.com/yourusername/radiant-launch-agent.git
cd radiant-launch-agent
Install Deps:textpython -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
pip install -r requirements.txt
Setup Secrets (.env):textGROK_API_KEY=your_xai_key_from_x.ai/api
# Optional: HUBSPOT_PAT=your_token for MCP
Config Hooks (config.yaml—edit for dental tweaks):YAMLcredentials:  # Auth (hash pw at bcrypt.online)
  usernames:
    test_user:
      email: your@email.com
      name: Test Manager
      password: $2b$12$hashed_pw_here
cookie:
  name: radiant_auth
  key: random_key_change_me
  expiry_days: 30
enable_mcp: false  # Toggle for real CRM
mcp_url: "http://localhost:8080/mcp/v1"
custom_templates:
  services:
    features: ["Whitening Magic", "Aligner Glow", "Confidence Boost"]
    cta: "Book Your Glow Consult"
  products:
    features: ["Home Kit Bundle", "Floss Pro Pack", "Smile Guard"]
    cta: "Shop Now & Save 20%"
grok_prompt_override: "Tailor for dental: Emphasize diverse smiles (men/women)."
Mock Leads (mock_crm.json—add your sample data):JSON[
  {"email": "john@dental.com", "name": "John Glow", "industry": "dental"},
  {"email": "sarah@clinic.com", "name": "Sarah Smile", "industry": "health"}
]
Run Locally:textstreamlit run campaign_manager.py
Login, brief "Dental Glow Up", launch—Grok gens page, "syncs" leads, downloads HTML.


Usage

Launch Campaign:
Sidebar: Enter brief (e.g., "Whitening service for busy pros").
Mode: "Services (Now)" for bookings.
Filter: "dental" to "pull" mock leads.
Hit "Launch with Grok!"—get HTML page, report, stats.

Customize:
Edit config.yaml for templates/CTAs.
Enable MCP: Set enable_mcp: true, add URL—syncs real leads.

Deploy Pages: Mock URL generated; integrate Netlify CLI for real deploys.

Example Output Page Snippet:
HTML<h1>Dental Glow Up</h1>
<p>Transform your smile—affordable whitening for pros.</p>
<a href="/book" class="btn">Book Now</a>
Testing
Robust testing ensures reliability—unit tests for tools, integration/E2E for full flows.
Running Tests

Install Test Deps:textpip install pytest pytest-mock
Run All:textpytest -v  # Verbose; covers test_campaign_manager.py (unit) and test_integration.py (E2E)
Expected: 100% pass rate ("OK" summary).

Specific File:textpytest test_campaign_manager.py -v  # Unit tests for CRM/content/deploy
pytest test_integration.py -v  # E2E launch flows (success/error/MCP/template)

Test Coverage

Unit: Tools (sync_crm pull/push, generate_content fallback, deploy_page).
E2E: Full invoke (brief → Grok → CRM → HTML → deploy), MCP errors, custom templates, Grok failures.
Coverage Report: pip install pytest-cov && pytest --cov=. --cov-report=html (opens HTML report in browser).

Add tests for new features—keep coverage >90%!
Architecture

Core: Streamlit UI + LangChain/Grok for orchestration.
Tools: CRM sync (mock/MCP), content gen (Grok JSON parse), deploy mock.
Hooks: YAML config for biz-specific (dental services/products).
Error Handling: Fallbacks, logging for robustness.
Tests: Unit (tools) + E2E (full launch) in test_*.py—run pytest.

Contributing

Fork repo.
Branch: git checkout -b feature/dental-hooks.
Commit: git commit -m "Add aligner template".
Push/PR: git push origin feature/dental-hooks.

Guidelines: Keep it lightweight, add tests, update README.
License
MIT—free to fork, modify, commercialize. See LICENSE.
Roadmap

Real xAI Flux image gen hook.
X posting tool for auto-shares.
Full MCP server script for easy self-host.

Questions? Open an issue or PR. Launch radiant campaigns! 🚀🌟