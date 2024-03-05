import streamlit as st
import numpy as np
import random
import string
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
import tempfile  # Import the tempfile module
import os

# Function to check space availability for word placement
def check_space(grid, word, start_pos, direction):
    row, col = start_pos
    if direction == 'horizontal' and col + len(word) > len(grid[0]):
        return False
    if direction == 'vertical' and row + len(word) > len(grid):
        return False
    if direction == 'diagonal' and (col + len(word) > len(grid[0]) or row + len(word) > len(grid)):
        return False

    for i, letter in enumerate(word):
        if direction == 'horizontal':
            if grid[row][col+i] not in [' ', letter]:
                return False
        elif direction == 'vertical':
            if grid[row+i][col] not in [' ', letter]:
                return False
        elif direction == 'diagonal':
            if grid[row+i][col+i] not in [' ', letter]:
                return False
    return True

# Function to place a word in the grid
def place_word(grid, word, start_pos, direction):
    row, col = start_pos
    for i, letter in enumerate(word):
        if direction == 'horizontal':
            grid[row][col+i] = letter
        elif direction == 'vertical':
            grid[row+i][col] = letter
        elif direction == 'diagonal':
            grid[row+i][col+i] = letter

# Function to generate the soup of letters
def generate_soup(words, size, difficulty):
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    directions = ['horizontal', 'vertical'] if difficulty == 'easy' else ['horizontal', 'vertical', 'diagonal']
    placed_words = defaultdict(list)

    for word in words:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            direction = random.choice(directions)
            start_pos = (random.randint(0, size-1), random.randint(0, size-1))
            if check_space(grid, word, start_pos, direction):
                place_word(grid, word, start_pos, direction)
                placed_words[word].append((start_pos, direction))
                placed = True
            attempts += 1
    
    # Fill the remaining spaces with random letters
    for row in range(size):
        for col in range(size):
            if grid[row][col] == ' ':
                grid[row][col] = random.choice(string.ascii_uppercase)
                
    return grid, placed_words

# Function to generate an image of the soup
def generate_soup_image(soup, cell_size=80, highlight_words=None):
    size = len(soup) * cell_size
    image = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(image)
    
    font_size = int(cell_size * 0.75)
    try:
        # Try to use a truetype font (better quality)
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fall back to the default PIL font if Arial is not available
        font = ImageFont.load_default()
    
    for i, row in enumerate(soup):
        for j, letter in enumerate(row):
            x = j * cell_size + (cell_size - draw.textsize(letter, font=font)[0]) / 2
            y = i * cell_size + (cell_size - draw.textsize(letter, font=font)[1]) / 2
            draw.text((x, y), letter, fill='black', font=font)

    # Highlight the words if highlight_words is provided
    if highlight_words:
        for word, positions in highlight_words.items():
            for start_pos, direction in positions:
                x_start, y_start = start_pos
                for i, char in enumerate(word):
                    x = x_start * cell_size
                    y = y_start * cell_size

                    if direction == 'horizontal':
                        x += i * cell_size
                    elif direction == 'vertical':
                        y += i * cell_size
                    elif direction == 'diagonal':
                        x += i * cell_size
                        y += i * cell_size
                    
                    # Highlight the background of the cell with the word's letter
                    draw.rectangle([x, y, x + cell_size, y + cell_size], fill='yellow')
                    # Redraw the letter on top of the highlighted background
                    letter_x = x + (cell_size - draw.textsize(char, font=font)[0]) / 2
                    letter_y = y + (cell_size - draw.textsize(char, font=font)[1]) / 2
                    draw.text((letter_x, letter_y), char, fill='black', font=font)
    
    return image

def display_soup(soup):
    # Convert the soup array into a formatted string
    soup_str = '<div style="font-family: monospace; line-height: 1.5;">'
    for row in soup:
        soup_str += ' '.join(row) + '<br>'
    soup_str += '</div>'
    st.markdown(soup_str, unsafe_allow_html=True)

def display_solution(soup, placed_words):
    # Convert the soup array into a formatted string with highlighted words
    solution_str = '<div style="font-family: monospace; line-height: 1.5;">'
    for r, row in enumerate(soup):
        for c, letter in enumerate(row):
            letter_colored = False
            for word, positions in placed_words.items():
                for start_pos, direction in positions:
                    if direction == 'horizontal' and start_pos[0] == r and start_pos[1] <= c < start_pos[1] + len(word):
                        solution_str += f'<span style="color: red;">{letter}</span> '
                        letter_colored = True
                    elif direction == 'vertical' and start_pos[1] == c and start_pos[0] <= r < start_pos[0] + len(word):
                        solution_str += f'<span style="color: red;">{letter}</span> '
                        letter_colored = True
                    elif direction == 'diagonal' and start_pos[0] <= r < start_pos[0] + len(word) and start_pos[1] <= c < start_pos[1] + len(word) and (r - start_pos[0]) == (c - start_pos[1]):
                        solution_str += f'<span style="color: red;">{letter}</span> '
                        letter_colored = True
            if not letter_colored:
                solution_str += f'{letter} '
        solution_str += '<br>'
    solution_str += '</div>'
    st.markdown(solution_str, unsafe_allow_html=True)
    

# Streamlit UI setup
# Streamlit UI setup
st.title('🍜 Letter Soup Generator')

st.markdown("""
Welcome to the Letter Soup Generator! Follow the steps below to create your own customized soup of letters:
1. Enter up to 30 words in the text box below.
2. Select your desired soup size and difficulty level.
3. Click "Generate Soup" to see your puzzle!
""")

words_input = st.text_area("Step 1: Enter your words (separated by commas)", height=100)

col1, col2 = st.columns(2)
with col1:
    size = st.slider('Step 2: Select the size of the soup', min_value=5, max_value=50, value=10)
with col2:
    difficulty = st.selectbox('Step 3: Select the difficulty level', ['easy', 'medium', 'hard'])

# Generate Soup button
if st.button('Generate Soup'):
    words_input_list = [word.strip().upper() for word in words_input.split(',') if word.strip() != '']
    words = list(set(words_input_list))[:30]
    if not words:
        st.error('Please enter at least one word.')
    else:
        soup, placed_words = generate_soup(words, size, difficulty)
        st.session_state['soup'] = soup
        st.session_state['placed_words'] = placed_words
        st.session_state['soup_generated'] = True

# Check if the soup has been generated
if 'soup_generated' in st.session_state and st.session_state['soup_generated']:
    # Display soup in a scrollable container
    with st.expander("🔍 View Soup", expanded=True):
        display_soup(st.session_state['soup'])  # This should be your function to display soup in a formatted way
    
    # Display solution in a scrollable container
    with st.expander("💡 Show Solution", expanded=False):
        display_solution(st.session_state['soup'], st.session_state['placed_words'])  # This should be your function to display solution in a formatted way

