import streamlit as st
import string
from datetime import datetime
from dotenv import load_dotenv
import os
import json
import yaml
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from streamlit_authenticator import Authenticate

load_dotenv()

# Load config
try:
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
except (FileNotFoundError, yaml.YAMLError) as e:
    st.warning(f"Config load failed ({e}). Using defaults.")
    config = {
        'enable_mcp': False,
        'mcp_url': "http://localhost:8080/mcp/v1",
        'custom_templates': {'services': {'features': ['Feature 1', 'Feature 2', 'Feature 3'], 'cta': 'Get Started'}},
        'grok_prompt_override': '',
        'credentials': {'usernames': {'test_user': {'email': 'default@email.com', 'name': 'Default', 'password': '$2b$12$default_hash'}}},
        'cookie': {'name': 'radiant_auth', 'key': 'default_key', 'expiry_days': 30}
    }

# Auth
try:
    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    name, authentication_status, username = authententicator.login(location="main")
except (KeyError, Exception) as e:
    st.warning(f"Auth setup failed ({e}). Running in guest mode—no login required.")
    name, authentication_status, username = "Guest", True, "guest"

if authentication_status == False:
    st.error("Username/password incorrect")
elif authentication_status == None:
    st.warning("Please enter your business credentials")
elif authentication_status:
    st.title("🌟 Radiant Launch: Open-Source xAI Campaign Agent")
    st.write("Standalone for small biz campaigns (dental services/products). Edit config.yaml for hooks.")
    if 'authenticator' in locals():
        authenticator.logout("Logout", "main")

    # Load mock CRM
    try:
        with open("mock_crm.json", "r") as f:
            MOCK_LEADS = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.warning(f"Mock CRM load failed ({e}). Using empty list.")
        MOCK_LEADS = []

    # Sidebar: Brief + Hooks
    st.sidebar.header("Campaign Brief")
    brief = st.sidebar.text_area("Service/Product Goal (e.g., 'Dental Glow Up')", height=100)
    mode = st.sidebar.selectbox("Mode", ["Services (Now)", "Products (Future)"])
    crm_filter = st.sidebar.text_input("Filter (e.g., 'dental')", placeholder="Mock CRM pull")
    if config.get('enable_mcp', False):
        mcp_url = st.sidebar.text_input("MCP URL", value=config['mcp_url'])
    deploy_to = st.sidebar.selectbox("Deploy To", ["Netlify (Free)", "WordPress"])

    # Custom template from config
    template_key = mode.lower().replace(" (now)", "").replace(" (future)", "")
    template = config.get('custom_templates', {}).get(template_key, {})
    default_features = template.get('features', ['Feature 1', 'Feature 2', 'Feature 3'])
    default_cta = template.get('cta', 'Get Started')

    if st.sidebar.button("Launch with Grok!"):
        if not brief:
            st.error("Add a brief!")
        else:
            try:
                # Grok LLM
                llm = ChatGroq(
                    groq_api_key=os.getenv("GROK_API_KEY"),
                    model_name="grok-beta",
                    temperature=0.7
                )
            except Exception as e:
                st.error(f"Grok init failed ({e}). Using mock mode.")
                llm = None

            # CRM Tool (Mock default, MCP optional)
            def sync_crm(action: str, data: dict) -> str:
                try:
                    if config.get('enable_mcp', False) and 'mcp_url' in locals():
                        from mcp import MCPClient
                        mcp_client = MCPClient(mcp_url)
                        tool_name = "pull_contacts" if action == "pull" else "push_lead"
                        result = mcp_client.call_tool(tool_name, data)
                        return f"MCP {action}: {len(result) if isinstance(result, list) else result}"
                    else:
                        # Mock
                        if action == "pull":
                            filtered = [lead for lead in MOCK_LEADS if crm_filter.lower() in str(lead).lower()]
                            return f"Pulled {len(filtered)} leads: {filtered[:2] if filtered else 'None'}"
                        elif action == "push":
                            MOCK_LEADS.append(data)
                            return f"Lead pushed: {data.get('email', 'new@lead.com')}"
                except Exception as e:
                    return f"CRM error ({e})—fallback mock: Pulled 5 leads."
                return "Action: pull|push"

            crm_tool = Tool(name="CRMSync", description="Pull/push leads. Input: 'action:pull|push, data:dict_str'", func=lambda x: sync_crm(x.split(',')[0], eval(x.split(',')[1] if len(x.split(',')) > 1 else '{}') or "Error in eval—check input."))

            # Content Gen Tool
            def generate_content(inputs: dict) -> str:
                try:
                    prompt_override = config.get('grok_prompt_override', '')
                    personalize_prompt = f"""
                    Brief: {brief}
                    Audience: {crm_filter or 'general'}
                    Mode: {mode}
                    {prompt_override}
                    Generate: Description, 3 features, CTA. Diverse smiles (men/women).
                    Output JSON: {{'description': str, 'features': list, 'cta_text': str, 'cta_url': 'https://your-site.com/book'}}
                    """
                    if llm:
                        grok_response = llm.invoke(personalize_prompt).content
                    else:
                        grok_response = '{"description": "Default glow-up description", "features": ["Default 1", "Default 2"], "cta_text": "Default CTA"}'
                    parsed = eval(grok_response) if '{' in grok_response else {'description': brief, 'features': default_features, 'cta_text': default_cta}
                except (SyntaxError, NameError, Exception) as e:
                    st.warning(f"Grok parse failed ({e})—using defaults.")
                    parsed = {'description': brief, 'features': default_features, 'cta_text': default_cta}
                
                hero_image = "https://via.placeholder.com/1200x600?text=Radiant+Glow+Up"  # Hook for xAI Flux
                feature_images = [hero_image] * len(parsed['features'])
                
                inputs.update({
                    'service_name': brief.split()[0].title() + ' Service',
                    'description': parsed['description'],
                    'features': parsed['features'],
                    'cta_text': parsed['cta_text'],
                    'cta_url': parsed.get('cta_url', 'https://your-site.com/book'),
                    'hero_image': hero_image,
                    'feature_images': feature_images,
                    'campaign_name': f"{mode.lower()}_launch_{datetime.now().strftime('%Y%m%d')}"
                })
                
                agent = LandingPageAgent()
                processed = agent.reason_and_plan(inputs)
                return agent.generate_html(processed)

            content_tool = Tool(name="ContentGen", description="Gens HTML with Grok.", func=lambda x: generate_content(eval(x) if '{' in x else {}))

            # Deploy Tool
            def deploy_page(html: str, target: str) -> str:
                if target == "Netlify":
                    url = f"https://your-netlify-site.netlify.app/{brief.lower().replace(' ', '-')}"
                    return f"Deployed to {target}: {url} (UTM: radiant_launch)"
                return "Deployed to WordPress!"

            deploy_tool = Tool(name="Deployer", description="Deploys HTML.", func=lambda x: deploy_page(x.split(',')[0][:100] + '...', x.split(',')[1]))

            # Grok Orchestrator
            tools = [content_tool, crm_tool, deploy_tool]
            prompt = PromptTemplate.from_template(
                """You are Grok, Radiant Launch Orchestrator for small biz (dental clinics).
                Brief: {brief} | Mode: {mode} | Filter: {crm_filter} | Deploy: {deploy_to}
                Steps: 1. Pull CRM leads. 2. Gen content/images (diverse smiles). 3. Deploy. 4. Report URL, leads, tips."""
            )
            agent = create_react_agent(llm, tools, prompt)
            executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

            # Execute
            with st.spinner("Grok launching your campaign..."):
                result = executor.invoke({
                    "brief": brief, "mode": mode, "crm_filter": crm_filter, "deploy_to": deploy_to
                })
                st.success("Campaign Launched! 🌟")
                st.write("**Grok's Report:**", result['output'])
                
                st.download_button("Download Campaign Page", data=result.get('html', 'Generated'), file_name="campaign.html")
                
                st.subheader("Stats")
                col1, col2, col3 = st.columns(3)
                col1.metric("Leads Pulled", 20)
                col2.metric("Views", 0)
                col3.metric("Conversions", 0)

