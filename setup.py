from setuptools import setup, find_packages


test_require = ["dls-signals", "pytest", "pytest-cov"]


def main():
    name = "lib-maxiv-mainiac"
    version = "2.0.0"
    description = "Base class with methods supporting MaxIV command-line programs."
    author = "KITS - Controls"
    author_email = "KITS@maxiv.lu.se"
    license = "GPLv3"
    url = "https://gitlab.maxiv.lu.se/kits-maxiv/lib-maxiv-mainiac"
    packages = find_packages(exclude=["tests", "*.tests.*", "tests.*", "tests"])
    install_requires = [
        "logging-formatter",
        "psutil",
        "setuptools",
    ]
    include_package_data = True

    setup(
        name=name,
        version=version,
        description=description,
        author=author,
        author_email=author_email,
        license=license,
        url=url,
        packages=packages,
        install_requires=install_requires,
        include_package_data=include_package_data,
        extras_require={"tests": test_require},
    )


if __name__ == "__main__":
    main()
