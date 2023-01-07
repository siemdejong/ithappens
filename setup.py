from setuptools import setup
from babel.messages import frontend as babel
from setuptools.command.install import install


class CompileLocalesCatalog(install):
    def run(self):
        """
        Performs the usual install process and then copies the True Type fonts
        that come with shithappens into matplotlib's True Type font directory,
        and deletes the matplotlib fontList.cache.
        """
        # Perform the usual install process
        self.execute(babel.compile_catalog, (), "Compile locales catalog.")
        install.run(self)


setup(
    cmdclass={
        "compile_catalog": babel.compile_catalog,
        "extract_messages": babel.extract_messages,
        "init_catalog": babel.init_catalog,
        "update_catalog": babel.update_catalog,
        "install": CompileLocalesCatalog,
    }
)
