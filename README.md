# running-plan-builder
AI-Powered Personalized Training Plan Generation Using Data Mining and Deep Learning


## Sprint 1 Review

### Deliverables 

#### 1. Data Cleaning
- **Dataset**: 50,859 runs from 116 athletes (2009-2020)
- **Cleaning Steps**:
  - Removed extreme outliers (pace >15 min/km, distance >50 miles)
  - Filtered unrealistic speeds (<2 min/km)
  - Created derived features (pace, distance conversions)
- **Output**: `cleaned-data.csv` (50,859 rows, 9 columns)


#### 2. Feature Engineering
- **Weekly Aggregation**: Reduced 50,859 daily runs → 14,234 weekly training records
- **12 New Features Created**:
  - `weekly_mileage_change`: Week-over-week distance delta
  - `consistency_index`: 4-week rolling standard deviation
  - `recovery_ratio`: Rest days / Training days
  - `fatigue_index`: Weekly mileage / Recovery ratio
  - `cumulative_mileage`: Running total per athlete
  - `training_intensity`: 1 / pace (speed measure)
- **Filtering**: Recreational runners only (3-70 miles/week)
- **Output**: `featured-data.csv` (14,234 rows, 18 columns)


#### 3. Clustering Preparation
- **Athlete Profiles**: Aggregated to 115 athlete-level profiles
- **Feature Selection**: 6 key metrics for clustering
  - Average weekly mileage
  - Average pace (min/km)
  - Average training days per week
  - Average fatigue index
  - Average consistency index
  - Average recovery ratio
- **Scaling**: StandardScaler applied (mean=0, std=1)
- **Output**: `scaled_clustering_data.csv` (115 athletes, 6 features)

---

### Key Insights

#### Athlete Characteristics
| Metric | Mean | Median | Range |
|--------|------|--------|-------|
| Weekly Mileage | 19.0 mi | 16.9 mi | 3.0 - 69.7 mi |
| Training Days | 2.8 days | 3 days | 1 - 7 days |
| Avg Pace | 6.08 min/km | 5.79 min/km | 2.0 - 15.0 min/km |
| Recovery Ratio | 2.47 | 1.33 | 0.1 - 6.0 |

#### Feature Correlations
- **Strong positive correlation** (0.97): `avg_fatigue_index` ↔ `avg_weekly_mileage`
  - Expected since fatigue = mileage / recovery
- **Strong negative correlation** (-0.94): `avg_recovery_ratio` ↔ `avg_training_days`
  - More training days = fewer rest days
- **Moderate positive correlation** (0.71): `avg_weekly_mileage` ↔ `avg_training_days`
  - Higher volume runners train more frequently

---

### Visualizations

1. **Feature Distributions** (`feature_distributions.png`)
   - 6 histograms showing distribution of key metrics
   - Mean lines highlighted for reference
   - Confirms data quality and realistic ranges

2. **Correlation Heatmap** (`feature_correlations.png`)
   - Color-coded relationship matrix
   - Identifies redundant features
   - Guides clustering interpretation

---

### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Weekly aggregation** | Daily runs too granular; weekly patterns more meaningful for training plans |
| **StandardScaler** | K-Means uses Euclidean distance; unscaled features would bias toward larger values |
| **6 features selected** | Balance of volume, intensity, frequency, and recovery patterns |
| **Recreational filter (3-70 mi/week)** | Focus on target user segment; exclude ultra-runners and beginners |
| **Recovery ratio = 0.1 for 7-day training** | Avoid division by zero; correctly shows extreme fatigue |

---

### Project Structure

```
running-plan-builder/
├── data/
│   ├── cleaned-data.csv              # 50,859 cleaned runs
│   ├── featured-data.csv             # 14,234 weekly records
│   ├── athlete_profiles.csv          # 116 athlete averages
│   └── scaled_clustering_data.csv    # 115 athletes (scaled)
├── notebooks/
│   ├── data_cleaning.ipynb           # Data cleaning pipeline
│   ├── feature_engineering.ipynb     # Feature creation & filtering
│   └── clustering_prep.ipynb         # EDA & scaling
├── visualizations/
│   ├── feature_distributions.png     # 6 feature histograms
│   └── feature_correlations.png      # Correlation heatmap
└── README.md
```

