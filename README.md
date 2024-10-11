<a name="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![PyPI][pypi-shield]][pypi-url]
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GPLv3 License][license-shield]][license-url]



<br />
<div align="center">

<h3 align="center">It Happens</h3>

  <p align="center">
    Create your own <a href="https://boardgamegeek.com/boardgame/196379/ithappens">Shit Happens</a> playing cards!
    <br />
    <a href="https://ithappens.streamlit.app/"><strong>Go to the app »</strong></a>
  </p>
</div>



![Front: "You don't know how to use this tool. Misery index 80"](https://raw.githubusercontent.com/siemdejong/ithappens/main/examples/example/outputs/front/80-you-dont-know-how-to-use-this-tool.png)  |  ![Back: It Happens, Example expansion](https://raw.githubusercontent.com/siemdejong/ithappens/main/examples/example/outputs/back/80-you-dont-know-how-to-use-this-tool.png)
:-------------------------:|:-------------------------:
Front             |  Back


Ever wanted to play with your own [Shit Happens](https://boardgamegeek.com/boardgame/196379/ithappens) playing cards?
Now you can.
Write down the most miserable situations you can think of and rank them.
This project automatically outputs playing cards in pdf format.

This project is not related to the original card game.
[Open an issue](https://github.com/siemdejong/ithappens/issues/new/choose) in case of any objections.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


# Getting started

## App

The tool is available as an online [app](https://ithappens.streamlit.app).

## CLI
The tool is also available as a command line interface (CLI), see [Local installation](#local-installation).
The tool requires an Excel or csv input file and optionally an expansion logo.
The input files must have header "misery index" and "situation" and optional "image" for the front image.
If an image name is given (stem + ext), it must live in the image dir, given by the optional third positional argument.
See the examples directory for an example.
```
Usage: ithappens create [OPTIONS] INPUT_FILE OUTPUT_DIR [IMAGE_DIR]

  Create cards.

Options:
  -n, --name TEXT                 Expansion name. If no name is specified,
                                  infers name from input_dir.
  -m, --merge                     Merge output.
  -s, --side [front|back|both]    Side(s) to generate.
  -e, --expansion_logo_path FILE  Expansion logo path.
  -f, --format [pdf|png]          Output format.
  -w, --workers INTEGER           Number of workers.
  --help                          Show this message and exit.
```

If the output folder does not exist, it will be created.
The format of the expansion logo must be on [this list](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


# Local installation
The app can be installed with `pip install ithappens`.

## Prerequisites

A virtual environment with python 3.9 or higher.

## Installing for developers

### Retrieve the latest version of the code
Developers should fork this repository and run
```
git clone https://github.com/<your-username>/ithappens.git
```
This will place the sources in a directory `ithappens` below your current working directory, set up the `origin` remote to point to your own fork, and set up the `upstream` remote to point to the `ithappens` main repository.
Change into this directory before continuing:
```
cd ithappens
```

### Create a dedicated environment
You should set up a dedicated environment to decouple your ithappens development from other Python and ithappens installations on your system.

### Installing ithappens in editable mode
Install ithappens in editable mode from the ithappens directory using the command
```
python -m pip install -e .[dev]
```
The 'editable/develop mode', builds everything and places links in your Python environment so that Python will be able to import ithappens from your development source directory.
This allows you to import your modified version of ithappens without re-installing after every change.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


# Contributing

Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Built With

[![Python][Python]][Python-url]
[![Streamlit][Streamlit]][Streamlit-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


# License

Distributed under the GPL-3.0 license. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[pypi-shield]: https://img.shields.io/pypi/v/ithappens?color=blue&logoColor=yellow&style=for-the-badge
[pypi-url]: https://pypi.org/project/ithappens/
[contributors-shield]: https://img.shields.io/github/contributors/siemdejong/ithappens.svg?style=for-the-badge
[contributors-url]: https://github.com/siemdejong/ithappens/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/siemdejong/ithappens.svg?style=for-the-badge
[forks-url]: https://github.com/siemdejong/ithappens/network/members
[stars-shield]: https://img.shields.io/github/stars/siemdejong/ithappens.svg?style=for-the-badge
[stars-url]: https://github.com/siemdejong/ithappens/stargazers
[issues-shield]: https://img.shields.io/github/issues/siemdejong/ithappens.svg?style=for-the-badge
[issues-url]: https://github.com/siemdejong/ithappens/issues
[license-shield]: https://img.shields.io/github/license/siemdejong/ithappens.svg?style=for-the-badge
[license-url]: https://github.com/siemdejong/ithappens/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot-front]: images\80-you-dont-know-how-to-use-this-tool-front.png
[product-screenshot-back]: images\80-you-dont-know-how-to-use-this-tool-back.png
[Python]: https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/
[Streamlit]: https://img.shields.io/badge/Streamlit-1E0A31?style=for-the-badge&logo=streamlit&logoColor=E81A1A
[Streamlit-url]: https://streamlit.io/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
