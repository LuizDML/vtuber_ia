# Assistente Virtual MIRAI

A asssitente foi idealizada em Python 3.10, utilizando a fala e convertendo para texto (STT), submetendo o texto em um modelo de IA rodando local em Ollama (por enquanto Mistral), capturando a resposta e convertendo o texto para audio (TTS) e então respondendo.

O projeto tem dois objetivos principais:
- Servir como conclusão de um bootcamp da DIO
- Ir além e implementar funções extras para tornar

Ele está sendo realizado em conjunto entre eu e o @HarukiMuraka, sendo ideia dele expandir o modelo.

Entra as expansões futuras:
- Pedir para o modelo LLM gerar tags que possam ser importadas em programas como Live2D ou VMagicMirror
- Criar um avatar em um desses programas citados
- Integrar com um LLM em nuvem para respostas mais rápidas
- Dar função de abrir aplicativos
- Dar função de capturar tela e responder questões referentes à captura

# Referente aos requisitos para operação
- Python 3.10
- Estar com o Ollama instalado e com o modelo indicado rodando;
- Criar uma pasta models e inserir nessa pasta os modelos de voz do vosk em pt
