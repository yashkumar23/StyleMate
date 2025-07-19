# 💳 StyleMate - An AI Powered Personalized Fashion Assistant

## 📌 Project Overview & Task Objective

The project focused on 
suggesting personalized fashion to users based on their physical attributes like skintone, gender and body measurments. The 
primary objective is to build a AI based personalized fashion App that can accurately determine 
what suits better to a user considering their physical attributes.

## 📂 Dataset Information

The project utilizes the custom built datasets for skintone and gender detection, for body measurement we have used the TrainingDataPro/body-measurements-dataset from huggingface and indofashion dataset for clothing recommendations.
The dataset contains full human body images equally distributed among male and female gender.  

## ✨ Features

- Skintone Detection.
- Gender Detection.
- Body Measurements Detection.
- CLothing recommendations based on these physical attributes.

## 🛠️ Installation

To run this notebook locally, you will need Python installed. 

## 🚀 Approach

My approach to credit risk prediction involved the following steps:

- **Library Import**: Imported essential Python libraries for data manipulation
  (pandas, numpy), visualization (matplotlib, seaborn), and machine learning
  (sklearn).
  
- **Data Loading**: Loaded the `train.csv`  dataset into a pandas DataFrame.

- **Data Cleaning and Preparation**:
  - **Handle Missing Values**: Categorical features were imputed using the mode,
    and numerical features (like `LoanAmount` ) were imputed using the median.
  - **Encode Categorical Variables**: Binary categorical variables were transformed
    using `LabelEncoder` , while multiclass variables were converted using one-
    hot encoding ( `pd.get_dummies` ).
    
- **Exploratory Data Analysis (EDA)**: Analyzed feature distributions and their
    relationships with the `Loan_Status`  target variable. A key visualization included
    plotting `Credit_History`  against `Loan_Status`  to understand their correlation.
  
- **Model Training and Testing**:
    The dataset was split into training and testing sets (80/20 split).
  - **Random Forest Classifier**: A Random Forest model was trained with 
      `max_depth=5` .
  - **Logistic Regression**: A Logistic Regression model was trained for binary
      classification.
  - **Decision Tree**: A Decision Tree Classifier was trained.

- **Model Evaluation**: Evaluated the trained models using accuracy score, confusion
    matrices, and classification reports to assess their performance in predicting loan
    approval.

## 🧰 Technologies Used
- P Y T H O N
- N U M P Y
- MA T P L O T L I B
- S E A B O R N
- S C I K I T - L E A R N
- M E D I A P I P E
- R O B O F L O W
- O P E N C V

## 📊 Results and Insights

### Key Insights:
  - **Credit History Impact**: The analysis clearly showed that credit history is a strong 
      predictor of loan approval. Applicants with a good credit history (Credit_History = 1) had 
      a significantly higher chance of loan approval, while those with a bad credit history 
      (Credit_History = 0) were mostly rejected.
  - **Model Performance**: The Logistic Regression model achieved an accuracy of `(78.86%)`, 
      outperforming the Decision Tree model `(69.11%)`. This indicates that Logistic Regression 
      is more suitable for this dataset given the features and their relationships.
  - **Confusion Matrices**: The confusion matrices for both models provided a detailed 
      breakdown of `true positives`, `true negatives`, `false positives`, and `false negatives`, offering 
      insights into where each model performed well and where it struggled.
    
### Final Outcome:
  - The project successfully demonstrates a workflow for credit risk prediction, from data preprocessing to model evaluation.
  - The Logistic Regression model proved to be effective in predicting loan approval status based on the given features. 
  - Further improvements could involve hyperparameter tuning or exploring more advanced ensemble methods.

## 🧪 Usage

```bash
# 1. Clone the repository
git clone https://github.com/your-username/StyleMatw.git

# 2. Navigate to the project directory
cd stylemate

# 3. Open the cmd to activate the environment 
venv\Scripts\activate

# 4. install flask-migrate
pip install flask_migrate

# 5. Run the App
python -m src.main 
```

## 🤝 Contributing

Contributions are welcome! If you have any suggestions or improvements, please open 
an issue or submit a pull request.

## 📬 Contact

For questions or collaboration:
- GitHub: `yashkumar23`
- Email: `yashchhatani7@gmail.com`.
