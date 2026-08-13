# Curriculum-Industry Skill Feature Store Using Feast

A simple Feast-based feature store for analyzing curriculum-industry skill gaps and predicting whether a student is ready for industry.

## Student Details

- **Name:** Sri Nayana Kanaparthi
- **Register Number:** 231FA04C32
- **Section:** 3

## Problem Statement

University curricula provide academic knowledge, but they may not always provide the practical skills expected by industry. This project analyzes the difference between curriculum-level skill coverage and industry-level proficiency for students.

The project uses engineered skill-gap features with Feast. Feast provides historical feature retrieval for model training and online feature retrieval for prediction. A Logistic Regression model uses the retrieved features to predict whether a student is industry-ready.

## Dataset

### Dataset name

`curriculum_industry_skill_gap.csv`

### Dataset description

This is a synthetic curriculum-industry skill-gap dataset created for academic demonstration. Each row represents a student assessment at a particular timestamp.

- **Number of records:** 80
- **Number of skills:** 5
- **Entity:** `student_id`
- **Timestamp:** `event_timestamp`
- **Target:** `target_readiness`

The five evaluated skills are:

1. Python
2. SQL
3. Machine Learning
4. Cloud Computing
5. Communication

Each skill has two ratings on a scale from 1 to 5:

- `*_curriculum`: academic curriculum coverage.
- `*_industry`: practical industry proficiency.

### Dataset columns

| Column | Description |
|---|---|
| `student_id` | Unique student identifier and Feast entity key |
| `event_timestamp` | Timestamp of the student assessment |
| `curriculum_track` | Student's academic or technical track |
| `python_curriculum` | Curriculum rating for Python |
| `python_industry` | Industry rating for Python |
| `sql_curriculum` | Curriculum rating for SQL |
| `sql_industry` | Industry rating for SQL |
| `ml_curriculum` | Curriculum rating for machine learning |
| `ml_industry` | Industry rating for machine learning |
| `cloud_curriculum` | Curriculum rating for cloud computing |
| `cloud_industry` | Industry rating for cloud computing |
| `communication_curriculum` | Curriculum rating for communication |
| `communication_industry` | Industry rating for communication |
| `internship_months` | Duration of internship exposure |
| `projects_completed` | Number of relevant projects completed |
| `certification_count` | Number of relevant certifications |
| `industry_experience_months` | Industry experience in months |
| `target_readiness` | Target label: 0 means not ready and 1 means industry-ready |

### How the entries were created

The dataset is synthetic. The records were generated with realistic ranges for academic skill ratings, industry skill ratings, internships, projects, certifications, and industry experience.

The `target_readiness` label was generated from a weighted readiness score based on industry proficiency, project experience, internship exposure, certifications, industry experience, and skill gaps. The target column is used as the model label and is not included in the Feast FeatureView to prevent target leakage.

## Feature Engineering

Feature engineering is performed by `prepare_data.py`. The script reads the original CSV file and writes the engineered features to:

```text
data/skill_gap_features.parquet
```

### Skill-gap calculation

For every skill, the gap is calculated as:

```text
skill_gap = curriculum_rating - industry_rating
```

For example:

```text
python_gap = python_curriculum - python_industry
```

A positive value means that curriculum coverage is higher than practical industry proficiency for that skill.

### Feast features

| Feature | Meaning |
|---|---|
| `python_gap` | Difference between Python curriculum and industry ratings |
| `sql_gap` | Difference between SQL curriculum and industry ratings |
| `ml_gap` | Difference between machine-learning curriculum and industry ratings |
| `cloud_gap` | Difference between cloud curriculum and industry ratings |
| `communication_gap` | Difference between communication curriculum and industry ratings |
| `average_skill_gap` | Average gap across all five skills |
| `industry_skill_average` | Average industry rating across all five skills |
| `projects_completed` | Number of completed practical projects |
| `internship_months` | Number of months of internship exposure |
| `certification_count` | Number of industry-related certifications |
| `industry_experience_months` | Industry experience in months |
| `project_experience_score` | Normalized project score between 0 and 1 |
| `internship_experience_score` | Normalized internship score between 0 and 1 |
| `certification_score` | Normalized certification score between 0 and 1 |
| `industry_experience_score` | Normalized industry experience score between 0 and 1 |

