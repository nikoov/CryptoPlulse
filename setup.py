from setuptools import setup, find_packages

setup(
    name="CryptoPulse",
    version="0.1.0",
    description="Cryptocurrency Market Sentiment Analysis & Price Prediction Platform",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "tweepy==4.14.0",
        "praw==7.7.1",
        "requests==2.31.0",
        "pandas==2.2.1",
        "numpy==1.26.4",
        "python-dotenv==1.0.1",
        "transformers==4.37.2",
        "torch==2.2.1",
        "nltk==3.8.1",
        "spacy==3.7.4",
        "emoji==2.10.1",
        "scikit-learn==1.6.1",
        "xgboost==2.0.3",
        "prophet==1.1.5",
        "tensorflow==2.16.1",
        "matplotlib==3.8.4",
        "seaborn==0.13.2",
        "plotly==5.22.0",
        "streamlit==1.32.0",
        "pytest==8.0.2"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 