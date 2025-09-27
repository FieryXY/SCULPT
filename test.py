# Write a quick script that asks tinyllama what 2+3 is and prints the result
# Use the ollama library
import ollama

response = ollama.chat(model='tinyllama', messages=[
    {'role': 'user', 'content': 'Explain quantum computing in simple terms.'},
])

print(response)

