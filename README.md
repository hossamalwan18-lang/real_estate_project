# Egypt Real Estate Price Prediction

Predicting asking prices of residential properties for sale in Egypt using machine learning.

## Data
- Source: "Egypt Property Finder — Cleaned" on Kaggle (47,420 listings scraped from propertyfinder.eg on 19 Feb 2026).
- Filtered to **17,483 residential for-sale listings** (rentals and commercial/administrative units excluded).
- These are **asking prices** from a single day, not transaction prices.

## Approach
1. Filtered the data to residential sale listings and checked price distribution and outliers.
2. Used `log(price)` as the target because prices are heavily right-skewed.
3. Features: size, bedrooms, bathrooms, property type, region, city, district, compound, latitude/longitude, distance to city center, amenity rank. (`value_per_sqm` was excluded to avoid data leakage.)
4. 80/20 train/test split, compared three models.

## Results
| Model | R² | MAE (log) | Median % error |
|---|---|---|---|
| Linear Regression (baseline) | 0.615 | 0.404 | - |
| HistGradientBoosting | 0.782 | 0.285 | 20.0% |
| **Random Forest** | **0.796** | **0.264** | **17.5%** |

## Key findings
- **Size** is the strongest single predictor, followed by property type and distance to the center.
- **Location as a group matters a lot**: shuffling all location columns together drops R² by about 0.36 (from 0.80 to about 0.43).

![Feature importance](images/feature_importance.png)
![Predicted vs actual](images/predicted_vs_actual.png)

## Limitations
- Asking prices from a single day: no trends, and negotiated prices are not captured.
- Heavy geographic concentration in Cairo and Giza ([75.2%]% of listings), so the model is less reliable elsewhere.
- The model overestimates very cheap listings and underestimates very expensive ones (visible in the plot above).
- Similar listings in the same compound may appear in both train and test sets, so the scores may be slightly optimistic.

## Tools
Python, pandas, NumPy, scikit-learn, matplotlib

## How to run
1. Download `cleaned_all_egypt.csv` from the Kaggle dataset page and place it next to the notebook.
2. Install requirements: `pip install pandas numpy matplotlib scikit-learn`
3. Run `egypt_real_estate_analysis.ipynb`.