import sys
from pathlib import Path
import tempfile

import numpy as np
import os

import zipfile

import streamlit as st

sys.path.append(str(Path(__file__).absolute().parent.parent))

from ithappens.create_cards import main, parse_input_file


def create_cards(
    name,
    input_file,
    output_dir,
    expansion_logo,
    merge,
    side,
    format,
    workers,
    image_dir,
    callbacks=None,
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
        image_dir=image_dir,
        callbacks=callbacks,
    )


def zip_cards(target_file: Path, source_dir: Path):
    with zipfile.ZipFile(target_file, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for entry in source_dir.rglob("*"):
            if entry.suffix == ".zip":
                continue
            zip_file.write(entry, entry.relative_to(tmp_dir))


st.set_page_config(
    page_title="It Happens",
    page_icon=":material/sprint:",
    initial_sidebar_state="expanded",
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
    ) as csv_file:
        st.download_button(
            label="Input csv",
            data=csv_file,
            file_name="example.csv",
            mime="text/csv",
            icon=":material/download:",
        )
    with open(
        Path(__file__).parent.parent.parent / "examples" / "example" / "example.xlsx",
        "rb",
    ) as xlsx_file:
        st.download_button(
            label="Input xlsx",
            data=xlsx_file,
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
    ) as logo_file:
        st.download_button(
            label="Expansion logo",
            data=logo_file,
            file_name="example-expansion-logo.png",
            mime="image/png",
            icon=":material/download:",
        )

expansion_name = st.text_input("Expansion name")
input_file = st.file_uploader("Please provide your excel or csv input file")
expansion_logo = st.file_uploader("Optionally provide your expansion logo")
images = st.file_uploader("Upload your front images", accept_multiple_files=True)

if input_file is not None:
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

    if st.button(":material/play_arrow: Create cards", use_container_width=True):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)

            image_dir = tmp_dir / "images"
            image_dir.mkdir()
            for image in images:
                with open(image_dir / image.name, "wb") as image_file:
                    image_file.write(image.getbuffer())

            df = parse_input_file(input_file, image_dir)

            pbar_text = "Creating your It Happens playing cards..."

            class PbarCallback:
                def __init__(self, total: int, text: str):
                    self.pbar = st.progress(0, text)
                    self.value = 0
                    self.stepsize = 1 / total
                    self.text = text

                def __call__(self):
                    self.advance()

                def advance(self):
                    self.value += self.stepsize
                    self.pbar.progress(self.value, self.text)

                def empty(self):
                    self.pbar.empty()

            pbar_callback = PbarCallback(len(df), pbar_text)
            callbacks = (pbar_callback,)
            create_cards(
                name=expansion_name,
                input_file=input_file,
                output_dir=tmp_dir,
                expansion_logo=expansion_logo,
                merge=merge,
                side=side,
                format=format,
                workers=workers,
                image_dir=image_dir,
                callbacks=callbacks,
            )
            pbar_callback.empty()

            archive = tmp_dir / "ithappens-output.zip"
            zip_cards(archive, tmp_dir)

            with open(archive, "rb") as zip_file_buf:
                st.download_button(
                    label="Download cards",
                    data=zip_file_buf,
                    file_name=archive.name,
                    mime="application/zip",
                    type="primary",
                    icon=":material/download:",
                    use_container_width=True,
                )
