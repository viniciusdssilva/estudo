from langchain.agents import AgentExecutor, create_openai_tools_agent
from data_visualization.toolkit import create_plotly_chart, repair_plotly_code
from data_visualization.toolkit import prompt


def create_plotly_agent(llm, max_interations=12, verbose=True):

    toolkit = [create_plotly_chart, repair_plotly_code]

    agent = create_openai_tools_agent(
        llm,
        toolkit,
        prompt
    )

    plotly_agent = AgentExecutor(
        agent=agent,
        tools=toolkit,
        verbose=verbose,
        max_iterations=max_interations
    )

    return plotly_agent
