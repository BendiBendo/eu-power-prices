# European day-ahead electricity prices: electricity, gas and carbon

Personal project (in progress). What drives day-ahead electricity prices in Europe, starting with Spain,
and how gas and EU ETS carbon prices feed into them.

## Questions
1. How do solar, wind and demand shape the daily price profile (by season)?
2. How does price relate to **residual load** (demand - wind - solar)? What does it say about the merit order?
3. How do Spain, France, Germany and the Netherlands differ (profiles, negative-price hours, spreads)?
4. Do prices follow the marginal cost of gas plants (TTF gas, EUA carbon)? **Clean spark spread**.
5. Simple forecast vs naive baseline (features known before the auction only).

## Plan
- [ ] Block A: Spain, exploration + residual load (OMIE or ENTSO-E)
- [ ] Block B: add FR, DE, NL and compare
- [ ] Block C: gas (TTF) and carbon (EUA) series, clean spark spread
- [ ] Block D: synthesis (3 numbers)
- [ ] Block E: forecasting (baseline vs ML, time-based split, no leakage)

## Data
- ENTSO-E Transparency Platform: prices, generation by type, load, day-ahead forecasts.
- Gas and carbon prices: source and limits to document here (frequency, gaps).
Raw data are not committed.

## Run
```bash
pip install -r requirements.txt
export ENTSOE_API_KEY="..."        # never commit the token
python src/download_entsoe.py --countries ES --start 2024-01-01 --end 2024-12-31   # test on one year first
jupyter notebook notebooks/01_exploration.ipynb
```

## Key findings
*(to fill in: 3 numbers you can say in 30 seconds)*

## Limits
Analysis and backtests only; no real trading. Check time resolution (hourly vs 15 min) across countries and series.