---

### Sprint 1 Success Metrics

✅ **Data Quality**: 14,234 clean weekly records across 115 athletes  
✅ **Feature Engineering**: 12 meaningful features created  
✅ **Scaling**: Perfect normalization (mean=0, std=1)  
✅ **Visualizations**: Professional plots generated  
✅ **Documentation**: Clear notebook structure with comments 

---

## About This Project

This project uses real Strava running data to build personalized training plans through machine learning clustering. By grouping runners with similar characteristics, the system can generate adaptive, data-driven recommendations.

**Tech Stack**: Python, Pandas, Scikit-learn, Matplotlib, Seaborn




## Sprint 2 Review

### Deliverables 

#### 1. K-Means Clustering
- **Optimal Clusters**: 3 clusters identified using elbow method and silhouette analysis
- **Model Performance**:
  - Silhouette Score: 0.341 (reasonable cluster separation)
  - Inertia: 115.8
- **Athlete Distribution**:
  - Cluster 0: 38 athletes (33%)
  - Cluster 1: 39 athletes (34%)
  - Cluster 2: 38 athletes (33%)
- **Output**: `athlete_profiles_clustered_k3.csv`, `cluster_summary_k3.csv`

#### 2. Cluster Profiling & Archetypes
**Cluster 0: High-Volume Consistent Runners**
- Weekly mileage: 28.5 mi (highest)
- Training days: 3.2 days/week
- Pace: 5.8 min/km (fastest)
- Fatigue index: 37.8 (highest)
- Profile: Experienced runners maintaining high consistent volume

**Cluster 1: Low-Volume Casual Runners**
- Weekly mileage: 12.8 mi (lowest)
- Training days: 2.4 days/week
- Pace: 6.5 min/km (slowest)
- Fatigue index: 15.2 (lowest)
- Profile: Beginners or recreational runners with lower commitment

**Cluster 2: Moderate Balanced Runners**
- Weekly mileage: 19.6 mi (middle)
- Training days: 2.9 days/week
- Pace: 6.0 min/km (moderate)
- Fatigue index: 25.4 (moderate)
- Profile: Intermediate runners balancing volume and recovery

#### 3. DBSCAN Clustering Analysis
- **Implementation**: Density-based clustering with tuned eps=1.65 and min_samples
- **Results**: Identified 1 main cluster + 4 outliers
- **Limitation**: Not suitable for personalized recommendations (most athletes grouped together)
- **Comparison**: K-Means provided clearer archetypes for training plan generation

#### 4. LSTM Model Development
- **Architecture**: Sequential model with LSTM layers for time-series forecasting
- **Input**: 6-week sequences of weekly mileage
- **Output**: Next week's mileage prediction
- **Training Data**: Transformed weekly records into sequential format
- **Model Saved**: `models/lstm_model_best.keras`

---

### Key Insights

#### Cluster Comparison Analysis
| Metric | Cluster 0 (High) | Cluster 1 (Low) | Cluster 2 (Moderate) |
|--------|------------------|-----------------|----------------------|
| Avg Weekly Mileage | 28.5 mi | 12.8 mi | 19.6 mi |
| Avg Training Days | 3.2 days | 2.4 days | 2.9 days |
| Avg Pace | 5.8 min/km | 6.5 min/km | 6.0 min/km |
| Avg Fatigue Index | 37.8 | 15.2 | 25.4 |
| Avg Consistency | 5.2 | 3.8 | 4.5 |

#### Model Selection Decision
- **Chosen Model**: K-Means with k=3
- **Rationale**: 
  - Clear, interpretable athlete archetypes
  - Balanced cluster sizes for training plan diversity
  - Better silhouette score (0.341) and meaningful separation
  - DBSCAN found only 1 cluster + 4 outliers (not useful for personalization)

