import torch
import numpy as np
import sounddevice as sd
import threading
import time
from TTS.api import TTS
import sys
import os

class MiraiTTS:
    def __init__(self, model_name="tts_models/pt/cv/vits"):
        """
        Inicializa o Coqui TTS com seleção de dispositivo de áudio
        """
        print("🔊 Inicializando sistema de fala...")
        
        # Configura dispositivo de computação
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📱 Dispositivo de computação: {self.device}")
        
        # Atributo sample_rate (CRÍTICO - estava faltando)
        self.sample_rate = 22050  # Taxa de amostragem padrão para maioria dos modelos TTS
        
        # Lista dispositivos de áudio disponíveis
        self.audio_devices = self.list_audio_devices()
        self.selected_device = None
        
        # Configurações de voz
        self.volume = 1.0
        self.speech_rate = 1.0
        
        # Inicializa TTS
        self.model_name = model_name
        self.tts = None
        self.load_tts_model()
    
    def load_tts_model(self):
        """Carrega o modelo TTS com tratamento de erro"""
        try:
            print(f"🔄 Carregando modelo: {self.model_name}")
            self.tts = TTS(model_name=self.model_name, progress_bar=False).to(self.device)
            print(f"✅ TTS carregado: {self.model_name}")
            
            # Tenta obter sample_rate do modelo se possível
            try:
                # Alguns modelos têm sample_rate como atributo
                if hasattr(self.tts, 'sample_rate'):
                    self.sample_rate = self.tts.sample_rate
                # Ou podemos tentar inferir
                elif hasattr(self.tts, 'model') and hasattr(self.tts.model, 'sample_rate'):
                    self.sample_rate = self.tts.model.sample_rate
            except:
                pass  # Mantém o padrão
                
            print(f"📊 Sample rate: {self.sample_rate} Hz")
            
        except Exception as e:
            print(f"⚠️  Erro ao carregar modelo {self.model_name}: {e}")
            print("🔧 Tentando modelo alternativo...")
            self.try_alternative_models()
    
    def try_alternative_models(self):
        """Tenta carregar modelos alternativos"""
        alternative_models = [
            "tts_models/multilingual/multi-dataset/your_tts",
            "tts_models/multilingual/multi-dataset/xtts_v2",
            "tts_models/en/ljspeech/tacotron2-DDC",
            "tts_models/en/vctk/vits"
        ]
        
        for model in alternative_models:
            try:
                print(f"🔄 Tentando: {model}")
                self.tts = TTS(model_name=model, progress_bar=False).to(self.device)
                self.model_name = model
                print(f"✅ Modelo carregado: {model}")
                return
            except Exception as e:
                print(f"❌ {model} falhou: {e}")
                continue
        
        print("❌ Não foi possível carregar nenhum modelo TTS")
        print("💡 Dica: Verifique se os modelos foram baixados corretamente")
        self.tts = None
    
    def list_audio_devices(self):
        """Lista todos os dispositivos de áudio de saída disponíveis"""
        devices = []
        try:
            all_devices = sd.query_devices()
            for i, device in enumerate(all_devices):
                if device['max_output_channels'] > 0:
                    devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_output_channels'],
                        'default': device['name'] == sd.default.device[1] if isinstance(sd.default.device, tuple) else i == sd.default.device,
                        'sample_rate': device['default_samplerate']
                    })
        except Exception as e:
            print(f"⚠️  Erro ao listar dispositivos: {e}")
        
        return devices
    
    def show_audio_devices_menu(self):
        """Mostra menu para selecionar dispositivo de áudio"""
        print("\n" + "="*50)
        print("🎧 DISPOSITIVOS DE ÁUDIO DISPONÍVEIS")
        print("="*50)
        
        if not self.audio_devices:
            print("❌ Nenhum dispositivo de saída encontrado!")
            return None
        
        for device in self.audio_devices:
            default_mark = " (PADRÃO)" if device['default'] else ""
            sample_rate = f" - {device['sample_rate']} Hz" if 'sample_rate' in device else ""
            print(f"[{device['id']}] {device['name']} - {device['channels']} canais{sample_rate}{default_mark}")
        
        print("\n[P] Usar dispositivo padrão do sistema")
        print("[T] Testar dispositivo")
        print("[L] Atualizar lista")
        print("[S] Sair da seleção")
        
        return self.audio_devices
    
    def select_audio_device(self, device_id=None):
        """
        Seleciona dispositivo de áudio
        
        Args:
            device_id: ID do dispositivo ou None para menu interativo
        """
        if device_id is None:
            devices = self.show_audio_devices_menu()
            if not devices:
                return False
            
            while True:
                choice = input("\n🎯 Selecione o dispositivo ou opção: ").strip().upper()
                
                if choice == 'P':
                    self.selected_device = None
                    sd.default.device = None
                    print("✅ Usando dispositivo padrão do sistema")
                    return True
                
                elif choice == 'T':
                    self.test_audio_device()
                    continue
                
                elif choice == 'L':
                    self.audio_devices = self.list_audio_devices()
                    self.show_audio_devices_menu()
                    continue
                
                elif choice == 'S':
                    print("⏭️  Mantendo configuração atual")
                    return False
                
                elif choice.isdigit():
                    device_id = int(choice)
                    if any(d['id'] == device_id for d in self.audio_devices):
                        self.selected_device = device_id
                        sd.default.device = device_id
                        print(f"✅ Dispositivo selecionado: {self.audio_devices[device_id]['name']}")
                        return True
                    else:
                        print("❌ ID inválido")
                else:
                    print("❌ Opção inválida")
        
        else:
            # Seleção direta por ID
            if any(d['id'] == device_id for d in self.audio_devices):
                self.selected_device = device_id
                sd.default.device = device_id
                print(f"✅ Dispositivo selecionado: ID {device_id}")
                return True
            else:
                print(f"❌ Dispositivo ID {device_id} não encontrado")
                return False
    
    def test_audio_device(self, device_id=None):
        """Testa o dispositivo de áudio com um som de teste"""
        print("\n🔊 Testando áudio...")
        
        if device_id is None and self.selected_device is not None:
            device_id = self.selected_device
        
        try:
            # Gera um tom de teste (440 Hz = Lá)
            sample_rate = 44100
            duration = 1.0  # segundos
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            tone = np.sin(2 * np.pi * 440 * t) * 0.3
            
            # Reproduz
            if device_id is not None:
                sd.play(tone, sample_rate, device=device_id)
            else:
                sd.play(tone, sample_rate)
            
            sd.wait()
            print("✅ Teste de áudio concluído - Você ouviu o som?")
            
        except Exception as e:
            print(f"❌ Erro no teste de áudio: {e}")
    
    def generate_speech(self, text, speaker=None):
        """
        Gera áudio a partir do texto
        
        Args:
            text: Texto para sintetizar
            speaker: Nome do falante (se suportado)
        
        Returns:
            tuple: (audio_data, sample_rate)
        """
        if not text or len(text.strip()) == 0:
            print("⚠️  Texto vazio para síntese")
            return None, None
        
        if self.tts is None:
            print("❌ TTS não inicializado")
            return None, None
        
        print(f"🗣️  Sintetizando: '{text[:60]}...'")
        
        try:
            # Parâmetros para síntese
            kwargs = {"text": text}
            
            # Adiciona speaker se disponível
            if speaker and hasattr(self.tts, 'speakers') and speaker:
                if speaker in self.tts.speakers:
                    kwargs["speaker"] = speaker
                else:
                    print(f"⚠️  Speaker '{speaker}' não disponível")
            
            # Adiciona language se o modelo suportar
            if hasattr(self.tts, 'language'):
                kwargs["language"] = "pt"
            
            print(f"⚙️  Parâmetros: {kwargs}")
            
            # Gera áudio
            wav = self.tts.tts(**kwargs)
            
            # Converte para numpy array se necessário
            if isinstance(wav, list):
                wav = np.array(wav)
            
            # Verifica o tipo de dados
            print(f"📊 Tipo de áudio: {wav.dtype}, Forma: {wav.shape}")
            
            # Converte para float32 se necessário
            if wav.dtype == np.int16:
                wav = wav.astype(np.float32) / 32767.0
            elif wav.dtype == np.int32:
                wav = wav.astype(np.float32) / 2147483647.0
            elif wav.dtype != np.float32:
                wav = wav.astype(np.float32)
            
            # Normaliza se necessário
            max_val = np.max(np.abs(wav))
            if max_val > 1.0:
                wav = wav / max_val
            
            duration = len(wav) / self.sample_rate
            print(f"✅ Áudio gerado: {duration:.2f}s, {len(wav)} amostras")
            
            return wav, self.sample_rate
            
        except Exception as e:
            print(f"❌ Erro ao gerar fala: {e}")
            import traceback
            traceback.print_exc()
            return None, None
    
    def play_audio(self, wav, sample_rate, blocking=True):
        """Reproduz áudio no dispositivo selecionado"""
        try:
            print(f"▶️  Reproduzindo no dispositivo {self.selected_device or 'padrão'}...")
            print(f"📊 Taxa: {sample_rate} Hz, Duração: {len(wav)/sample_rate:.2f}s")
            
            # Reproduz no dispositivo selecionado
            if self.selected_device is not None:
                sd.play(wav, sample_rate, device=self.selected_device)
            else:
                sd.play(wav, sample_rate)
            
            if blocking:
                sd.wait()
                print("✅ Fala concluída")
            
        except Exception as e:
            print(f"❌ Erro na reprodução: {e}")
            print("💡 Tente selecionar outro dispositivo de áudio")
            import traceback
            traceback.print_exc()
    
    def speak(self, text, speaker=None, blocking=True):
        """
        Sintetiza e fala o texto
        
        Args:
            text: Texto para falar
            speaker: Falante específico
            blocking: Se True, espera terminar de falar
        """
        if self.tts is None:
            print("❌ TTS não disponível. Verifique se os modelos foram baixados.")
            print("💡 Tente: python -c 'from TTS.api import TTS; print(TTS().list_models())'")
            return None
        
        if not text or len(text.strip()) == 0:
            print("⚠️  Texto vazio para fala")
            return None
        
        print(f"🔊 Preparando para falar: '{text[:80]}...'")
        
        # Gera o áudio
        wav, sr = self.generate_speech(text, speaker)
        
        if wav is not None and sr is not None:
            # Ajusta volume
            wav = wav * self.volume
            
            # Reproduz
            if blocking:
                self.play_audio(wav, sr, blocking=True)
            else:
                # Thread não-bloqueante
                thread = threading.Thread(
                    target=self.play_audio, 
                    args=(wav, sr, True),
                    daemon=True
                )
                thread.start()
                return thread
        else:
            print("❌ Falha ao gerar áudio")
        
        return None
    
    def set_voice_settings(self, volume=1.0, rate=1.0):
        """
        Ajusta configurações de voz
        
        Args:
            volume: Volume (0.0 a 2.0)
            rate: Velocidade (0.5 a 2.0)
        """
        self.volume = max(0.0, min(2.0, volume))
        self.speech_rate = max(0.5, min(2.0, rate))
        print(f"⚙️  Configurações: volume={volume}, velocidade={rate}")
    
    def interactive_setup(self):
        """Configuração interativa do TTS"""
        print("\n" + "="*50)
        print("🔧 CONFIGURAÇÃO INTERATIVA DO TTS")
        print("="*50)
        
        while True:
            print("\n📋 Menu de configuração:")
            print("1. Selecionar dispositivo de áudio")
            print("2. Testar dispositivo atual")
            print("3. Ajustar volume e velocidade")
            print("4. Testar síntese de voz")
            print("5. Listar modelos disponíveis")
            print("6. Trocar modelo TTS")
            print("7. Voltar")
            
            choice = input("\nEscolha uma opção: ").strip()
            
            if choice == "1":
                self.select_audio_device()
            
            elif choice == "2":
                self.test_audio_device()
            
            elif choice == "3":
                try:
                    vol = float(input("Volume (0.0-2.0, padrão=1.0): ") or "1.0")
                    speed = float(input("Velocidade (0.5-2.0, padrão=1.0): ") or "1.0")
                    self.set_voice_settings(vol, speed)
                except:
                    print("❌ Valores inválidos")
            
            elif choice == "4":
                test_text = input("Texto para teste (Enter para padrão): ").strip()
                if not test_text:
                    test_text = "Olá, eu sou a Mirai, sua assistente virtual. Este é um teste de áudio."
                self.speak(test_text)
            
            elif choice == "5":
                self.list_available_models()
            
            elif choice == "6":
                self.change_model()
            
            elif choice == "7":
                print("✅ Configuração concluída")
                break
            
            else:
                print("❌ Opção inválida")
    
    def list_available_models(self):
        """Lista modelos TTS disponíveis"""
        print("\n📋 Modelos disponíveis:")
        try:
            models = TTS().list_models()
            pt_models = [m for m in models if 'pt' in m.lower()]
            multilingual = [m for m in models if 'multilingual' in m.lower()]
            
            if pt_models:
                print("\n🇵🇹 Português:")
                for model in pt_models[:5]:  # Mostra apenas 5
                    print(f"  • {model}")
            
            if multilingual:
                print("\n🌍 Multilíngue:")
                for model in multilingual[:5]:
                    print(f"  • {model}")
                    
            print(f"\n📊 Total de modelos: {len(models)}")
            
        except Exception as e:
            print(f"❌ Erro ao listar modelos: {e}")
    
    def change_model(self):
        """Troca o modelo TTS"""
        print(f"\n🔄 Modelo atual: {self.model_name}")
        new_model = input("Novo modelo (Enter para cancelar): ").strip()
        
        if new_model:
            try:
                self.model_name = new_model
                self.load_tts_model()
            except Exception as e:
                print(f"❌ Erro ao carregar modelo: {e}")

