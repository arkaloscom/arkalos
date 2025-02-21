

# Arkalos Beta 2 - The Python Framework for AI & Data Artisans

[![PyPI version](https://img.shields.io/pypi/v/arkalos)](https://pypi.org/project/arkalos/)
[![PyPI Downloads](https://static.pepy.tech/badge/arkalos)](https://pepy.tech/projects/arkalos)

Docs: [https://arkalos.com/docs/installation/](https://arkalos.com/docs/installation/)

Folder Structure: [https://arkalos.com/docs/structure/](https://arkalos.com/docs/structure/)

Git: [https://github.com/arkaloscom/arkalos](https://github.com/arkaloscom/arkalos)

<div style="display: flex;">

<div style="padding: 10px;">
<img src="https://arkalos.com/assets/img/arkalos-logo.png" alt="Arkalos Logo" width="100">
</div>

<div style="flex: 1; padding: 10px;">
<p>Arkalos is an easy-to-use framework for data analysis, data science, building data apps, warehouses, AI agents, robots, ML, training LLMs with elegant syntax. It just works.</p>
</div>

</div>



## Why Arkalos? Beginner- and Micro Business-Friendly

Arkalos makes it easy to get started, whether you're a beginner non-coder, scientist, or AI engineer.

And small businesses can now leverage the power of data warehouses and AI on a budget and at speed.

No more struggling with:

* Setting up your environment
* Spending hours searching for basic solutions
* Following instructions that just don't work
* Manually installing and managing packages
* Writing too much code for basic tasks
* Resolving import issues and errors
* Figuring out how to structure custom code and modules
* Growing from Jupyter Notebooks to full AI apps and pipelines
* Connecting data sources and building data warehouses
* Training AI models and running LLMs locally
* Collaborating with teams or sharing code across devices

The name Arkalos combines "Arc" and the Greek word "Kalos," meaning "a beautiful journey through the data."


<img src="https://arkalos.com/assets/img/arkalos-ai-web.png" alt="Arkalos Web UI">



## Beautiful Syntax and Documentation

Arkalos offers:

* Beautiful Documentation: Clear, concise, and easy-to-follow guides, even if you are learning coding, Python or data science.
* Elegant Syntax: Simple code that's easy to write and read.
* Reliable Performance: Works out of the box with minimal setup.


```bash
uv init
uv add arkalos
uv run arkalos init

# That's it. Your workspace is ready to write code. It just works!
```


## Key Features

* **🚀 Modern Python Workflow:**<br> Built with modern Python practices, libraries, and a package manager. Perfect for non-coders and AI engineers.

* **🛠️ Hassle-Free Setup:**<br> No more struggling with environment setups, package installs, or import errors.

* **🤝 Easy Collaboration & Folder Structure:**<br> Share code across devices or with your team. Built-in workspace folder and file structure. Know where to put each file.

* **📓 Jupyter Notebook Friendly:**<br> Start with a simple notebook and easily transition to scripts, full apps, or microservices.

* **📊 Built-in Data Warehouse:**<br> Connect to Notion, Airtable, Google Drive, and more. Uses SQLite for a local, lightweight data warehouse.

* **🤖 AI, LLM & RAG Ready. Talk to Your Own Data:**<br> Train AI models, run LLMs, and build AI and RAG pipelines locally. Fully open-source and compliant. Built-in AI agent helps you to talk to your own data in natural language.

* **🐞 Debugging and Logging Made Easy:**<br> Built-in utilities and Python extensions like `var_dump()` for quick variable inspection, `dd()` to halt code execution, and pre-configured logging for notices and errors.

* **🧩 Extensible Architecture:**<br> Easily extend Arkalos components and inject your own dependencies with a modern, modular software design.

* **🔗 Seamless Microservices:**<br> Deploy your own data or AI microservice like ChatGPT without the need to use external APIs to integrate with your existing platforms effortlessly.

* **🔒 Data Privacy & Compliance First:**<br> Run everything locally with full control. No need to send sensitive data to third parties. Fully open-source under the MIT license, and perfect for organizations needing data governance.



## Truly Open-Source, Local, and Compliant

Arkalos helps individuals and businesses analyze data securely, with everything running locally and fully compliant with regulations.



## Free Built-In Data Warehouse and Integrations

Data warehouses are centralized repositories that connect multiple data sources to enable AI and analytics.

Not every case needs complex and expensive tools like Snowflake or BigQuery. With Arkalos, you get a simple, local data warehouse right out of the box!

Arkalos connects seamlessly to popular tools like Notion, Airtable, Google Drive, and HubSpot.

Automatically detects and generates the schema.

And syncs data into your own data warehouse.

config/data_sources.py
```python title="config/data_sources.py"
    'airtable': {
        'enabled': True,
        'api_key': env('AIRTABLE_API_KEY'),
        'base_id': env('AIRTABLE_BASE_ID'),
        'tables': env('AIRTABLE_TABLES'),
    }
```

SQLite is used as the default local data warehouse.

.env
```ini title=".env"
DWH_ENGINE=SQLite
DWH_SCHEMA_PATH=data/dwh/schema.sql
DWH_SQLITE_PATH=data/dwh/dwh.db
```

```bash
uv run arkalos dwh sync
```

scripts/etl/my_script.py
```python
from arkalos.data.extractors.airtable_extractor import AirtableExtractor
# or for Notion
# from arkalos.data.extractors.notion_extractor import NotionExtractor
from arkalos.workflows.etl_workflow import ETLWorkflow

wf = ETLWorkflow(AirtableExtractor)
wf.run(drop_tables=True)
```

And that's it! Your data is imported automatically, ready for analysis or AI pipelines, and even accessible offline.




## Built-in HTTP API Server - Launch a Python Data or AI Microservice

Python is the world's fastest-growing programming language thanks to its rich ecosystem of data, AI, and scientific libraries.

Arkalos lets freelancers, consultants, startups, businesses, and even governments add powerful data and AI capabilities to their products and platforms. Simply launch Arkalos as a microservice and integrate it seamlessly into your architecture.

```bash
uv run arkalos serve
```



## Build Custom AI Agents Without Abstraction

app/ai/actions/what_is_my_ip_action.py
```python
import socket
from arkalos.ai import AIAction

class WhatIsMyIpAction(AIAction):

    NAME = 'what_is_my_ip'
    DESCRIPTION = 'Determine the user IP'
    
    def run(self, message):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
```

app/ai/actions/calc_action.py
```python
from arkalos.ai import AIAction

class CalcAction(AIAction):

    NAME = 'calc'
    DESCRIPTION = 'Calculate mathematical expressions and provide a single value'
    
    def run(self, message):
        prompt = f"""
            ### Instructions:
            You are a calculator. Calculate mathematical expression and provide an answer

            ### Input:
            Generate a proper mathematical formula based on this question `{message}`.

            And calculate the final answer to this formula.
                    
            ### Response:
            Respond as a single mathematical value to the expression
        """
        return self.generateTextResponse(prompt)
```


## Multi-Task Agent - Determine Which Action to Take

app/ai/agents/multi_agent.py
```python
from arkalos.ai import AIAgent, TextToSQLAction

from app.ai.actions import WhatIsMyIpAction, CalcAction



class MultiAgent(AIAgent):
    
    NAME = 'MultiAgent'

    DESCRIPTION = 'An Agent that understands the intent, determines which task to perform and runs it.'

    GREETING = 'Hi, I am a MultiAgent. I can tell your IP address, do basic math calculations or transform text to SQL.'
    
    ACTIONS = [
        WhatIsMyIpAction, 
        CalcAction, 
        TextToSQLAction
    ]

    def processMessage(self, message):
        response = f"Determining the intent and which task to run...\n"
        which_action = self.whichAction(message)
        response += f"Based on your question, I determined this task: {which_action}\n"
        response += f"Running this task...\n"
        output = self.runAction(which_action, message)
        response += f"Task output: {output}\n"
        return response
```



## Test Your Models and Agents Locally

scripts/ai/agent.py
```python
from app.ai.agents import MultiAgent

agent = MultiAgent()
agent.runConsole()
```

```bash
uv run scripts/ai/agent.py
```



## Beautiful Documentation - Get Started Today

Read the [Documentation](https://arkalos.com)



## Appreciations

We are grateful to the communities behind [these open-source projects on which we depend](https://arkalos.com/appreciations).



## License

MIT License.

Check the LICENSE file for answers to common questions.