#### LSTM Model Performance
| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Test Loss (MSE)** | 0.0187 | Low error on scaled data |
| **MAE (Scaled)** | 0.1055 | Small average prediction error |
| **MAE** | 7.04 miles | Average prediction error in real units |
| **RMSE** | 9.12 miles | Typical prediction deviation |
| **R² Score** | 0.414 | Model explains 41.4% of variance |

**Model Interpretation:**
- **Reasonable accuracy** for 1-week-ahead mileage forecasting
- **R² of 0.414** indicates moderate predictive power (expected for human behavior)
- **MAE of 7 miles** is acceptable given weekly ranges of 3-70 miles
- **Use case**: Good enough for directional guidance ("increase", "maintain", "taper")
- **Limitation**: Not precise enough for exact mileage prescription (hence the rule-based system)

**Sample Predictions:**
```
Actual → Predicted (Error)
24.7 mi → 19.5 mi (5.2 mi)   ✓ Close
 7.4 mi →  8.9 mi (1.5 mi)   ✓ Very close
 4.3 mi → 15.5 mi (11.2 mi)  ✗ Overestimated low week
55.1 mi → 33.9 mi (21.2 mi)  ✗ Underestimated high week
37.5 mi → 43.6 mi (6.1 mi)   ✓ Close
```

---

### Visualizations

1. **Clustering Comparison** (`visualizations/clustering_comparison_kmeans_vs_dbscan.png`)
   - Side-by-side K-Means vs DBSCAN using PCA components
   - K-Means: 3 balanced clusters (Silhouette: 0.341)
   - DBSCAN: 1 main cluster + 4 outliers (not useful for personalization)
   - Visual justification for K-Means selection

2. **Cluster Comparison Report** (`reports/clustering_comparison.txt`)
   - Quantitative metrics and statistical analysis
   
3. **Cluster Profiles** (`data/cluster_profiles.json`)
   - JSON structure with detailed archetype definitions
   - Used for rule-based recommendation system

---

### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **k=3 clusters** | Optimal balance between specificity and generalization; clear elbow in inertia plot |
| **K-Means over DBSCAN** | More interpretable archetypes; DBSCAN grouped 96% of athletes into one cluster |
| **PCA for visualization** | Reduced 6D feature space to 2D while preserving cluster structure |
| **6-week LSTM sequences** | Captures training cycle patterns while maintaining sufficient training samples |
| **Keras Sequential model** | Simple architecture suitable for univariate time-series forecasting |
| **MSE loss function** | Standard for regression tasks; aligns with RMSE evaluation metric |

---

### Project Structure Update

```
running-plan-builder/
├── data/
│   ├── athlete_profiles_clustered_k3.csv  # Athletes with cluster labels
│   ├── cluster_summary_k3.csv             # Cluster statistics
│   └── cluster_profiles.json              # Archetype definitions
├── models/
│   └── lstm_model_best.keras              # Trained LSTM model
├── notebooks/
│   ├── clustering.ipynb                   # Clustering implementation
│   └── lstm_model.ipynb                   # LSTM training pipeline
├── reports/
│   ├── clustering_comparison.txt          # Model comparison analysis
│   └── clustering_summary_k3.txt          # Final cluster report
├── visualizations/
│   └── clustering_comparison_kmeans_vs_dbscan.png
└── README.md
```

---

### Sprint 2 Success Metrics

✅ **Clustering**: 3 clear athlete archetypes identified  
✅ **Model Comparison**: K-Means vs DBSCAN analysis completed with visualization  
✅ **LSTM Architecture**: Sequential model trained with R²=0.414  
✅ **Forecasting Accuracy**: MAE of 7.04 miles on test set  
✅ **Data Pipeline**: Weekly sequences prepared for forecasting  
✅ **Documentation**: Cluster profiles exported to JSON  
✅ **Model Persistence**: Trained models saved for deployment  
✅ **Visualization**: PCA-based cluster comparison plot created  

---

### Next Steps (Sprint 3)

