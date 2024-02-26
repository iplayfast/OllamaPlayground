from crewai import Crew, Process

from agents import AINewsLetterAgents
from tasks import AINewsletterTasks
from file_io import save_markdown
from langchain_community.llms import Ollama
from dotenv import load_dotenv
load_dotenv()

llm = Ollama(model="mistral")

agents = AINewsLetterAgents()
tasks = AINewsletterTasks()

editor = agents.editor_agent(llm)
news_fetcher = agents.news_fetcher_agent(llm)
news_analyzer = agents.news_analyzer_agent(llm)
newsletter_compiler = agents.newsletter_compiler_agent(llm)

fetch_news_task = tasks.fetch_news_task(news_fetcher)
analyzed_news_task = tasks.analyze_news_task(news_analyzer,[fetch_news_task])
compiled_newsletter_task = tasks.compile_newsletter_task(
    newsletter_compiler,[analyzed_news_task],callback_function=save_markdown)

crew = Crew(
    agents=[editor,news_fetcher,news_analyzer,newsletter_compiler],
    tasks=[fetch_news_task,analyzed_news_task,compiled_newsletter_task],
    process=Process.hierarchical,
    manager_llm = llm
)

results = crew.kickoff()
print("Crew work results:")
print(results)