"""
Módulo de escuta usando SpeechRecognition com VAD embutido
Não precisa do webrtcvad - SpeechRecognition já tem detecção de voz
"""
import speech_recognition as sr
import json
import os

# Configurações
MODEL_PATH = "models/vosk-model-small-pt-0.3"
WAKE_VARIATIONS = [
    "mirai", "mira", "mirá", "mírai", "miray", "mirrai", 
    "mira e", "mirai assistente", "ei mirai", "olá mirai",
    "ok mirai", "mirahi", "mirrei", "mirei", "miray assistente",
    "teste", "tchau", "oi mirai", "hey mirai", "fala mirai", "mír ai",
    "mir ai"
 ]

class MiraiListener:
    def __init__(self, model_path=MODEL_PATH):
        """
        Inicializa o listener com SpeechRecognition
        """
        print("🎧 Inicializando sistema de escuta...")
        
        # Inicializa o reconhecedor
        self.recognizer = sr.Recognizer()
        
        # Configurações de sensibilidade
        self.recognizer.energy_threshold = 300  # Ajuste conforme seu microfone
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # Segundos de silêncio para considerar fim da fala
        
        # Configura o modelo Vosk
        self.model_path = model_path
        if not os.path.exists(model_path):
            print(f"⚠️  Modelo Vosk não encontrado em: {model_path}")
            print("📥 Baixe modelos em: https://alphacephei.com/vosk/models")
            print("📁 Coloque na pasta 'models/'")
        
        # Lista dispositivos de áudio
        self.list_audio_devices()
    
    def list_audio_devices(self):
        """Lista dispositivos de áudio disponíveis"""
        print("\n🎤 Dispositivos de microfone disponíveis:")
        try:
            mics = sr.Microphone.list_microphone_names()
            for i, name in enumerate(mics):
                print(f"  [{i}] {name}")
        except:
            print("  Não foi possível listar dispositivos")
        
        print("\n📢 Para usar um dispositivo específico, ajuste no código.")
    
    def adjust_for_noise(self, source, duration=1):
        """Ajusta para ruído ambiente"""
        print("🔊 Ajustando para ruído ambiente...")
        try:
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"✅ Energia ajustada para: {self.recognizer.energy_threshold:.1f}")
        except Exception as e:
            print(f"⚠️  Não foi possível ajustar ruído: {e}")
    
    def listen_for_wake_word(self, device_index=None, timeout=10):
        """
        Escuta continuamente até detectar a palavra de ativação
        
        Args:
            device_index: Índice do dispositivo de microfone
            timeout: Timeout em segundos para cada tentativa de escuta
        """
        print(f"\n{'='*50}")
        print("🛌 M.I.R.A.I aguardando palavra de ativação...")
        print("🎯 Diga: 'Mirai' seguido do seu comando")
        print(f"{'='*50}")
        
        with sr.Microphone(device_index=device_index) as source:
            # Ajusta para ruído ambiente
            self.adjust_for_noise(source)
            
            while True:
                try:
                    print(f"\n📞 Escutando... (timeout: {timeout}s)")
                    
                    # Escuta áudio com timeout
                    # O VAD do SpeechRecognition já filtra silêncio automaticamente
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=10  # Máximo 5 segundos por frase
                    )
                    
                    print("🎧 Áudio capturado, processando...")
                    
                    """ # Reconhece usando Vosk
                    try:
                        # Método 1: Usando recognize_vosk
                        text = self.recognizer.recognize_vosk(
                            audio, 
                            language="pt"
                        )
                        
                        # Parse do resultado JSON
                        result = json.loads(text)
                        text_lower = result.get("text", "").lower()
                        
                    except:
                        # Método 2: Fallback para recognize_google (menos preciso)
                        print("⚠️  Vosk falhou, usando Google como fallback...")
                        text_lower = self.recognizer.recognize_google(
                            audio, 
                            language="pt-BR"
                        ).lower() """
                    
                    try:
                        # Método 2: Fallback para recognize_google (menos preciso)
                        print("⚠️  Vosk falhou, usando Google como fallback...")
                        text_lower = self.recognizer.recognize_google(
                            audio, 
                            language="pt-BR"
                        ).lower() 
                    except:
                        print("Não foi possível iniciar o reconhecimento d voz :'(")

                    if text_lower:
                        #print(f"🎧 Ouvido: '{text_lower}'")
                        
                        # Verifica se contém palavra de ativação
                        for wake_word in WAKE_VARIATIONS:
                            if wake_word in text_lower:
                                print(f"🔔 Palavra de ativação detectada: '{wake_word}'")
                                
                                # Extrai o comando (remove a wake word)
                                command = self.extract_command(text_lower, wake_word)
                                
                                if command:
                                    print(f"🎯 Comando extraído: '{command}'")
                                else:
                                    command = "olá"  # Comando padrão se só disse "Mirai"
                                    print("ℹ️  Comando padrão: 'olá, não seja tímido! Baka!'")
                                
                                return command
                    
                    print("⏭️  Nenhuma palavra de ativação detectada, continuando...")
                    
                except sr.WaitTimeoutError:
                    # Timeout normal - continua escutando
                    print("⏰ Timeout, continuando escuta...")
                    continue
                    
                except sr.UnknownValueError:
                    print("❓ Não foi possível entender o áudio")
                    continue
                    
                except sr.RequestError as e:
                    print(f"⚠️  Erro no serviço de reconhecimento: {e}")
                    continue
                    
                except KeyboardInterrupt:
                    print("\n👋 Interrompido pelo usuário")
                    raise
                    
                except Exception as e:
                    print(f"⚠️  Erro inesperado: {e}")
                    continue
    
    def extract_command(self, full_text, wake_word):
        """
        Extrai o comando removendo a palavra de ativação
        
        Args:
            full_text: Texto completo reconhecido
            wake_word: Palavra de ativação detectada
        
        Returns:
            Comando limpo
        """
        # Remove a wake word
        clean_text = full_text.replace(wake_word, "", 1)
        
        # Remove palavras comuns que podem vir depois da wake word
        remove_words = ["assistente", "por favor", "pode", "poderia", "oi", "olá"]
        for word in remove_words:
            clean_text = clean_text.replace(word, "", 1)
        
        # Limpa espaços extras
        clean_text = clean_text.strip()
        
        # Se o texto ficou vazio ou muito curto, retorna None
        if len(clean_text) < 2:
            return None
        
        return clean_text
    
    def listen_single_command(self, device_index=None):
        """
        Escuta um único comando (sem wake word)
        Útil para depois da ativação
        """
        print("\n🎤 O que deseja...")
        
        with sr.Microphone(device_index=device_index) as source:
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=10,
                    phrase_time_limit=10
                )
                
                # Reconhece com Vosk
                text = self.recognizer.recognize_vosk(audio, language="pt")
                result = json.loads(text)
                return result.get("text", "")
                
            except sr.WaitTimeoutError:
                print("⏰ Timeout ao esperar comando")
                return None
            except Exception as e:
                print(f"⚠️  Erro ao reconhecer comando: {e}")
                return None

# Função de conveniência para compatibilidade
def ouvir(device_index=None):
    """
    Função principal para escutar wake word
    Mantém compatibilidade com código existente
    """
    listener = MiraiListener()
    return listener.listen_for_wake_word(device_index=device_index)

# Teste direto
if __name__ == "__main__":
    print("🔧 Teste do sistema de escuta")
    print("="*50)
    
    listener = MiraiListener()
    
    # Testa com dispositivo padrão (None) ou específico
    dispositivo = None  # Mude para número se quiser específico
    
    print("\n🎤 Iniciando teste...")
    print("🎯 Diga: 'Mirai, que horas são?' ou similar")
    print("⏳ Pressione Ctrl+C para sair\n")
    
    try:
        while True:
            comando = listener.listen_for_wake_word(device_index=dispositivo)
            if comando:
                print(f"\n✅ Comando recebido: {comando}")
                print("\n" + "="*50)
    except KeyboardInterrupt:
        print("\n\n👋 Teste finalizado")