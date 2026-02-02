from setuptools import setup, find_packages

setup(
    name="adb_tool",
    version="1.0.0",
    description="A cross-platform GUI tool for ADB commands",
    author="Antigravity",
    packages=find_packages(),
    install_requires=[
        "ttkbootstrap>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "adb-tool=adb_tool.main:main",
        ],
    },
    python_requires=">=3.6",
)
