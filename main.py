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
            "volume": 1.0,
            "speed": 1.1,
            "model": "mistral",
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
        # Configura áudio
        if self.config.get("audio_device") is not None:
            self.tts.select_audio_device(self.config["audio_device"])
        
        self.tts.set_voice_settings(
            volume=self.config.get("volume", 1.0),
            rate=self.config.get("speed", 1.1)
        )
    
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
    
    def process_command(self, command):
        """Processa um comando do usuário"""
        if not command:
            return
        
        print(f"\n🎯 Comando recebido: {command}")
        
        # Obtém resposta da IA
        print("🧠 Pensando...")
        response = self.ai.responder(command)
        
        if response:
            # Fala a resposta
            print(f"🤖 Mirai: {response}")
            print("🎤 Falando...")
            self.tts.speak(response)
        else:
            error_msg = "Desculpe, não consegui processar isso."
            print(f"⚠️  {error_msg}")
            self.tts.speak(error_msg)
    
    def audio_setup_wizard(self):
        """Assistente de configuração de áudio"""
        print("\n" + "="*50)
        print("🎧 ASSISTENTE DE SAÍDA DE SOM")
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
            print("Dispositivo padrão funcionando, não precisa configurar")
    
    def settings_menu(self):
        """Menu de configurações"""
        while True:
            print("\n" + "="*50)
            print("⚙️  CONFIGURAÇÕES DA MIRAI")
            print("="*50)
            print("1. Configurar dispositivo de áudio")
            print("2. Ajustar volume e velocidade")
            print("3. Testar síntese de voz")
            print("4. Listar dispositivos de áudio")
            print("5. Configurar palavras de ativação")
            print("6. Salvar configuração")
            print("7. Voltar ao menu principal")
            print("="*50)
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.tts.select_audio_device()
                # Salva seleção
                self.config["audio_device"] = self.tts.selected_device
                self.save_config()
            
            elif choice == "2":
                try:
                    vol = float(input("Volume (0.0-2.0): ") or "1.0")
                    speed = float(input("Velocidade (0.5-2.0): ") or "1.1")
                    self.tts.set_voice_settings(vol, speed)
                    self.config["volume"] = vol
                    self.config["speed"] = speed
                    self.save_config()
                except:
                    print("❌ Valores inválidos")
            
            elif choice == "3":
                text = input("Texto para teste: ").strip()
                if not text:
                    text = "Olá, eu sou a Mirai. Este é um teste de áudio."
                self.tts.speak(text)
            
            elif choice == "4":
                self.tts.show_audio_devices_menu()
                input("\nPressione Enter para continuar...")
            
            elif choice == "5":
                self.configure_wake_words()
            
            elif choice == "6":
                self.save_config()
                print("✅ Configuração salva!")
            
            elif choice == "7":
                break
            
            else:
                print("❌ Opção inválida")
    
    def configure_wake_words(self):
        """Configura palavras de ativação personalizadas"""
        print("\n🔧 Configurar palavras de ativação")
        print("Palavras atuais:", self.config.get("wake_words", ["mirai"]))
        
        new_words = input("Novas palavras (separadas por vírgula): ").strip()
        if new_words:
            words = [w.strip().lower() for w in new_words.split(",")]
            self.config["wake_words"] = words
            print(f"✅ Palavras atualizadas: {words}")
    
    def listen_loop(self):
        """Loop principal de escuta"""
        print("\n🎧 Modo de escuta ativado")
        print("🎯 Diga 'Mirai' seguido do seu comando")
        print("⏸️  Pressione Ctrl+C para voltar ao menu\n")
        
        while self.active:
            try:
                # Aguarda wake word
                command = self.listener.listen_for_wake_word(
                    device_index=None,
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
    
    def main_menu(self):
        """Menu principal interativo"""
        print("\n" + "="*50)
        print("🤖 M.I.R.A.I - MENU PRINCIPAL")
        print("="*50)
        print("1. Iniciar modo de escuta (com wake word)")
        print("2. Configurações")
        print("3. Configurações de saída de som")
        print("4. Teste rápido de áudio")
        print("5. Conversação direta (sem wake word)")
        print("6. Sair")
        print("="*50)
    
    def run(self):
        """Executa a assistente"""
        # Verificação inicial de áudio
        print("🔊 Verificando sistema de áudio...")
        if not self.tts.audio_devices:
            print("❌ Nenhum dispositivo de áudio encontrado!")
            print("💡 Verifique se seus alto-falantes/fones estão conectados.")
        
        # Menu principal
        while self.active:
            self.main_menu()
            
            try:
                choice = input("\nEscolha uma opção: ").strip()
                
                if choice == "1":
                    self.listen_loop()
                
                elif choice == "2":
                    self.settings_menu()
                
                elif choice == "3":
                    self.audio_setup_wizard()
                
                elif choice == "4":
                    self.tts.test_audio_device()
                    input("\nPressione Enter para continuar...")
                
                elif choice == "5":
                    print("\n💬 Modo conversação direta")
                    print("⚠️  Não precisa dizer 'Mirai' antes")
                    print("⏰ Timeout de 10 segundos\n")
                    
                    command = self.listener.listen_single_command()
                    if command:
                        self.process_command(command)
                    else:
                        print("⏰ Nenhum comando recebido")
                
                elif choice == "6":
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
    print("\n🎯 Dica: Todos os cogumelos são comestíveis, alguns apenas uma vez")
    
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