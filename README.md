# European day-ahead electricity prices: electricity, gas and carbon

Personal project. What drives day-ahead electricity prices in Europe, starting with Spain (2024), and how gas (TTF) and EU ETS carbon (EUA) prices feed into them.

**Status:** Spain exploration and residual load (notebook 01) and gas / carbon / clean spark spread (notebook 02) are done. Other countries and forecasting are planned, not done.

## Key findings (Spain, 2024)

1. **784 hours (8.9 %) at a price of 0 or below.** 65 % of them in spring and 80 % between 10:00 and 17:59, i.e. when solar output is high.
2. **Residual load explains about half of the hourly price variance.** About +5 EUR/MWh per additional GW of residual load (demand - wind - solar), R2 = 0.53, correlation 0.73.
3. **The price is below the cost of a gas plant most of the time.** Mean day-ahead price 63 EUR/MWh vs a gas plant marginal cost of about 96 EUR/MWh (efficiency 0.50). Mean clean spark spread -33 EUR/MWh, with only 18 % of days positive (6 % to 35 % for efficiencies 0.45 to 0.60).

More detail:

- **Evening vs midday.** In summer, the mean price is about 107 EUR/MWh at 20-22 h against 40 at 12-15 h. The clean spark spread is about -57 EUR/MWh at 12-15 h (5 % of hours positive) and about -5 at 20-22 h (53 % positive): in the evening the price comes close to the cost of a gas plant, at midday it is far below. This is consistent with gas being near the margin once solar is gone; it is not a test of who sets the price.
- **Gas matters more than carbon in the daily variation.** Daily correlation of the price with the marginal cost is 0.66, with TTF alone 0.67, with the EUA alone 0.25. Carbon is a nearly constant share of the cost (about 28 %, 27 EUR/MWh). A move of 10 EUR/t in the EUA changes the marginal cost by about 4 EUR/MWh (0.202 x 10 / 0.5).
- **Seasons.** The spread is closest to zero in November-December and most negative from March to May (no positive day). The solar share alone does not explain the spring gap (daily R2 of the spread on the solar share: 0.05); hydro, wind and lower demand are untested candidates.
- **Robustness.** Aligning gas and carbon prices on the same day, D-1 or D-2 gives the same result (correlation 0.65-0.66, mean spread about -33 EUR/MWh).

Figures are in `figures/`.

![Marginal cost vs price](figures/02_spread_over_time.png)
![Spread by hour](figures/02_spread_by_hour.png)

## Questions

1. How do solar, wind and demand shape the daily price profile, by season? *(notebook 01, done)*
2. How does the price relate to residual load, and what does it say about the merit order? *(notebook 01, done)*
3. Do prices follow the marginal cost of gas plants (TTF, EUA)? Clean spark spread. *(notebook 02, done)*
4. How do Spain, France, Germany and the Netherlands differ? *(planned)*
5. Simple forecast vs naive baseline, using only information known before the auction. *(planned)*

## Plan

- [x] Block A: Spain, exploration and residual load (`notebooks/01_exploration.ipynb`)
- [ ] Block B: add FR, DE, NL and compare
- [x] Block C: gas (TTF) and carbon (EUA) series, marginal cost, clean spark spread (`notebooks/02_gas_carbon_spread.ipynb`)
- [x] Block D: synthesis (this README)
- [ ] Block E: forecasting (baseline vs ML, time-based validation, no leakage)

## Data

| Series                                                               | Source                                                    | Frequency             | Notes                                                                  |
| -------------------------------------------------------------------- | --------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------- |
| Spain day-ahead price, generation by type, load, day-ahead forecasts | ENTSO-E Transparency Platform (via `entsoe-py`)           | hourly after cleaning | Downloaded with `src/download_entsoe.py`; token in `.env`              |
| Gas                                                                  | Yahoo Finance, ticker `TTF=F`                             | daily close           | Front-month TTF future, continuous series                              |
| Carbon                                                               | Investing.com, "Carbon Emissions Futures Historical Data" | daily close           | Nearest-December EUA future, continuous series, CSV downloaded by hand |

