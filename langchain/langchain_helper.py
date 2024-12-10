from langchain_openai.llms import OpenAI 
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType

load_dotenv()

def generate_pet_name(animal_type, pet_color):
    llm_name = OpenAI(temperature = 0.7)

    prompt_template_name = PromptTemplate(
        input_variables = ['animal_type', 'pet_color'],
        template = "Eu tenho um {animal_type} como animal de estimação. Ele é da cor {pet_color}. Eu gostaria de cinco nomes legais para o meu animal de estimação. Forneça apenas os nomes, não é necessário explicar suas escolhas."
    )

    name_chain = LLMChain(llm = llm_name, prompt = prompt_template_name, output_key = "pet_name")

    response = name_chain({'animal_type': animal_type, 'pet_color': pet_color})

    return response

def langchain_agent(animal_type):
    llm_name = OpenAI(temperature = 0.5)
    
    tools_name = load_tools(["wikipedia", "llm-math"], llm = llm_name)
    tools_name[0].api_wrapper.lang = 'br'

    agent_name = initialize_agent(
        tools_name, llm_name, agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose = True
    )

    result_en = agent_name.run(
        "Eu tenho um " + animal_type + " como animal de estimação. Diga um fato curioso sobre esse tipo de animal. Limite sua resposta a no máximo 256 caracteres."
    )

    result_br = llm_name(prompt = "Traduza o texto a seguir do inglês para o português do Brasil: " + result_en)

    return result_br

#if __name__ == "__main__":
#    langchain_agent()

