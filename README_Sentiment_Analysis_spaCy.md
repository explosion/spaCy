Sentiment Analysis Using Logistic Regression (using spaCy)
This repository provides a Text Categorization model using logistic regression built on spaCy without using scikit-learn. It aims to classify text as positive or negative based on custom logistic regression implementation. The project includes training and testing scripts for sentiment analysis.

💬 Project Highlights
Custom Logistic Regression Model: Implemented from scratch using Python.
Natural Language Processing: Leveraging spaCy for text preprocessing (tokenization, vectorization).
No External ML Libraries: The project does not rely on external libraries like scikit-learn.

✨ Features
Text Classification: Sentiment analysis using logistic regression.
Preprocessing: spaCy is used to tokenize and vectorize text data.
Evaluation Tools: Includes scripts to evaluate the performance of the model on test datasets.
Modular Design: Easily replace datasets and tweak preprocessing steps.

📦 Installation
To begin with, you'll need Python 3.7 or higher and install spaCy and its required language model. Here's how to set it up:
pip install spacy
python -m spacy download en_core_web_lg

🚀 Quickstart
Clone the repository:
git clone https://github.com/yourusername/sentiment-analysis-logisticregression.git
cd sentiment-analysis-logisticregression

Run the logistic regression model:
python pure_Logistic.py
Test the model:
python test_pure_logistic.py

🗂️ Project Structure
│
├── spacy/                   # Contains spaCy-related pipeline and models
│   ├── pipeline/textcat/pure_Logistic.py     # SpaCy text classification models
│   └── pipeline/test_text/test_pure_Logistic.py     # Logistic regression implementation
└── README_Sentiment_Anlysis_spaCy.md                # This file

🔧 Usage
For using the model, you don't need to re-implement any functionality. The PureLogisticTextCategorizer class, which is defined in pure_Logistic.py, can be directly imported and used in your test scripts.

To execute the model:
python test_pure_logistic.py
In this file, you can import the logistic regression class as:
from pure_Logistic import PureLogisticTextCategorizer
This will allow you to run predefined test cases and evaluate the performance of the logistic regression model on your test data.


📊 Model Details
The model performs sentiment analysis by leveraging spaCy's powerful text preprocessing capabilities. The logistic regression classifier is implemented manually, without any help of scikit-learn or any other major machine learning libraries.

spaCy is used to preprocess text, including tokenization, vectorization, and feature extraction.
Logistic Regression is implemented in pure Python for binary classification (positive vs negative sentiment).

🛠️ Development
Requirements
Python 3.7+
spaCy

To install the required packages, run:
pip install spacy
python -m spacy download en_core_web_lg
Contributing
Feel free to fork the repository, make updates, and submit pull requests. Suggestions for improvements are always welcome.