- Integrate clustering and LSTM models into recommendation pipeline
- Build rule-based expert system using cluster profiles
- Connect OpenAI API for natural language generation
- Develop Streamlit web interface
- Complete end-to-end testing and final report

**Tech Stack**: Python, Pandas, Scikit-learn, TensorFlow/Keras, Matplotlib, Seaborn

## Sprint 3 Review

### Deliverables

#### 1. **Personalized Plan Generation Web App**
- **Streamlit UI**: Modern, earth-tone themed interface with Quick and Advanced modes.
    - **Quick Plan**: Minimal input for new runners.
    - **Advanced Plan**: Collects 6 weeks of mileage, fatigue, training days, and race goals for personalized recommendations.
- **User Experience**: 
    - Sidebar collects all relevant inputs.
    - Main area displays a structured summary, a single weekly schedule table, and coach’s advice.
    - Table includes day-by-day activities, mileage, time, and pace for each workout.

#### 2. **LSTM Integration for Mileage Prediction**
- **Advanced Mode**: Uses a trained LSTM model to predict next week’s mileage based on the user’s last 6 weeks.
- **Fallback**: If LSTM is unavailable, uses a rule-based estimate (average of last 3 weeks + 5%).

#### 3. **LLM-Driven Plan Explanation**
- **Gemini (Google AI Studio) API**: Generates friendly, motivating, and structured training plans.
- **Prompt Engineering**: Ensures the LLM outputs:
    - A summary of workout types for the week.
    - A single Markdown table with columns: Day, Activity, Mileage (mi), Time (min), Pace.
    - Coach’s advice and encouragement (no repeated schedule in prose).
- **Robust Table Extraction**: App parses and displays only the LLM’s Markdown table, ensuring clarity.

#### 4. **Rule-Based Recommender System**
- **Cluster Archetypes**: Uses K-Means cluster profiles to tailor recommendations.
- **Action Mapping**: Internal codes (e.g., `progressive_build`) mapped to human-friendly phrases for LLM and UI.

#### 5. **Code & UI Improvements**
- **Error Handling**: Improved feedback for model/API errors.
- **Styling**: Enhanced layout, font, and color palette for a professional look.
- **Table Parsing**: Handles LLM output robustly, displaying only the intended weekly schedule.

---

### Key Insights

- **LSTM Model**: Useful for directional mileage guidance, but not precise for exact weekly prescriptions (MAE ~7 miles, R² ~0.41).
- **LLM Output**: Prompt engineering is critical for structured, actionable plans.
- **User Experience**: Offering both quick and advanced modes increases accessibility and personalization.

---

### Visualizations & Features

- **Weekly Plan Table**: Day-by-day schedule with mileage, time, and pace.
- **Coach’s Advice**: Motivational, context-aware explanations.
- **Modern UI**: Earth-tone theme, card-based layout, and clear separation of summary, schedule, and advice.

---

### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **LLM Table Output** | Ensures clarity and easy parsing for the UI |
| **LSTM for Advanced Users** | Personalizes mileage progression based on real history |
| **Cluster-based Recommender** | Matches users to archetypes for safe, effective plans |
| **Quick/Advanced Modes** | Balances ease-of-use and personalization |
| **Markdown Table Parsing** | Guarantees a single, clean schedule display |

---

### Project Structure Update

```
running-plan-builder/
├── app.py                         # Streamlit web app
├── llm_handler.py                 # LLM prompt & response handler
├── recommender.py                 # Rule-based recommendation logic
├── mileage_predictor.py           # LSTM mileage prediction
├── models/
│   └── lstm_model_best.keras      # Trained LSTM model
├── data/
│   ├── athlete_profiles_clustered_k3.csv
│   ├── cluster_summary_k3.csv
│   └── cluster_profiles.json
├── notebooks/
│   ├── clustering.ipynb
│   ├── lstm_model.ipynb
│   └── ...
├── visualizations/
│   └── clustering_comparison_kmeans_vs_dbscan.png
└── README.md
```

---