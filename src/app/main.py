import sys
from pathlib import Path
import tempfile

import numpy as np
import os

import shutil

import streamlit as st

sys.path.append(str(Path(__file__).absolute().parent.parent))

from ithappens.create_cards import main, parse_input_file


@st.cache_data
def create_cards(
    name, input_file, output_dir, expansion_logo, merge, side, format, workers, chunks
):
    main(
        name=name,
        input_file=input_file,
        output_dir=output_dir,
        expansion_logo_path=expansion_logo.name if expansion_logo else None,
        merge=merge,
        side=side,
        format=format,
        workers=workers,
        chunks=chunks,
    )


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

with st.popover("Download example data"):
    st.write("Download example data to get started.")
    with open(
        Path(__file__).parent.parent.parent / "examples" / "example" / "example.csv",
        "rb",
    ) as zip_file:
        st.download_button(
            label="Input csv",
            data=zip_file,
            file_name="example.csv",
            mime="text/csv",
            icon=":material/download:",
        )
    with open(
        Path(__file__).parent.parent.parent / "examples" / "example" / "example.xlsx",
        "rb",
    ) as zip_file:
        st.download_button(
            label="Input xlsx",
            data=zip_file,
            file_name="example.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            icon=":material/download:",
        )
    with open(
        Path(__file__).parent.parent.parent
        / "examples"
        / "example"
        / "images"
        / "expansion-logo.png",
        "rb",
    ) as zip_file:
        st.download_button(
            label="Expansion logo",
            data=zip_file,
            file_name="example-expansion-logo.png",
            mime="image/png",
            icon=":material/download:",
        )

expansion_name = st.text_input("Expansion name")
input_file = st.file_uploader("Please provide your excel or csv input file")
expansion_logo = st.file_uploader("Optionally provide your expansion logo")

if input_file is not None:
    df = parse_input_file(input_file)

    with st.popover(":material/settings: Additional settings"):
        merge = st.toggle(":material/picture_as_pdf: Merge output", value=True)
        side = st.radio(
            "Side(s) to generate", ["both", "front", "back"], horizontal=True
        )
        format = st.radio("Output format", ["pdf", "png"], horizontal=True)
        workers = st.select_slider(
            "Number of workers",
            options=np.arange(1, os.cpu_count() + 1),
            value=os.cpu_count(),
        )
        chunks = st.select_slider(
            "Number of chunks", options=np.arange(1, len(df) + 1), value=len(df)
        )

    if st.button(":material/play_arrow: Create cards", use_container_width=True):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with st.spinner("Creating your It Happens playing cards..."):
                create_cards(
                    name=expansion_name,
                    input_file=input_file,
                    output_dir=tmp_dir,
                    expansion_logo=expansion_logo,
                    merge=merge,
                    side=side,
                    format=format,
                    workers=workers,
                    chunks=chunks,
                )

                zip_file = Path(tmp_dir) / "ithappens-output.zip"
                archive = shutil.make_archive(zip_file, "zip", tmp_dir)

                with open(archive, "rb") as zip_file_buf:
                    st.download_button(
                        label="Download cards",
                        data=zip_file_buf,
                        file_name="ithappens-output.zip",
                        mime="application/zip",
                        type="primary",
                        icon=":material/download:",
                        use_container_width=True,
                    )
