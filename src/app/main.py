import os
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

sys.path.append(str(Path(__file__).absolute().parent.parent))

from ithappens.create_cards import main, parse_input_file
from ithappens.exceptions import ItHappensException

# True if app is running on Streamlit Community Cloud
# https://discuss.streamlit.io/t/environment-variable-indicating-my-app-is-running-on-streamlit-sharing/8668/4
IS_STREAMLIT_SHARING = os.getenv("USER") == "appuser"


def create_cards(
    name,
    input_file,
    output_dir,
    expansion_logo_path,
    merge,
    side,
    format,
    workers,
    image_dir,
    misery_index_desc="misery index",
    callbacks=None,
):
    main(
        name=name,
        input_file=input_file,
        output_dir=output_dir,
        expansion_logo_path=expansion_logo_path,
        merge=merge,
        side=side,
        format=format,
        workers=workers,
        image_dir=image_dir,
        misery_index_desc=misery_index_desc,
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


st.title("It Happens")
st.write("Create your own Shit Happens playing cards!")
st.write(
    "Ever wanted to play with your own [Shit Happens](https://boardgamegeek.com/boardgame/196379/shit-happens) playing cards? Now you can. Write down the most miserable situations you can think of and rank them. This project automatically outputs playing cards in pdf format."
)
st.write(
    "This project is not related to the original card game. [Open an issue](https://github.com/siemdejong/ithappens/issues/new/choose) in case of any objections."
)
st.write(
    '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">This project is open source. See <a href=https://github.com/siemdejong/ithappens><i class="fa-brands fa-github">&nbsp;</i>siemdejong/ithappens</a>.',
    unsafe_allow_html=True,
)


with tempfile.TemporaryDirectory() as tmp_dir:
    tmp_dir = Path(tmp_dir)
    with st.sidebar:
        example_data_col, additional_settings_col = st.columns(2)
        with example_data_col.popover("Download example data"):
            st.write("Download example data to get started.")
            with open(
                Path(__file__).parent.parent.parent
                / "examples"
                / "example"
                / "example.yaml",
                "rb",
            ) as yaml_file:
                st.download_button(
                    label="Input yaml",
                    data=yaml_file,
                    file_name="example.yaml",
                    mime="text/yaml",
                    icon=":material/download:",
                )
            with open(
                Path(__file__).parent.parent.parent
                / "examples"
                / "example"
                / "example.csv",
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
                Path(__file__).parent.parent.parent
                / "examples"
                / "example"
                / "example.xlsx",
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
            with open(
                Path(__file__).parent.parent.parent
                / "examples"
                / "example"
                / "images"
                / "umbrella.png",
                "rb",
            ) as logo_file:
                st.download_button(
                    label="umbrella.png",
                    data=logo_file,
                    file_name="umbrella.png",
                    mime="image/png",
                    icon=":material/download:",
                )
            with open(
                Path(__file__).parent.parent.parent
                / "examples"
                / "example"
                / "images"
                / "simple stick figure.png",
                "rb",
            ) as logo_file:
                st.download_button(
                    label="simple stick figure.png",
                    data=logo_file,
                    file_name="simple stick figure.png",
                    mime="image/png",
                    icon=":material/download:",
                )

        with additional_settings_col.popover(":material/settings: Additional settings"):
            format = st.radio("Output format", ["pdf", "png"], horizontal=True)
            side = st.radio(
                "Side(s) to generate", ["both", "front", "back"], horizontal=True
            )
            merge = st.toggle(
                ":material/picture_as_pdf: Merge output",
                value=True if format == "pdf" else False,
                disabled=True if format == "png" else False,
            )
            max_workers = 3 if IS_STREAMLIT_SHARING else os.cpu_count() + 1
            default_workers = 2 if IS_STREAMLIT_SHARING else 4
            workers = st.select_slider(
                "Number of workers",
                options=np.arange(1, max_workers),
                value=default_workers,
            )
            misery_index_desc = st.text_input(
                "Misery index description", "misery index"
            )

        expansion_name = st.text_input("Custom name", "It Happens")
        input_file = st.file_uploader("Input file (csv, xlsx, or yaml)")
        expansion_logo = st.file_uploader("Custom logo (optional)")
        images = st.file_uploader(
            "Front images (optional, required if specified)", accept_multiple_files=True
        )

        create_cards_button = st.button(
            ":material/play_arrow: Create cards", use_container_width=True
        )

        if input_file is not None and create_cards_button:
            image_dir = tmp_dir / "images"
            image_dir.mkdir()
            for image in images:
                with open(image_dir / image.name, "wb") as image_file:
                    image_file.write(image.getbuffer())

            if expansion_logo is not None:
                expansion_logo_path = image_dir / expansion_logo.name
                with open(expansion_logo_path, "wb") as expansion_logo_file:
                    expansion_logo_file.write(expansion_logo.getbuffer())
            else:
                expansion_logo_path = None

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

            try:
                create_cards(
                    name=expansion_name,
                    input_file=input_file,
                    output_dir=tmp_dir,
                    expansion_logo_path=expansion_logo_path,
                    merge=merge,
                    side=side,
                    format=format,
                    workers=workers,
                    image_dir=image_dir,
                    misery_index_desc=misery_index_desc,
                    callbacks=callbacks,
                )
            except ItHappensException as e:
                st.error(e)
                st.stop()

            pbar_callback.empty()

            archive = tmp_dir / "ithappens-output.zip"
            zip_cards(archive, tmp_dir)

            if expansion_name:
                st.warning("Please provide a custom name for your expansion.")

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

            st.components.v1.html(
                '<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="siemdejong" data-color="#FFDD00" data-emoji="🍺"  data-font="Poppins" data-text="Consider buying me a beer" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>'
            )

        elif input_file is None and create_cards_button:
            st.error(
                "Please provide an input file and click the button to create cards."
            )

    def sort_by_mi(path: Path):
        return int(path.stem.split("-")[0])

    showcase_cards = sorted((tmp_dir / "front").rglob("*.png"), key=sort_by_mi)

    if create_cards_button and len(showcase_cards):
        st.markdown("## Preview")
        st.markdown(
            "Preview your custom cards below. Download them via the button in the sidebar."
        )
        with st.container():
            columns = st.columns(len(showcase_cards))
            for card, col in zip(showcase_cards, columns):
                pil_img = Image.open(card)
                pil_img.thumbnail((256, 256), Image.Resampling.BICUBIC)
                col.image(np.array(pil_img))
    else:
        st.markdown("## Demo")
        showcase_cards = sorted(
            Path("examples/example/outputs/front").rglob("*.png"), key=sort_by_mi
        )
        with st.container():
            columns = st.columns(len(showcase_cards))
            for card, col in zip(showcase_cards, columns):
                pil_img = Image.open(card)
                pil_img.thumbnail((256, 256), Image.Resampling.BICUBIC)
                col.image(np.array(pil_img))
