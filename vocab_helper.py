import pygame
import csv
import random
import datetime
import time
import os

# 初始化 Pygame
pygame.init()

# 設定視窗大小和標題
screen = pygame.display.set_mode((800, 650))
pygame.display.set_caption("Vocabulary Trainer")

# 定義顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 載入字型
font_path = "NotoSansCJK-Regular.ttc"  # 替換為你的字型檔案路徑
font_large = pygame.font.Font(font_path, 74)
font_medium = pygame.font.Font(font_path, 56)
font_small = pygame.font.Font(font_path, 36)

# 截斷過長的文字
def truncate_text(text, font, max_width):
    while font.size(text)[0] > max_width:
        text = text[:-1]
    return text

# 載入單字資料
def load_words(file_path):
    words = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            next(reader)  # 跳過標題行
            for row in reader:
                words.append((row[0], row[1], int(row[2])))
    except Exception as e:
        print(f"無法讀取文件: {e}")
    return words

def save_words(file_path, words):
    try:
        with open(file_path, mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["word", "translation", "count"])
            for word, translation, count in words:
                writer.writerow([word, translation, count])
    except Exception as e:
        print(f"無法寫入文件: {e}")

def export_incorrect_words(file_path, words):
    incorrect_words = [word for word in words if word[2] > 0]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = f"{file_path.split('.')[0]}_{timestamp}.csv"
    try:
        with open(export_path, mode='w', encoding='utf-8-sig', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["word", "translation", "count"])
            for word in incorrect_words:
                writer.writerow(word)
    except Exception as e:
        print(f"無法寫入文件: {e}")
    return export_path

# 初始化變量
csv_files = [file for file in os.listdir() if file.endswith('.csv')]
file_path = None
export_base_path = 'incorrect_words.csv'
worng_words = []
unused_words = []

history = []
current_word = None
current_translation = None
show_translation = False
finished = False
increment_counter = True
correct_count = 0
incorrect_count = 0
total_wordscount = 0
start_time = time.time()

# 顯示下一個單字
def next_word():
    global current_word, current_translation, show_translation, unused_words, finished, increment_counter, start_time
    if not unused_words:
        finished = True
        return

    if current_word is not None:
        history.append((current_word, current_translation, increment_counter))

    current_word, current_translation, _ = unused_words.pop(random.randint(0, len(unused_words) - 1))
    show_translation = False
    increment_counter = True
    start_time = time.time()

# 顯示上一個單字
def previous_word():
    global current_word, current_translation, show_translation, increment_counter, start_time
    if history:
        unused_words.append((current_word, current_translation, 0))
        current_word, current_translation, increment_counter = history.pop()
        show_translation = False
        start_time = time.time()

# 顯示文字
def draw_text(text, font, color, surface, x, y, max_width=None):
    if max_width:
        text = truncate_text(text, font, max_width)
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.center = (x, y)
    surface.blit(textobj, textrect)

# 主循環
running = True
export_message = ""
unfamiliar = False
selecting_file = True
selected_file_index = 0
word_bank = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if file_path:
                word_bank.sort(key=lambda x: x[2], reverse=True)
                save_words(file_path, word_bank)
            running = False
        if event.type == pygame.KEYDOWN:
            if selecting_file:
                if event.key == pygame.K_UP:
                    selected_file_index = (selected_file_index - 1) % len(csv_files)
                elif event.key == pygame.K_DOWN:
                    selected_file_index = (selected_file_index + 1) % len(csv_files)
                elif event.key == pygame.K_RETURN:
                    file_path = csv_files[selected_file_index]
                    word_bank = load_words(file_path)
                    total_wordscount = len(word_bank)
                    unused_words = load_words(file_path)
                    next_word()
                    selecting_file = False
            elif finished:
                if event.key == pygame.K_y:
                    unused_words = worng_words.copy()
                    history = []
                    worng_words = []
                    total_wordscount = len(unused_words)
                    finished = False
                    next_word()
                    correct_count = 0
                    incorrect_count = 0
                    export_message = ""
                    word_bank.sort(key=lambda x: x[2], reverse=True)
                    save_words(file_path, word_bank)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    word_bank.sort(key=lambda x: x[2], reverse=True)
                    save_words(file_path, word_bank)
                    running = False
                elif event.key == pygame.K_e:
                    worng_words.sort(key=lambda x: x[2], reverse=True)
                    export_path = export_incorrect_words(export_base_path, worng_words)
                    export_message = f"匯出成功: {export_path}"
            else:
                if event.key == pygame.K_SPACE:
                    if show_translation:
                        if not unfamiliar:
                            correct_count += 1
                        next_word()
                        unfamiliar = False
                    else:
                        end_time = time.time()
                        elapsed_time = end_time - start_time
                        show_translation = True
                        print(elapsed_time)
                        print(worng_words)
                        if elapsed_time > 2:  # 只在需要增加計數器時增加
                            for i, (word, translation, count) in enumerate(word_bank):
                                if word == current_word:
                                    word_bank[i] = (word, translation, count + 1)
                                    worng_words.append((word, translation, count + 1))
                                    break
                            unfamiliar = True
                            incorrect_count += 1
                elif event.key == pygame.K_x:
                    for i, (word, translation, count) in enumerate(word_bank):
                                if word == current_word:
                                    word_bank[i] = (word, translation, count + 1)
                                    worng_words.append((word, translation, count + 1))
                                    break
                    incorrect_count += 1
                    next_word()
                    unfamiliar = False
                        
                elif event.key == pygame.K_RIGHT:
                    if not unfamiliar:
                        correct_count += 1
                    next_word()
                    unfamiliar = False
                elif event.key == pygame.K_LEFT:
                    previous_word()
                    unfamiliar = False

    screen.fill(WHITE)

    if selecting_file:
        draw_text("選擇一個CSV文件", font_medium, BLACK, screen, 400, 100, 700)
        for index, file in enumerate(csv_files):
            color = GREEN if index == selected_file_index else BLACK
            draw_text(file, font_small, color, screen, 400, 200 + index * 50, 700)
    elif finished:
        total = correct_count + incorrect_count
        ratio = (correct_count / total) * 100 if total > 0 else 0
        draw_text("太棒了!你複習完所有單字了!", font_medium, BLACK, screen, 400, 100, 700)
        draw_text(f"會的題數: {correct_count}", font_small, BLACK, screen, 400, 200, 700)
        draw_text(f"不會的題數: {incorrect_count}", font_small, BLACK, screen, 400, 250, 700)
        draw_text(f"答題比率: {ratio:.2f}%", font_small, BLACK, screen, 400, 300, 700)
        draw_text("按 'Y' 重新開始, 按 'ESC' 結束並保存", font_small, BLACK, screen, 400, 400, 700)
        draw_text("按 'E' 匯出所有不會的單字", font_small, BLACK, screen, 400, 450, 700)
        if export_message:
            draw_text(export_message, font_small, GREEN, screen, 400, 500, 700)
    else:
        draw_text(current_word, font_large, BLACK, screen, 400, 150, 700)
        if show_translation:
            draw_text(current_translation, font_medium, BLUE, screen, 400, 300, 700)
        draw_text(f"進度: {len(history)}/{total_wordscount}", font_small, BLACK, screen, 400, 50, 700)
        draw_text("按空白鍵 察看中文意思", font_small, BLACK, screen, 400, 450, 700)
        draw_text("按 '→' 下一個單字", font_small, GREEN, screen, 400, 500, 700)
        draw_text("按 '←' 回到上一個單字", font_small, BLACK, screen, 400, 600, 700)

    pygame.display.flip()

pygame.quit()