The target `target_readiness` is intentionally excluded from the FeatureView because it is the prediction label.

## Feast Architecture

```text
Original Dataset
curriculum_industry_skill_gap.csv
        |
        v
Feature Engineering
prepare_data.py
        |
        v
Parquet Offline Data
data/skill_gap_features.parquet
        |
        v
Feast FeatureView
skill_gap_features
        |
        +-----------------------------+
        |                             |
        v                             v
Historical Feature Retrieval      Materialization
get_historical_features()         feast materialize
        |                             |
        v                             v
Model Training                   SQLite Online Store
train_model.py                   data/online_store.db
                                      |
                                      v
                              Online Feature Retrieval
                              get_online_features()
                                      |
                                      v
                                  Prediction
```

## Feast Implementation

### Entity

The Feast entity is `student`. Its join key is `student_id`, which uniquely identifies each student record for feature retrieval.

```python
student = Entity(
    name="student",
    join_keys=["student_id"],
    description="Student skill-gap entity",
)
```

### Data source

The data source is a local Parquet file created by `prepare_data.py`:

```text
data/skill_gap_features.parquet
```

The Feast `FileSource` uses `event_timestamp` to perform time-aware historical joins.

### FeatureView

The FeatureView is named `skill_gap_features`. It contains the engineered skill gaps, industry skill averages, practical experience features, and normalized experience scores.

The FeatureView is online-enabled so that its values can be materialized into the SQLite online store and retrieved during prediction.

### Historical retrieval

Historical features are retrieved using:

```python
historical_df = store.get_historical_features(
    features=feature_refs,
    entity_df=entity_df,
).to_df()
```

The entity dataframe contains:

- `student_id`
- `event_timestamp`
- `target_readiness`

The resulting historical dataframe is used to train the machine-learning model.

### Model

A Logistic Regression model is trained using the Feast historical features. The model uses a `StandardScaler` followed by `LogisticRegression`.

The target is:

```text
target_readiness
```

The target values have the following meaning:

- `0`: Student is not predicted to be industry-ready.
- `1`: Student is predicted to be industry-ready.

### Online retrieval

After materialization, online features are retrieved using:

```python
online_data = store.get_online_features(
    features=feature_refs,
    entity_rows=[{"student_id": "S080"}],
).to_dict()
```

The returned online features are passed to the trained model to generate the final prediction.

## Execution Instructions

### Install dependencies

```bash
pip install -r requirements.txt
```

For Google Colab:

```python
!pip install -q feast==0.53.0 pandas pyarrow scikit-learn joblib
```

### Step 1: Engineer features

```bash
python prepare_data.py
```

This creates:

```text
data/skill_gap_features.parquet
```

### Step 2: Register Feast objects

```bash
feast apply
```

This registers the entity and FeatureView in the Feast registry.

### Step 3: Retrieve historical features

```bash
python historical_features.py
```

This creates:

```text
data/historical_features.parquet
```

### Step 4: Materialize features

```bash
feast materialize 2026-01-01T00:00:00 2026-12-31T23:59:59
```

This loads feature values into:

```text
data/online_store.db
```

### Step 5: Train the model

```bash
python train_model.py
```

### Step 6: Retrieve online features and predict

```bash
python online_features.py
```

## Results

### Historical feature output

Historical features were retrieved from the Parquet offline store using Feast's `get_historical_features()` method.

Example generated columns include:

```text
student_id
event_timestamp
python_gap
sql_gap
ml_gap
cloud_gap
communication_gap
average_skill_gap
industry_skill_average
projects_completed
internship_months
certification_count
industry_experience_months
target_readiness
```

The generated historical output is stored in:

```text
data/historical_features.parquet
```

### Model accuracy

The Logistic Regression model was trained using Feast historical features.

```text
Model accuracy: 0.9000
```

### Online feature output

Online features were retrieved from the SQLite online store after materialization.

Example entity used for online retrieval:

