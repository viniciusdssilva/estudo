import os
import pandas as pd

def convert_excel_to_csv(directory):
    """Converte todos os arquivos Excel de um diretório para CSV."""
    for file in os.listdir(directory):
        if file.endswith(".xlsx"):
            file_path = os.path.join(directory, file)
            csv_file = os.path.splitext(file)[0] + ".csv"
            csv_path = os.path.join(directory, csv_file)
            
            try:
                df = pd.read_excel(file_path)
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                print(f"Convertido: {file} -> {csv_file}")
            except Exception as e:
                print(f"Erro ao converter {file}: {e}")


directory = "./planilhas"  # Substitua pelo caminho do diretório desejado
convert_excel_to_csv(directory)

#Isso funciona, mas eu não lembro como gerei o arquivo .jsonl
'''from ragas import EvaluationDataset

from datasets import load_dataset

dataset = EvaluationDataset.from_jsonl("document.jsonl")

dataset.to_csv("document.csv")'''
