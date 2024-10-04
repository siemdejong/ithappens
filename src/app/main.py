import sys
from pathlib import Path

import streamlit as st
import tkinter as tk
from tkinter import filedialog

sys.path.append(str(Path(__file__).absolute().parent.parent))

from ithappens.create_cards import main, parse_input_file


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(parent=root)
    root.destroy()
    return Path(folder_path)


with st.sidebar:
    st.title("It Happens")
    st.write("Create your own Shit Happens playing cards!")
    st.write(
        "Ever wanted to play with your own [Shit Happens](https://boardgamegeek.com/boardgame/196379/shit-happens) playing cards? Now you can. Write down the most miserable situations you can think of and rank them. This project automatically outputs playing cards in pdf format."
    )
    st.write(
        "This project is not related to the original card game. [Open an issue](https://github.com/siemdejong/ithappens/issues/new/choose) in case of any objections."
    )
    st.write(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">This project is open source.<br>See <a href=https://github.com/siemdejong/ithappens><i class="fa-brands fa-github">&nbsp;</i>siemdejong/ithappens</a>.',
        unsafe_allow_html=True,
    )
    st.components.v1.html(
        '<br><script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="siemdejong" data-color="#FFDD00" data-emoji="🍺"  data-font="Lato" data-text="Buy me a beer" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>'
    )

uploaded_file = st.file_uploader("Please provide your excel or csv input file")

if uploaded_file is not None:
    df = parse_input_file(uploaded_file)
    expansion_name = st.text_input("Expansion name")
    input_dir = st.session_state.get("input_dir", None)
    folder_select_button = st.button("Select input directory")
    if folder_select_button:
        input_dir = select_folder()
        st.session_state.input_dir = input_dir
    if input_dir:
        st.write("Selected input directory path:", input_dir)
        output_dir = input_dir / "outputs"

    merge = st.checkbox("Merge output", value=True)
    side = st.selectbox("Side(s) to generate", ["both", "front", "back"])
    format = st.selectbox("Output format", ["pdf", "png"])
    workers = st.number_input("Number of workers", value=4)
    chunks = st.number_input("Number of chunks for the workers to process", value=30)

    if st.button("Create cards"):
        main(
            name=expansion_name,
            input_dir=input_dir,
            merge=merge,
            side=side,
            format=format,
            workers=workers,
            chunks=chunks,
        )
        st.write("Cards written to ", output_dir)
