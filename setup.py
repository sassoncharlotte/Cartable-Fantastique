import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cartable-fantastique",
    version="0.1.0",
    author="Charlotte Sasson, Ali Charara & Benjamin Poux",
    description="Adaptation automatique d'exercices pour le cartable fantastique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=['fantastic', 'tagging'],
    python_requires=">=3.6",
    install_requires=[
        "xmltodict==0.12.0",
        "pandas==1.3.3",
        "nltk==3.6.3",
        "openpyxl==3.0.7",
        "jinja2==3.0.1",
        "spacy==3.1.3",
        "transformers==4.10.3",
        "sentencepiece==0.1.96",
        "protobuf==3.18.0",
        "pylint==2.11.1",
        "python-Levenshtein==0.12.2",
        "simpletransformers==0.62.2",
        "scikit-learn==1.0",
        "scipy==1.7.1",
        "fastapi==0.70.0",
        "uvicorn[standard]",
    ],
)
