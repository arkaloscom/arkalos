

# The Python Framework for AI & Data Artisans

<div style="display: flex;">

<div style="padding: 10px;">
<img src="/assets/img/arkalos-logo.png" alt="Arkalos Logo" width="100">
</div>

<div style="flex: 1; padding: 10px;">
<p>Arkalos is an easy-to-use framework for data analysis, building data apps, warehouses, AI agents, robots, ML, training LLMs with elegant syntax. It just works.</p>
</div>

</div>




## Why Arkalos?

Are you tired of:

* Reading bad documentation?
* Spending hours searching for basic solutions?
* Following instructions that just don't work?

Arkalos fixes all of that. It offers:

* Beautiful Documentation: Clear, concise, and easy-to-follow guides.
* Elegant Syntax: Simple code that's easy to write and read.
* Reliable Performance: Works out of the box with minimal setup.

```bash
uv init
uv add arkalos
uv run arkalos init

# That's it. Your workspace is ready to write code. It just works!
```

Whether you're analyzing data, building AI agents, or training LLMs, Arkalos makes it easy and enjoyable.

The name Arkalos combines "Arc" and the Greek word "Kalos," meaning "a beautiful journey through the data."





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




## Modern Python Workflow, Ready Out-of-the-Box

Arkalos makes it easy to get started, whether you're a non-coder, scientist, or AI engineer.

No more struggling with:

* Setting up your environment
* Manually installing and managing packages
* Writing too much code for basic tasks
* Resolving import issues and errors
* Figuring out how to structure custom code and modules
* Growing from Jupyter Notebooks to full AI apps and pipelines
* Connecting data sources and building data warehouses
* Training AI models and running LLMs locally
* Collaborating with teams or sharing code across devices




## Truly Open-Source, Local, and Compliant

Arkalos helps individuals and businesses analyze data securely, with everything running locally and fully compliant with regulations.




## Free Built-In Data Warehouse and Integrations

Data warehouses are centralized repositories that connect multiple data sources to enable AI and analytics.

Not every case needs complex and expensive tools like Snowflake or BigQuery. With Arkalos, you get a simple, local data warehouse right out of the box!

Arkalos connects seamlessly to popular tools like Notion, Airtable, Google Drive, and HubSpot.

Automatically detects and generates the schema.

And syncs data into your own data warehouse.

```python title="config/data_sources.py"
    'airtable': {
        'enabled': True,
        'api_key': env('AIRTABLE_API_KEY'),
        'base_id': env('AIRTABLE_BASE_ID'),
        'tables': env('AIRTABLE_TABLES'),
    }
```

SQLite is used as the default local data warehouse.

```ini title=".env"
DWH_ENGINE=SQLite
DWH_SCHEMA_PATH=data/dwh/schema.sql
DWH_SQLITE_PATH=data/dwh/dwh.db
```

```python
uv run arkalos dwh sync
```

And that's it! Your data is imported automatically, ready for analysis or AI pipelines, and even accessible offline.





## Launch a Python Data or AI Microservice

Python is the world's fastest-growing programming language thanks to its rich ecosystem of data, AI, and scientific libraries.

Arkalos lets freelancers, consultants, startups, businesses, and even governments add powerful data and AI capabilities to their products and platforms. Simply launch Arkalos as a microservice and integrate it seamlessly into your architecture.




## Get Started Today

Read the [Documentation](https://arkalos.com)



## Appreciations

We are grateful to the communities behind [these open-source projects on which we depend](https://arkalos.com/appreciations).



## License

MIT License. Check the LICENSE file for details, annotations and answers to common questions.
