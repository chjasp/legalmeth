# DB connection
from sqlalchemy import text

import torch
from transformers import AutoTokenizer, AutoModel
from backend.db_interface import DatabaseInterface

project_id = "steam-378309"
region = "europe-west3"
instance_name = "legalm"

DB_NAME = "pubmed"
DB_USER = "postgres"
DB_PASS = "bdpass"
DB_PORT = "5432"

INSTANCE_CONNECTION_NAME = f"{project_id}:{region}:{instance_name}"
print(f"Your instance connection name is: {INSTANCE_CONNECTION_NAME}")

db_interface = DatabaseInterface(INSTANCE_CONNECTION_NAME, DB_USER, DB_PASS, DB_NAME)

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

sim_query = """SELECT caption, 1 - (embedding <=> :user_query_embedding) AS similarity
               FROM huberman_embeddings
               WHERE 1 - (embedding <=> :user_query_embedding) > :similarity_threshold
               ORDER BY similarity DESC
               LIMIT :num_matches
            """

def get_embedding(query):
    # query = "I want to understand how breathing really works"
    inputs = tokenizer(query, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state[:, 0, :].numpy()
        embedding = embedding.reshape(768,)

    return embedding

def get_matches(query):
    similarity_threshold = 0.5
    num_matches = 3

    user_query_embedding = get_embedding(query)
    user_query_embedding = str(user_query_embedding.tolist())

    sim_query_values = {
                        "user_query_embedding": user_query_embedding,
                        "similarity_threshold": similarity_threshold,
                        "num_matches": num_matches
                        }

    results = []

    try:
        with db_interface.pool.connect() as connection:
            cursor = connection.execute(text(sim_query), sim_query_values)
            results = cursor.fetchall()
            connection.commit()
    except Exception as e:
        print("EXCEPTION THROWN")
        print(e)
        connection.rollback()

    processed_results = [dict(row._mapping) for row in results]
            
    if len(processed_results) == 0:
        raise Exception("Did not find any results. Adjust the query parameters.")
    return processed_results