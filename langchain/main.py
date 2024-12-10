import langchain_helper as lch
import streamlit as st

st.title("Gerador de nomes de animais de estimação")

user_animal_type = st.sidebar.selectbox("Selecione o tipo do seu animal de estimação?", {"Cachorro", "Gato", "Vaca", "Pássaro", "Hamster"}, index = None, placeholder = "Selecione uma opção")  

user_pet_color = st.sidebar.text_area("Qual a cor do seu animal de estimação?", max_chars = 15) 

if user_animal_type and user_pet_color:
    response = lch.generate_pet_name(user_animal_type, user_pet_color)
    st.text(response['pet_name'])
    st.text("Fato curioso sobre seu tipo de animal de estimação: ")
    st.text(lch.langchain_agent(user_animal_type))

