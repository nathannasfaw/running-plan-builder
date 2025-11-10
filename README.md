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