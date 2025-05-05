import os
import random

def get_random_response(category: str) -> str:
    base_path = "data/response_examples"
    file_path = os.path.join(base_path, f"{category}.txt")

    if not os.path.exists(file_path):
        return "We're looking into your request and will follow up shortly."

    with open(file_path, "r") as file:
        responses = [line.strip() for line in file.readlines() if line.strip()]

    return random.choice(responses) if responses else "Thanks for reaching out."