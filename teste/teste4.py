import pandas as pd
import ast
import os
import numpy as np
import nest_asyncio
from dotenv import load_dotenv
import wandb
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import EvaluationDataset
from ragas.metrics import (
    LLMContextRecall, Faithfulness, FactualCorrectness,
    LLMContextPrecisionWithoutReference, NoiseSensitivity,
    ResponseRelevancy, ContextEntityRecall
)
from ragas.run_config import RunConfig

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

import plotly.graph_objects as go
import time  # For timestamp-based file naming


# Apply nest_asyncio to avoid event loop issues
nest_asyncio.apply()


# Load environment variables from .env file
load_dotenv()


# Access API keys and validate them
#anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

#Meu code
openai_api_key = os.environ.get('OPENAI_API_KEY')


if not openai_api_key:
    raise ValueError("OpenAI API Key not found.")
#if not anthropic_api_key:
    raise ValueError("Anthropic API Key not found.")


# Initialize W&B logging
wandb.init(project="RAGAS_Model_Evaluation", name="multi_model_visualization")


# List of generation and embedding models to compare
gen_models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
embed_models = ["openai"]


# Helper function to select the appropriate generation model
def get_generation_model(gen_model_name):
    if "claude" in gen_model_name:
        return LangchainLLMWrapper(ChatAnthropic(model=gen_model_name))
    return LangchainLLMWrapper(ChatOpenAI(model=gen_model_name))


# Create a reusable RunConfig
my_run_config = RunConfig(max_workers=1, timeout=180) # preventing rate limiting 


# Function to log radar plots
def log_radar_plot(metrics_data, model_pair):
    fig = go.Figure()
    metrics = list(metrics_data.keys())
    values = list(metrics_data.values())
    metrics += [metrics[0]]  # Close radar loop
    values += [values[0]]


    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=metrics,
        fill='toself',
        name=model_pair
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1], tickvals=[0, 0.5, 1])),
        title=dict(text=f"Radar Plot - {model_pair}", x=0.5, xanchor='center'),
        showlegend=True
    )


    # Save and log radar plot
    timestamp = int(time.time())
    radar_html_path = f"./radar_plot_{model_pair}_{timestamp}.html"
    fig.write_html(radar_html_path, auto_play=False)
    wandb.log({f"Radar Plot {model_pair}": wandb.Html(radar_html_path)})


# Function to log heatmaps
def log_heatmap(heatmap_data, metric_name):
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=["Low", "Medium", "High"],
        y=[f"{gen}_{embed}" for gen, embed in zip(gen_models, embed_models)],
        colorscale='YlGnBu', showscale=True
    ))
    fig.update_layout(
        title=f"{metric_name} Heatmap",
        xaxis_title="Score Bin", yaxis_title="Model Pair"
    )


    heatmap_html_path = f"./heatmap_{metric_name}.html"
    fig.write_html(heatmap_html_path, auto_play=False)
    wandb.log({f"{metric_name} Heatmap": wandb.Html(heatmap_html_path)})


# Helper function to bin metric values
def bin_metric_values(values):
    bins = [0, 0.3, 0.75, 1.01]
    return np.clip(np.digitize(values, bins) - 1, 0, 2)


# Store heatmap data across models
all_heatmap_data = {metric: [] for metric in ["factual_correctness", "faithfulness", "answer_relevancy"]}


# Loop through all combinations of generation and embedding models
for gen_model, embed_model in zip(gen_models, embed_models):
    model_pair = f"{gen_model}_{embed_model}"
    output_eval_csv = f"./evaluation_results_{model_pair}.csv"


    # Check if evaluation results exist
    if os.path.exists(output_eval_csv):
        print(f"Loading existing results for {model_pair}.")
        df = pd.read_csv(output_eval_csv)
    else:
        print(f"Running evaluation for {model_pair}...")
        input_csv_path = f"./results_{model_pair}.csv"
        data = pd.read_csv(input_csv_path)


        # Parse retrieved contexts from the CSV
        if 'retrieved_contexts' in data.columns:
            data['retrieved_contexts'] = data['retrieved_contexts'].apply(ast.literal_eval)


        # Prepare evaluation dataset
        eval_data = data[['user_input', 'reference', 'response', 'retrieved_contexts']].to_dict(orient="records")
        eval_dataset = EvaluationDataset.from_list(eval_data)


        # Get the appropriate generation model for evaluation
        evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-2024-08-06"))


        # Evaluate the dataset
        metrics = [
            LLMContextRecall(), FactualCorrectness(), Faithfulness(),
            LLMContextPrecisionWithoutReference(), NoiseSensitivity(),
            ResponseRelevancy(), ContextEntityRecall()
        ]
        results = evaluate(dataset=eval_dataset, metrics=metrics, llm=evaluator_llm, run_config=my_run_config)
        df = results.to_pandas()
        df.to_csv(output_eval_csv, index=False)


    # Collect binned values for heatmaps
    for metric_name in ["factual_correctness", "faithfulness", "answer_relevancy"]:
        binned_values = bin_metric_values(df[metric_name])
        counts = [binned_values.tolist().count(i) for i in range(3)]
        all_heatmap_data[metric_name].append(counts)


    # Log radar plot for the current model pair
    radar_metrics_data = {
        "Context Recall": df["context_recall"].mean(),
        "Factual Correctness": df["factual_correctness"].mean(),
        "Faithfulness": df["faithfulness"].mean(),
        "Context Precision": df["llm_context_precision_without_reference"].mean(),
        "Noise Sensitivity": df["noise_sensitivity_relevant"].mean(),
        "Answer Relevancy": df["answer_relevancy"].mean(),
        "Context Entity Recall": df["context_entity_recall"].mean(),
    }
    log_radar_plot(radar_metrics_data, model_pair)


# Log heatmaps for all metrics across models
for metric_name, heatmap_data in all_heatmap_data.items():
    log_heatmap(heatmap_data, metric_name)


# Finalize W&B logging
wandb.finish()
