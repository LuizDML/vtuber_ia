#!/usr/bin/env python3
"""
M.I.R.A.I - Assistente Virtual
Sistema completo com seleção de dispositivo de áudio
"""

from ouvir_sr import ouvir, MiraiListener
from ia import responder, MiraiAI
from falar import MiraiTTS, get_tts_engine
import time
import sys
import signal
import json
import os
import speech_recognition as sr  # Adicione esta linha se não existir

class MiraiAssistant:
    def __init__(self, config_file="mirai_config.json"):
        """Inicializa todos os componentes do MIRAI"""
        print("🤖 Inicializando M.I.R.A.I...")
        print("="*50)
        
        # Carrega configuração
        self.config_file = config_file
        self.config = self.load_config()
        
        # Inicializa componentes
        self.listener = MiraiListener()
        self.ai = MiraiAI(model=self.config.get("model", "mistral"))
        self.tts = get_tts_engine()
        
        # Aplica configurações salvas
        self.apply_config()
        
        # Estado
        self.active = True
        self.conversation_mode = False
        
        # Configura tratamento de Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
        print("\n✅ M.I.R.A.I inicializada com sucesso!")
        print("="*50)
    
    def load_config(self):
        """Carrega configuração do arquivo"""
        default_config = {
            "audio_device": None,
            "mic_device": None,
            "volume": 1.0,
            "speed": 1.1,
            "model": "mistral",
            "temperature": 1.1,
            "wake_words": ["mirai", "mirá", "miray"],
            "auto_listen": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Mescla com padrão
                    for key in default_config:
                        if key not in loaded_config:
                            loaded_config[key] = default_config[key]
                    return loaded_config
            except:
                print(f"⚠️  Erro ao carregar configuração, usando padrão")
        
        return default_config
    
    def save_config(self):
        """Salva configuração no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print("💾 Configuração salva")
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def apply_config(self):
        """Aplica configurações carregadas"""
        # Configura áudio de saída (fone)
        if self.config.get("audio_device") is not None:
            self.tts.select_audio_device(self.config["audio_device"])
        
        self.tts.set_voice_settings(
            volume=self.config.get("volume", 1.0),
            rate=self.config.get("speed", 1.1)
        )
        
        # Aplica temperatura no modelo AI
        self.ai.config["temperature"] = self.config.get("temperature", 1.1)
    
    

    def signal_handler(self, sig, frame):
        """Lida com Ctrl+C"""
        print("\n\n🛑 Interrupção recebida...")
        self.active = False
        sys.exit(0)
    
    def greeting(self):
        """Saudação inicial"""
        greeting_text = (
            "Hai! Konnichiwa! Eu sou a Mirai, sua assistente virtual. "
            "Como posso ajudar você hoje?"
        )
        print(f"🤖 Mirai: {greeting_text}")
        self.tts.speak(greeting_text)
    
    def process_command(self, command, text_only=False):
        """Processa um comando do usuário"""
        if not command:
            return
        
        print(f"\n🎯 Comando recebido: {command}")
        
        # Obtém resposta da IA
        print("🧠 Pensando...")
        response = self.ai.responder(command)
        
        if response:
            # Mostra a resposta
            print(f"🤖 Mirai: {response}")
            
            # Se não for modo texto apenas, fala a resposta
            if not text_only:
                print("🎤 Falando...")
                self.tts.speak(response)
        else:
            error_msg = "Desculpe, não consegui processar isso."
            print(f"⚠️  {error_msg}")
            if not text_only:
                self.tts.speak(error_msg)
    
    def audio_setup_wizard(self):
        """Assistente de configuração de áudio de saída"""
        print("\n" + "="*50)
        print("🎧 CONFIGURAÇÃO DE SAÍDA DE SOM")
        print("="*50)
        print("Vamos configurar onde a Mirai vai falar...")
        
        # Lista dispositivos
        self.tts.show_audio_devices_menu()
        
        # Teste interativo
        print("\n🔊 Vamos testar os dispositivos:")
        print("1. Primeiro teste o dispositivo padrão")
        self.tts.test_audio_device()
        
        heard = input("\n🎧 Você ouviu o som? (S/N): ").strip().upper()
        
        if heard != 'S':
            print("\n🔍 Vamos tentar outros dispositivos...")
            devices = self.tts.audio_devices
            
            for device in devices:
                if not device['default']:
                    print(f"\nTestando: {device['name']} (ID: {device['id']})")
                    self.tts.test_audio_device(device['id'])
                    
                    heard = input("Você ouviu o som deste dispositivo? (S/N): ").strip().upper()
                    if heard == 'S':
                        self.tts.select_audio_device(device['id'])
                        self.config["audio_device"] = device['id']
                        self.save_config()
                        print("✅ Dispositivo selecionado e salvo!")
                        return
        else:
            print("✅ Dispositivo padrão funcionando")
    
    def text_only_mode(self):
        """Modo somente texto - sem áudio"""
        print("\n" + "="*50)
        print("📝 MODO SOMENTE TEXTO")
        print("="*50)
        print("ℹ️  Digite seus comandos e receba respostas em texto.")
        print("💡 Digite 'sair' para voltar ao menu principal")
        print("="*50)
        
        while True:
            try:
                user_input = input("\n👤 Você: ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit', 'voltar']:
                    print("↩️  Voltando ao menu principal...")
                    break
                
                if not user_input:
                    continue
                
                # Processa o comando em modo texto
                self.process_command(user_input, text_only=True)
                
            except KeyboardInterrupt:
                print("\n↩️  Voltando ao menu principal...")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
    
    def listen_continuous_mode(self):
        """Modo de conversação contínua sem wake word"""
        print("\n🎧 Modo de conversação contínua")
        print("⚠️  Não precisa dizer 'Mirai' antes dos comandos")
        print("⏰ Timeout de 10 segundos entre comandos")
        print("⏸️  Pressione Ctrl+C para voltar ao menu\n")
        
        while self.active:
            try:
                # Escuta um único comando
                command = self.listener.listen_single_command(
                    device_index=self.config.get("mic_device")
                )
                
                if command and self.active:
                    # Processa o comando
                    self.process_command(command)
                    
                    # Pequena pausa para evitar detecção do próprio áudio
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                print("\n🛑 Retornando ao menu...")
                break
            except Exception as e:
                print(f"⚠️  Erro: {e}")
                time.sleep(2)
    
    def listen_wake_word_mode(self):
        """Modo com wake word"""
        print("\n🎧 Modo de escuta com wake word")
        print(f"🎯 Palavras de ativação: {self.config.get('wake_words', ['mirai'])}")
        print("⏸️  Pressione Ctrl+C para voltar ao menu\n")
        
        while self.active:
            try:
                # Aguarda wake word
                command = self.listener.listen_for_wake_word(
                    device_index=self.config.get("mic_device"),
                    timeout=30
                )
                
                if command and self.active:
                    # Processa o comando
                    self.process_command(command)
                    
                    # Pequena pausa para evitar detecção do próprio áudio
                    time.sleep(0.5)
                    
            except KeyboardInterrupt:
                print("\n🛑 Retornando ao menu...")
                break
            except Exception as e:
                print(f"⚠️  Erro: {e}")
                time.sleep(2)
    
    def audio_output_settings(self):
        """Configurações de saída de áudio (fone)"""
        while True:
            print("\n" + "="*50)
            print("🎧 CONFIGURAÇÕES DE FONE/ALTO-FALANTE")
            print("="*50)
            print("1. Testar dispositivo de áudio")
            print("2. Selecionar dispositivo de áudio")
            print("3. Ajustar volume e velocidade")
            print("4. Listar dispositivos disponíveis")
            print("5. Voltar")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.tts.test_audio_device()
                input("\nPressione Enter para continuar...")
            
            elif choice == "2":
                if self.tts.select_audio_device():
                    self.config["audio_device"] = self.tts.selected_device
                    self.save_config()
            
            elif choice == "3":
                try:
                    vol = float(input("Volume (0.0-2.0, padrão=1.0): ") or "1.0")
                    speed = float(input("Velocidade (0.5-2.0, padrão=1.1): ") or "1.1")
                    self.tts.set_voice_settings(vol, speed)
                    self.config["volume"] = vol
                    self.config["speed"] = speed
                    self.save_config()
                except:
                    print("❌ Valores inválidos")
            
            elif choice == "4":
                self.tts.show_audio_devices_menu()
                input("\nPressione Enter para continuar...")
            
            elif choice == "5":
                break
            
            else:
                print("❌ Opção inválida")
    
    def mic_settings(self):
        """Configurações de microfone"""
        while True:
            print("\n" + "="*50)
            print("🎤 CONFIGURAÇÕES DE MICROFONE")
            print("="*50)
            print("1. Testar microfone")
            print("2. Selecionar microfone")
            print("3. Listar microfones disponíveis")
            print("4. Voltar")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.test_microphone()
            
            elif choice == "2":
                self.select_microphone()
            
            elif choice == "3":
                self.listener.list_audio_devices()
                input("\nPressione Enter para continuar...")
            
            elif choice == "4":
                break
            
            else:
                print("❌ Opção inválida")
    
    def test_microphone(self):
        """Testa o microfone atual"""
        print("\n🎤 Teste de microfone")
        print("Fale algo por 3 segundos...")
        
        try:
            with sr.Microphone(device_index=self.config.get("mic_device")) as source:
                self.listener.adjust_for_noise(source, duration=1)
                
                print("🎤 Gravando...")
                audio = self.listener.recognizer.listen(
                    source, 
                    timeout=3,
                    phrase_time_limit=3
                )
                
                print("✅ Áudio capturado! Teste concluído.")
                print(f"🔊 Nível de energia: {self.listener.recognizer.energy_threshold:.1f}")
                
        except Exception as e:
            print(f"❌ Erro ao testar microfone: {e}")
    
    def select_microphone(self):
        """Seleciona o microfone"""
        print("\n🎤 Seleção de microfone")
        
        try:
            mics = sr.Microphone.list_microphone_names()
            
            if not mics:
                print("❌ Nenhum microfone encontrado!")
                return
            
            print("\n📋 Microfones disponíveis:")
            for i, name in enumerate(mics):
                default_mark = " (PADRÃO)" if i == 0 else ""
                print(f"[{i}] {name}{default_mark}")
            
            try:
                choice = input("\nSelecione o número do microfone (Enter para padrão): ").strip()
                
                if choice == "":
                    self.config["mic_device"] = None
                    print("✅ Usando microfone padrão")
                elif choice.isdigit() and 0 <= int(choice) < len(mics):
                    self.config["mic_device"] = int(choice)
                    print(f"✅ Microfone selecionado: {mics[int(choice)]}")
                else:
                    print("❌ Opção inválida")
                    return
                
                self.save_config()
                
            except ValueError:
                print("❌ Número inválido")
                
        except Exception as e:
            print(f"❌ Erro ao listar microfones: {e}")
    
    def personality_settings(self):
        """Configurações de personalidade da IA"""
        while True:
            print("\n" + "="*50)
            print("🧠 CONFIGURAÇÕES DE PERSONALIDADE")
            print("="*50)
            print(f"Temperatura atual: {self.config.get('temperature', 1.1)}")
            print("ℹ️  Temperatura controla a criatividade:")
            print("   - 0.0: Mais determinística, previsível")
            print("   - 1.0: Equilibrado")
            print("   - 2.0: Mais criativa, aleatória")
            print("="*50)
            print("1. Ajustar temperatura")
            print("2. Ver dicas de uso")
            print("3. Voltar")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                try:
                    temp = float(input("Nova temperatura (0.0-2.0): ") or "1.1")
                    temp = max(0.0, min(2.0, temp))  # Limita entre 0 e 2
                    self.config["temperature"] = temp
                    self.save_config()
                    print(f"✅ Temperatura ajustada para: {temp}")
                    
                    # Atualiza no modelo AI
                    self.ai.config["temperature"] = temp
                    
                except ValueError:
                    print("❌ Valor inválido. Use números como 0.5, 1.0, 1.5")
            
            elif choice == "2":
                print("\n💡 Dicas de uso da temperatura:")
                print("• 0.2-0.5: Para tarefas factuais, respostas diretas")
                print("• 0.7-1.0: Conversação normal, equilíbrio criativo")
                print("• 1.2-1.5: Respostas mais criativas e variadas")
                print("• 1.7-2.0: Máxima criatividade, pode ser imprevisível")
                input("\nPressione Enter para continuar...")
            
            elif choice == "3":
                break
            
            else:
                print("❌ Opção inválida")
    
    def settings_menu(self):
        """Menu de configurações principal"""
        while True:
            print("\n" + "="*50)
            print("⚙️  CONFIGURAÇÕES DA MIRAI")
            print("="*50)
            print("1. Configurações de Fone/Alto-falante")
            print("2. Configurações de Microfone")
            print("3. Configurações de Personalidade")
            print("4. Voltar ao menu principal")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.audio_output_settings()
            
            elif choice == "2":
                self.mic_settings()
            
            elif choice == "3":
                self.personality_settings()
            
            elif choice == "4":
                break
            
            else:
                print("❌ Opção inválida")
    
    def main_menu(self):
        """Menu principal interativo"""
        print("\n" + "="*50)
        print("🤖 M.I.R.A.I - MENU PRINCIPAL")
        print("="*50)
        print("1. Iniciar com Wake Word")
        print("2. Iniciar sem Wake Word (conversa contínua)")
        print("3. Iniciar somente texto")
        print("4. Configurações")
        print("5. Sair")
        print("="*50)
    
    def run(self):
        """Executa a assistente"""
        # Verificação inicial de áudio
        print("🔊 Verificando sistema de áudio...")
        if not self.tts.audio_devices:
            print("⚠️  Nenhum dispositivo de áudio encontrado!")
            print("💡 A funcionalidade de voz pode não funcionar corretamente.")
        
        # Menu principal
        while self.active:
            self.main_menu()
            
            try:
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "1":
                    self.listen_wake_word_mode()
                
                elif choice == "2":
                    self.listen_continuous_mode()
                
                elif choice == "3":
                    self.text_only_mode()
                
                elif choice == "4":
                    self.settings_menu()
                
                elif choice == "5":
                    print("👋 Até logo!")
                    self.active = False
                
                else:
                    print("❌ Opção inválida")
                    
            except KeyboardInterrupt:
                print("\n↩️  Voltando ao menu...")
                continue
            except Exception as e:
                print(f"❌ Erro: {e}")

# Função principal simplificada
def main():
    """Ponto de entrada principal"""
    print("="*50)
    print("🤖 M.I.R.A.I - Assistente Virtual")
    print("="*50)
    
    assistant = MiraiAssistant()
    
    # Saudação inicial
    print("\n🎯 Dica: Vamos construir um futuro incrível juntos!")
    
    # Executa
    assistant.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 M.I.R.A.I encerrada")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)