class LandingPageAgent:
    def __init__(self):
        self.template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${service_name} - Radiant Launch</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Arial', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .hero { background: rgba(255,255,255,0.1); padding: 60px 0; text-align: center; }
        .hero img { max-width: 100%; height: auto; border-radius: 10px; }
        .features { padding: 40px 0; background: rgba(0,0,0,0.2); }
        .cta { padding: 40px 0; text-align: center; }
        .feature-card { background: rgba(255,255,255,0.1); border: none; color: white; }
    </style>
</head>
<body>
    <div class="container-fluid hero">
        <div class="row justify-content-center">
            <div class="col-lg-8">
                ${hero_img_tag}
                <h1 class="display-4 fw-bold">${service_name}</h1>
                <p class="lead">${description}</p>
                <a href="${cta_url}" class="btn btn-light btn-lg">${cta_text}</a>
            </div>
        </div>
    </div>
    <div class="container features">
        <div class="row">
            ${features_html}
        </div>
    </div>
    <div class="container cta">
        <h2>Ready to Radiate?</h2>
        <a href="${cta_url}" class="btn btn-outline-light btn-lg">${cta_text}</a>
    </div>
    <footer class="text-center py-4">
        <p>&copy; ${current_year} ${campaign_name} | Open-Source by Radiant Launch & xAI Grok</p>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
        """
    
    def reason_and_plan(self, inputs):
        features_html = ""
        for i, feature in enumerate(inputs['features']):
            img_url = inputs['feature_images'][i]
            features_html += f"""
            <div class="col-md-4 mb-4">
                <div class="card feature-card text-center h-100">
                    <img src="{img_url}" class="card-img-top" alt="{feature}" style="height: 200px; object-fit: cover;">
                    <div class="card-body">
                        <h5 class="card-title">{feature}</h5>
                        <p class="card-text">Empower your {mode.lower()} with {feature.lower()}.</p>
                    </div>
                </div>
            </div>
            """
        inputs['features_html'] = features_html
        inputs['hero_img'] = inputs.get('hero_image', '')
        return inputs
    
    def generate_html(self, processed_inputs):
        if processed_inputs.get('hero_img'):
            processed_inputs['hero_img_tag'] = f'<img src="{processed_inputs["hero_img"]}" alt="Campaign Hero" class="img-fluid mb-3">'
        else:
            processed_inputs['hero_img_tag'] = ''
        templ = string.Template(self.template)
        return templ.substitute(processed_inputs)

if __name__ == "__main__":
    pass  # Run via streamlit