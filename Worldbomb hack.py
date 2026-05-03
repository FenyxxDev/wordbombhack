import keyboard
import random
import time
import threading
import os

# =============== CONFIGURAÇÕES ===============
AUTO_DELAY = 0.3                     # segundos de pausa antes de completar
PASTA_LISTAS = r"C:\Users\SUPORTE GERENCIAL\OneDrive - Pan American Silver\Área de Trabalho\sofiavêessicoude\Worldbomb\BombParty-Lists-main"
TECLA_DESFAZER = "ctrl+shift+backspace"   # atalho para apagar a última palavra
# ============================================

def carregar_palavras_txt(pasta):
    todas = set()
    for raiz, _, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            if arquivo.lower().endswith('.txt'):
                caminho = os.path.join(raiz, arquivo)
                try:
                    with open(caminho, 'r', encoding='utf-8') as f:
                        for linha in f:
                            palavra = linha.strip().lower()
                            if palavra:
                                todas.add(palavra)
                except (UnicodeDecodeError, FileNotFoundError):
                    try:
                        with open(caminho, 'r', encoding='latin-1') as f:
                            for linha in f:
                                palavra = linha.strip().lower()
                                if palavra:
                                    todas.add(palavra)
                    except:
                        continue
    return list(todas)

print('Carregando palavras...')
wordlist = carregar_palavras_txt(PASTA_LISTAS)
print(f'{len(wordlist)} palavras carregadas.')

typed = ''
istyping = False
auto_timer = None
ultima_palavra = ''       # guarda a última palavra digitada (string)
usadas = set()            # conjunto de palavras já escolhidas nesta sessão

def digitar_palavra(palavra, qtd_backspaces):
    """Apaga o fragmento e escreve a palavra (sem Enter)."""
    global ultima_palavra
    print(f'Completando: {palavra}')
    for _ in range(qtd_backspaces):
        keyboard.press_and_release('backspace')
        time.sleep(random.uniform(0.02, 0.05))
    for char in palavra:
        keyboard.press_and_release(char)
        time.sleep(random.uniform(0.03, 0.09))
    ultima_palavra = palavra

def completar():
    global typed, istyping, usadas
    qtd = len(typed)
    fragmento = typed.strip().lower()
    typed = ''

    if not fragmento:
        print('Nada digitado.')
        return

    # Busca todas as correspondências que contêm o fragmento
    matches = [w for w in wordlist if fragmento in w]
    if not matches:
        print('Nenhuma correspondência.')
        return

    # Remove a palavra idêntica ao fragmento (se houver outras opções)
    matches_sem_exata = [w for w in matches if w != fragmento]
    if matches_sem_exata:
        matches = matches_sem_exata

    # Filtra as palavras ainda não usadas nesta sessão
    matches_nao_usadas = [w for w in matches if w not in usadas]
    if matches_nao_usadas:
        matches = matches_nao_usadas
    else:
        # Todas as opções já foram usadas – reinicia o histórico
        usadas.clear()
        # matches permanece com todas as opções disponíveis

    # Seleciona as palavras mais curtas e sorteia uma
    tamanho_min = min(len(w) for w in matches)
    mais_curtas = [w for w in matches if len(w) == tamanho_min]
    palavra = random.choice(mais_curtas)

    # Marca como usada
    usadas.add(palavra)

    istyping = True
    digitar_palavra(palavra, qtd)
    istyping = False

def resetar_timer():
    global auto_timer
    if auto_timer:
        auto_timer.cancel()
    auto_timer = threading.Timer(AUTO_DELAY, completar)
    auto_timer.start()

def desfazer():
    """Apaga a última palavra digitada e a remove do histórico de usadas."""
    global ultima_palavra, istyping
    if istyping or not ultima_palavra:
        return
    if auto_timer:
        auto_timer.cancel()
    print(f'Desfazendo: {ultima_palavra}')
    for _ in range(len(ultima_palavra)):
        keyboard.press_and_release('backspace')
        time.sleep(0.02)
    # Remove do conjunto de usadas, para que possa ser sugerida novamente
    usadas.discard(ultima_palavra)
    ultima_palavra = ''

# Registra atalho para desfazer
keyboard.add_hotkey(TECLA_DESFAZER, desfazer)

def evento_tecla(event):
    global typed, istyping

    if istyping:
        return
    if event.event_type != 'down':
        return

    if event.name == 'backspace':
        typed = typed[:-1]
        resetar_timer()
        return

    if len(event.name) == 1:  # caractere comum
        typed += event.name
        resetar_timer()
        return

keyboard.hook(evento_tecla)
print(f'Script ativo! Pare de digitar para completar...')
print(f'Use {TECLA_DESFAZER.upper()} para apagar a última palavra sugerida.')
print('Pressione ESC para sair.')
keyboard.wait('esc') 