```text
student_id = S080
```

The online feature output was:

```text
  student_id  internship_months  industry_skill_average  projects_completed  \
0       S080                  4                      1.6                   4

   sql_gap  ...  certification_score  industry_experience_score  python_gap  \
0     -1.0  ...                  0.5                   0.166667         1.0

   cloud_gap  internship_experience_score
0        0.0                    0.333333

[1 rows x 16 columns]
```

### Final prediction

The final prediction was generated using the online features retrieved from the SQLite online store.

```text
Student: S080
Final prediction: 0
Readiness probability: 0.0002
```

Interpretation: Student `S080` is predicted as not industry-ready by the trained model and may require additional training.

## Required Analysis Answers

### 1. What is the entity in your Feast implementation?

The entity is `student`. The entity join key is `student_id`, which uniquely identifies each student record for feature retrieval.

### 2. List the features stored in your FeatureView.

The FeatureView stores:

- `python_gap`
- `sql_gap`
- `ml_gap`
- `cloud_gap`
- `communication_gap`
- `average_skill_gap`
- `industry_skill_average`
- `projects_completed`
- `internship_months`
- `certification_count`
- `industry_experience_months`
- `project_experience_score`
- `internship_experience_score`
- `certification_score`
- `industry_experience_score`

### 3. Explain how one feature was calculated.

The `python_gap` feature was calculated as:

```text
python_gap = python_curriculum - python_industry
```

For example, if a student's Python curriculum rating is 5 and industry rating is 3, then:

```text
python_gap = 5 - 3 = 2
```

### 4. What is the difference between your original dataset and the feature dataset?

The original dataset contains raw curriculum ratings, industry ratings, and student-experience information. The feature dataset contains transformed and engineered values such as skill gaps, average skill gap, industry skill average, and normalized experience scores.

The feature dataset is stored in Parquet format and is used as the Feast offline data source.

### 5. What is the purpose of the offline store?

The offline store keeps historical feature data. It is used to create training datasets, perform point-in-time feature retrieval, and support batch model training.

In this project, the engineered Parquet file acts as the offline data source.

### 6. What is the purpose of the online store?

The online store keeps the latest materialized feature values for fast retrieval during prediction. In this project, SQLite is used as the local online store.

### 7. What is the purpose of `feast apply`?

`feast apply` reads the Feast definitions and registers the entity, data source, and FeatureView in the Feast registry. It creates or updates the metadata needed by the feature store.

### 8. What does materialization do?

Materialization copies feature values from the offline data source into the online store for a specified time range. After materialization, the model can retrieve features using an entity key such as `student_id`.

### 9. What is the advantage of retrieving features through Feast instead of manually calculating them separately during training and prediction?

Feast provides a consistent feature definition for both training and prediction. This reduces training-serving skew because the same feature names and calculations are used in both workflows.

Feast also supports point-in-time-correct historical retrieval, which reduces the risk of using information that would not have been available at the time of prediction.

### 10. State two limitations of your current dataset.

1. The dataset is synthetic and may not represent the full complexity of real student performance or industry requirements.
2. The dataset contains only five skills and a limited number of student records, so the model may not generalize well to different institutions, job roles, or industries.

### 11. State two ways your feature store could be improved when more curriculum and industry evidence becomes available.

1. Add real evidence from job descriptions, internship evaluations, employer surveys, coding assessments, project repositories, and placement outcomes.
2. Add more detailed and time-dependent features, such as skill assessment history, changing job-market demand, course completion dates, project quality scores, and separate FeatureViews for different job roles.

## Limitations

This project is intended for local educational demonstration. It uses a synthetic dataset, a local Parquet offline source, and SQLite as the online store. A production system would require stronger data validation, access control, monitoring, feature versioning, and a scalable online infrastructure.

## Repository Files

```text
curriculum_industry_skill_gap.csv
prepare_data.py
feature_definitions.py
feature_store.yaml
requirements.txt
README.md
```

Generated local files such as the Feast registry and SQLite database should not be committed:

```text
data/registry.db
data/online_store.db
__pycache__/
.venv/
```