Raw and processed data are not committed. To rebuild: run the download script, then save the carbon CSV as `data/raw/Carbon Emissions Futures Historical Data.csv` (daily, 2023-12-01 to 2025-01-03). The TTF series is downloaded once and cached in `data/raw/ttf_daily.csv`. Data from third-party sites is for personal, non-commercial use.

## Method

- **Time handling.** Source CSVs mix UTC offsets, so timestamps are parsed in UTC and converted to `Europe/Madrid`. Quarter-hourly or sub-hourly values are averaged to hourly means (MW are averaged, never summed). Short gaps (up to 3 hours) are interpolated; forecast series are not interpolated. Audit of gaps and daylight-saving days is in notebook 01.
- **Residual load** = load - wind - solar, realised values.
- **Marginal cost of a gas plant** (EUR/MWh of electricity) = (gas price + EF x carbon price) / efficiency.
  - EF = 0.202 tCO2 per MWh of gas: IPCC 2006 Guidelines, vol. 2, ch. 2, table 2.2 (56.1 tCO2/TJ, net calorific basis).
  - Efficiency = 0.50: an assumption. No single official figure for the Spanish fleet was found; the EEA indicates that combined-cycle plants can reach about 60 %. A sensitivity analysis (0.45 to 0.60) is in notebook 02.
- **Clean spark spread** = electricity price - marginal cost. Positive: a gas plant makes money at that price.
- **Alignment.** The day-ahead order book closes at 12:00 CET/CEST on D-1 (SDAC), so gas and carbon prices of day D are taken from D-1, forward-filled over weekends and holidays and then shifted by one day. The daily close of D-1 is set after the auction closes, so this is an approximation; D-2 and same-day alignments give the same results.

## Limits

- Spain only so far; 2024 only.
- **Gas:** TTF front-month future, not the Spanish MIBGAS price. Yahoo's calendar has gaps on some US holidays; they are forward-filled.
- **Carbon:** continuous series of the nearest-December future. The provider changes contract before expiry (volume drops around 10 December 2024 and mid-December 2023), which can create small artificial jumps.
- Constant efficiency and emission factor; no start-up, ramping, variable O&M costs, or plant-level heterogeneity. The emission factor is on a net calorific basis while gas prices may be quoted on another basis; not quantified.
- Residual load ignores imports, exports and pumping.
- Daily averages hide intra-day structure; the hourly comparison uses one marginal cost per day.
- Correlations and slopes on realised values are associations, not causal estimates. Explanations for the spring price pattern (hydro, wind, demand) are hypotheses and have not been tested. About 940 hours at roughly 0 EUR/MWh and 300 hours at roughly 35 EUR/MWh form flat clusters whose cause has not been tested.
- Analysis only; no trading or forecasting results yet.

## Run

```bash
pip install -r requirements.txt
```

Create a `.env` file at the root of the repository (it is git-ignored, never commit it):

```
ENTSOE_API_KEY=your_token
```

Then:

```bash
python src/download_entsoe.py --countries ES --start 2024-01-01 --end 2024-12-31
jupyter notebook notebooks/01_exploration.ipynb
jupyter notebook notebooks/02_gas_carbon_spread.ipynb
```

## Repository

```
src/        data download
notebooks/  01_exploration, 02_gas_carbon_spread
figures/    exported figures
data/       raw/ and processed/ (not committed)
```

## Sources

- IPCC (2006), *Guidelines for National Greenhouse Gas Inventories*, vol. 2 Energy, ch. 2 Stationary Combustion, table 2.2.
- EPEX Spot, *SDAC Fallback Manual* (gate closure 12:00 CET/CEST).
- European Environment Agency, efficiency of electricity and heat production.
- ENTSO-E Transparency Platform; Yahoo Finance; Investing.com.