# Instância global com inicialização preguiçosa
_tts_engine = None

def get_tts_engine():
    """Obtém ou cria instância do TTS (singleton)"""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = MiraiTTS()
    return _tts_engine

def falar(texto, **kwargs):
    """Função de conveniência"""
    try:
        engine = get_tts_engine()
        return engine.speak(texto, **kwargs)
    except Exception as e:
        print(f"❌ Erro na função falar: {e}")
        return None

# Teste direto
if __name__ == "__main__":
    print("🧪 Teste do sistema de fala MIRAI")
    print("="*50)
    
    # Teste rápido
    tts = MiraiTTS()
    
    if tts.tts is not None:
        print("\n✅ TTS carregado com sucesso!")
        print(f"📋 Modelo: {tts.model_name}")
        print(f"📊 Sample rate: {tts.sample_rate} Hz")
        
        # Teste de áudio
        print("\n🔊 Testando dispositivo padrão...")
        tts.test_audio_device()
        
        # Teste de síntese
        print("\n🗣️  Teste de síntese...")
        tts.speak("Olá! Eu sou a Mirai, sua assistente virtual. Como posso ajudar?")
        
        # Menu interativo
        tts.interactive_setup()
    else:
        print("❌ Não foi possível inicializar o TTS")
        print("\n💡 Soluções:")
        print("1. Verifique se o TTS está instalado: pip show TTS")
        print("2. Baixe modelos: python -c 'from TTS.api import TTS; tts = TTS()'")
        print("3. Tente outro modelo nas configurações")