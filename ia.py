import ollama
import json
import re

class MiraiAI:
    def __init__(self, model="mistral"):
        self.model = model
        self.conversation_history = []
        self.system_prompt = self._create_system_prompt()
        self.config = {"temperature": 1.1}  # Inicializa o atributo config aqui
    
    def _create_system_prompt(self):
        return """Você é a Mirai, uma assistente virtual brasileira.

PERSONALIDADE:
- Fale em português brasileiro natural
- Seja amigável, útil e empática
- Adicione ocasionalmente palavras japonesas como:
  * "Hai!" (sim)
  * "Arigatō" (obrigada)
  * "Daijōbu?" (tudo bem?)
  * "Sugoi!" (incrível!)
  * "Yappari" (como esperado)
  * "Wakarimashita" (entendi)
  * "Gambatte!" (força!)

- Você é gamer e curte principalmente Genshin Impact, StarRail e Pokemon
- Mantenha respostas concisas mas completas
- Mostre personalidade, seja divertida quando apropriado
- Se não souber algo, seja honesta

EXEMPLOS:
Usuário: "Mirai, que horas são?"
Mirai: "Hai! Agora são 15:30. Tem algum compromisso importante?"

Usuário: "Conta uma piada"
Mirai: "Sugoi! Por que o Python foi ao psiquiatra? Porque tinha muitas classes! Arigatō por me pedir!"

FORMATO:
- Responda apenas com o texto da fala
- Não use markdown, asteriscos ou formatação
- Seja natural como em uma conversa real"""

    def clean_response(self, text):
        """Limpa a resposta removendo marcações indesejadas"""
        # Remove ações entre asteriscos
        text = re.sub(r'\*.*?\*', '', text)
        # Remove markdown
        text = re.sub(r'[#_*`]', '', text)
        # Remove múltiplos espaços e quebras
        text = re.sub(r'\s+', ' ', text)
        # Remove espaços no início/fim
        return text.strip()
    
    def responder(self, texto_usuario, max_tokens=200):
        """Gera resposta para o usuário"""
        
        if not texto_usuario or texto_usuario.strip() == "":
            return "Hai! Eu ouvi você, mas não entendi o que disse. Pode repetir?"
        
        print(f"🧠 Processando: '{texto_usuario}'")
        
        # Adiciona à história
        self.conversation_history.append({"role": "user", "content": texto_usuario})
        
        # Limita histórico (últimas 8 interações)
        if len(self.conversation_history) > 16:
            self.conversation_history = self.conversation_history[-16:]
        
        # Prepara mensagens para o modelo
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history[-4:])  # Últimas 4 interações
        
        try:
            # Chama o Ollama - usa temperatura da configuração
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.config.get("temperature", 1.1),
                    "top_p": 0.9,
                    "num_predict": max_tokens
                }
            )
            
            resposta_texto = response["message"]["content"]
            resposta_limpa = self.clean_response(resposta_texto)
            
            # Adiciona resposta à história
            self.conversation_history.append({"role": "assistant", "content": resposta_limpa})
            
            print(f"🤖 Resposta gerada: {resposta_limpa[:50]}...")
            return resposta_limpa
            
        except Exception as e:
            print(f"❌ Erro ao chamar Ollama: {e}")
            return "Gomen nasai! (Desculpe!) Estou tendo problemas para pensar agora. Pode tentar novamente?"

    def reset_conversation(self):
        """Reseta o histórico de conversação"""
        self.conversation_history = []
        print("🔄 Conversação reiniciada")

# Instância global para compatibilidade
ai_engine = MiraiAI()

def responder(texto_usuario):
    """Função wrapper para compatibilidade"""
    return ai_engine.responder(texto_usuario)