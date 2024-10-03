import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import tkinter as tk
from tkinter import filedialog

sys.path.append(str(Path(__file__).absolute().parent.parent))

from ithappens.create_cards import main


def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(parent=root)
    root.destroy()
    return Path(folder_path)


uploaded_file = st.file_uploader("Please provide your excel input")

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
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
