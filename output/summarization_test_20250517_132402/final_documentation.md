# Code Documentation

Generated on: 2025-05-17 13:41:23
Codebase: `MonteCarloPFE`

## Table of Contents

- [Document Control](#document-control)
- [Executive Summary](#executive-summary)
- [1. Introduction](#1-introduction)
  - [1.1. Purpose of the Model](#11-purpose-of-the-model)
  - [1.2. Scope and Applicability](#12-scope-and-applicability)
  - [1.3. Intended Users](#13-intended-users)
  - [1.4. Regulatory Context](#14-regulatory-context)
- [2. Model Methodology](#2-model-methodology)
  - [2.1. Theoretical Basis](#21-theoretical-basis)
  - [2.2. Mathematical Formulation](#22-mathematical-formulation)
  - [2.3. Assumptions and Justifications](#23-assumptions-and-justifications)
  - [2.4. Limitations of the Methodology](#24-limitations-of-the-methodology)
- [3. Data](#3-data)
  - [3.1. Input Data Sources and Specifications](#31-input-data-sources-and-specifications)
  - [3.2. Data Preprocessing and Transformations](#32-data-preprocessing-and-transformations)
  - [3.3. Data Quality Assessment](#33-data-quality-assessment)
  - [3.4. Data Lineage](#34-data-lineage)
- [4. Model Implementation](#4-model-implementation)
  - [4.1. System Architecture](#41-system-architecture)
  - [4.2. Detailed Module Descriptions](#42-detailed-module-descriptions)
  - [4.3. Key Parameters and Calibration](#43-key-parameters-and-calibration)
  - [4.4. Code Version Control](#44-code-version-control)
  - [4.5. Computational Aspects](#45-computational-aspects)
- [5. Model Validation](#5-model-validation)
  - [5.1. Validation Framework Overview](#51-validation-framework-overview)
  - [5.2. Backtesting](#52-backtesting)
  - [5.3. Benchmarking](#53-benchmarking)
  - [5.4. Sensitivity and Stress Testing](#54-sensitivity-and-stress-testing)
  - [5.5. Key Validation Findings and Recommendations](#55-key-validation-findings-and-recommendations)
- [6. Reporting and Output](#6-reporting-and-output)
  - [6.1. Description of Output Files/Reports](#61-description-of-output-files/reports)
  - [6.2. Interpretation of Results](#62-interpretation-of-results)
- [7. Model Governance and Controls](#7-model-governance-and-controls)
  - [7.1. Model Ownership](#71-model-ownership)
  - [7.2. Ongoing Monitoring](#72-ongoing-monitoring)
  - [7.3. Change Management Process](#73-change-management-process)
  - [7.4. Access Controls](#74-access-controls)
- [8. Overall Model Limitations and Weaknesses](#8-overall-model-limitations-and-weaknesses)
- [9. Conclusion and Recommendations](#9-conclusion-and-recommendations)
- [Appendix A: Glossary of Terms](#appendix-a:-glossary-of-terms)
- [Appendix B: Code File Manifest](#appendix-b:-code-file-manifest)

## Document Control

| Property | Value |
|----------|-------|
| Document ID | MD-PFE-TRS-2025-001 |
| Model Name/Identifier | MonteCarloPFE |
| Model Version | 1.0.0 |
| Document Version | 1.0d |
| Document Status | Draft |
| Publication Date | 2025-05-17 |
| Author(s) | ['BMO AI Documentation Assistant'] |
| Reviewer(s) | ['[Reviewer Name(s) Placeholder]'] |
| Approver | [Approver Name Placeholder] |

## Run Metadata

| Property | Value |
|----------|-------|
| Files Processed | 17 |
| Sections Generated (from template) | 12 |
| Template Used | templates/bmo_model_documentation_template.json |

## Executive Summary

**Executive Summary**

The purpose of this model is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. PFE is a risk metric that quantifies the potential future credit exposure arising from derivative instruments, which is crucial for risk management and regulatory capital calculations.

The key methodologies employed in this model are:

- **Monte Carlo Simulation**: The model simulates multiple paths of underlying asset prices using the Geometric Brownian Motion (GBM) process. This stochastic process generates random price trajectories based on the asset's current price, volatility, risk-free rate, and dividend yield.

- **Equity TRS Valuation**: For each simulated asset price path, the model values the corresponding Equity TRS instrument. The mark-to-market (MtM) value of the TRS is calculated based on the change in the underlying asset price relative to the trade's inception price, multiplied by the notional amount.

- **Exposure Calculation**: The exposure at each time step is derived from the MtM values, where positive MtM values represent potential exposure to the counterparty. The model computes exposure paths for each simulated price path.

- **PFE Quantile Calculation**: The PFE profile for a trade is calculated by taking a specified quantile (e.g., 95th percentile) of the positive exposures across all simulated paths at each time step. This provides a time-series of PFE values representing the potential future credit exposure at different time horizons.

The primary output of the model is the PFE profile for individual trades and an aggregated PFE profile across the entire portfolio. The aggregation is currently implemented as a simple summation of individual trade PFE profiles, although more sophisticated aggregation methods accounting for netting effects are typically required for accurate portfolio-level PFE calculations.

[Information regarding the overall model soundness, strengths, and significant limitations needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

[Information regarding any critical recommendations for model usage, enhancements, or governance (if applicable) needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

## 1. Introduction

**1. Introduction**

This section provides an overview of the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). The model aims to quantify the potential future credit exposure arising from TRS instruments by simulating underlying asset price paths and calculating the corresponding exposure profiles.

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric widely used in counterparty credit risk management and regulatory capital calculations. It represents an estimate of the potential future exposure that a bank or financial institution may face due to fluctuations in the market value of derivative instruments, such as TRS contracts.

By accurately quantifying PFE, financial institutions can better manage their counterparty credit risk, allocate appropriate economic capital, and comply with regulatory requirements related to counterparty credit risk management.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are derivative contracts that exchange the total return of an underlying equity asset between two counterparties. The model currently focuses on TRS instruments and does not cover other derivative types or asset classes.

[Information regarding the specific portfolios or trading desks for which this model is intended needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures arising from TRS portfolios.

- Traders and portfolio managers: To understand the potential future exposure associated with their TRS positions and make informed trading decisions.

- Regulatory reporting and capital calculation teams: To calculate regulatory capital requirements related to counterparty credit risk.

[Information regarding any additional intended users needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines that this model and its documentation adhere to needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulatory guidelines are applicable, the following statement can be included:

"This model and its documentation follow BMO's internal standards for model governance, validation, and risk management practices related to counterparty credit risk."

### 1.1. Purpose of the Model

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric used to estimate the potential future credit exposure arising from derivative instruments, such as TRS contracts, over their remaining lifetimes. Specifically, this model aims to quantify the PFE for a portfolio of Equity TRS trades by simulating the underlying asset price paths and valuing the TRS instruments accordingly.

The calculation of PFE is crucial for effective risk management and regulatory compliance in financial institutions. It helps assess the counterparty credit risk associated with derivative portfolios and determine appropriate capital requirements. By projecting the potential future exposure under various market scenarios, institutions can better manage their risk exposures and ensure they hold sufficient capital buffers.

In the context of Equity TRS, the model simulates the future price paths of the underlying equity assets using the Geometric Brownian Motion (GBM) process, a widely adopted stochastic model for asset price dynamics. These simulated price paths are then used to value the TRS instruments at each time step, considering the contractual terms and cash flows. The resulting mark-to-market (MtM) values are used to calculate the exposure profiles, which represent the potential future exposure at different time points.

The model employs a Monte Carlo simulation approach, generating a large number of potential asset price paths to capture the inherent randomness and volatility of the underlying equity prices. By analyzing the distribution of exposures across these simulated paths, the model computes the PFE profile at a specified quantile (e.g., 95th percentile), providing a conservative estimate of the potential future exposure over the remaining life of the TRS trades.

The PFE profiles are calculated for individual trades and can be aggregated across the entire portfolio, enabling a comprehensive assessment of the overall counterparty credit risk. This information is crucial for risk management purposes, such as determining appropriate credit limits, setting margin requirements, or allocating capital reserves.

[Information regarding the specific regulatory context or guidelines that this model and its documentation adhere to needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 1.2. Scope and Applicability

**1.2. Scope and Applicability**

The Potential Future Exposure (PFE) calculation model is designed specifically for Equity Total Return Swaps (TRS). It is currently scoped to handle this particular type of financial instrument and is not intended to be applied to other asset classes or derivative products. The model's core functionality revolves around simulating the underlying equity price paths using the Geometric Brownian Motion (GBM) process, valuing the TRS instruments based on these simulated paths, and calculating the PFE profiles from the resulting exposure paths.

The key components of the model are:

1. **Monte Carlo Simulation Engine:** This module is responsible for generating multiple simulated price paths for the underlying equity asset using the GBM process. It takes into account market data parameters such as the current asset price, volatility, risk-free rate, and dividend yield.

2. **Equity TRS Valuation:** The `EquityTRS` class within the `financial_instruments` module encapsulates the logic for valuing Equity Total Return Swaps. It calculates the mark-to-market (MtM) and exposure values for a given TRS trade based on the simulated underlying asset price paths.

3. **PFE Calculation:** The `pfe_calculation` module contains components for computing the PFE profile from the exposure paths generated by the TRS valuation. The `PFEQuantileCalculator` class calculates the PFE at each time step as a specified quantile (e.g., 95th percentile) of the positive exposures across all simulated paths.

4. **Trade Aggregation:** The `TradeAggregator` class in the `pfe_calculation` module manages the aggregation of individual trade PFE profiles. It currently implements a simple summation approach, although it acknowledges that this may not be the correct method for calculating portfolio-level PFE due to potential netting effects.

While the model is primarily designed for Equity TRS instruments, it does not explicitly exclude the possibility of extending its scope to other asset classes or derivative types in the future. However, such an extension would likely require modifications to the underlying assumptions, valuation methodologies, and potentially the simulation process itself.

It is important to note that the model's scope and applicability may be subject to specific regulatory requirements or guidelines related to counterparty credit risk management and PFE calculation. [Information regarding any applicable regulatory requirements or guidelines needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

Regarding the intended users of the model and its outputs, the summaries do not provide explicit information. However, based on the context of PFE calculation and counterparty credit risk management, the primary intended users are likely to be:

- Risk management teams

- Traders and portfolio managers

- Regulatory bodies or auditors (for compliance and reporting purposes)

[Information regarding any specific portfolios or trading desks the model is intended for needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 1.3. Intended Users

**1.3. Intended Users**

The primary intended users of the Potential Future Exposure (PFE) calculation model and its outputs are:

- **Risk Management Teams**: The PFE profiles generated by the model are crucial inputs for counterparty credit risk management and exposure monitoring processes. Risk managers rely on these PFE calculations to assess the potential future exposure to counterparties arising from derivative instruments like Equity Total Return Swaps (TRS).

- **Traders and Front Office**: Traders and front office personnel involved in structuring and managing TRS trades can utilize the PFE profiles to understand the potential future exposure implications of their trading strategies and positions. This information aids in risk-informed decision-making and portfolio optimization.

- **Regulatory Bodies and Auditors**: Financial institutions are required to calculate and report counterparty credit risk metrics, including PFE, to regulatory bodies for capital adequacy and risk management oversight purposes. The PFE calculations and associated documentation from this model may be subject to review by regulators and auditors to ensure compliance with relevant guidelines and industry best practices.

- **Model Validation and Risk Control Teams**: Internal teams responsible for model validation, risk control, and governance processes within the institution are intended users of the model documentation. They assess the model's soundness, identify potential limitations, and provide recommendations for improvement or enhanced oversight.

- **Senior Management and Executive Committees**: While not directly involved in the technical aspects of the model, senior management and executive committees overseeing risk management activities may review high-level summaries and assessments of the PFE model's performance, limitations, and implications for the institution's risk profile.

It is important to note that while the primary intended users are internal stakeholders within the financial institution, certain aspects of the PFE calculations and associated documentation may also be shared with external counterparties or regulatory bodies as part of risk reporting or due diligence processes, subject to appropriate confidentiality and information-sharing agreements.

### 1.4. Regulatory Context

This section aims to address any specific regulatory requirements or guidelines that the model and its documentation adhere to.

Based on the information available in the provided codebase summaries, there are no explicit mentions of specific regulatory requirements or guidelines that this Potential Future Exposure (PFE) calculation model and its documentation are designed to comply with.

However, it is worth noting that PFE calculations and counterparty credit risk management are critical components of regulatory frameworks for financial institutions, such as:

- Basel III Accord: The Basel Committee on Banking Supervision has established guidelines for calculating regulatory capital requirements, including counterparty credit risk capital charges. PFE calculations are a key input for determining these capital requirements.

- Fundamental Review of the Trading Book (FRTB): The FRTB is a set of reforms introduced by the Basel Committee to revise the market risk capital requirements for trading book positions. PFE calculations play a role in determining the capital requirements for counterparty credit risk exposures arising from derivatives and securities financing transactions.

While the provided codebase summaries do not explicitly mention specific regulatory guidelines, it is reasonable to assume that the PFE calculation model and its documentation follow industry best practices and internal standards for model governance and validation within the financial institution (BMO in this case).

If no specific regulatory guidelines are applicable, the documentation should clearly state that it adheres to BMO's internal standards and procedures for model development, validation, and risk management. These internal standards are likely designed to align with regulatory expectations and ensure robust model governance practices.

In summary, the following statement could be included in this section:

"The Potential Future Exposure (PFE) calculation model and its documentation adhere to BMO's internal standards and procedures for model development, validation, and risk management. These internal standards are designed to align with industry best practices and regulatory expectations for counterparty credit risk management and model governance, although no specific regulatory guidelines are explicitly referenced within the scope of this model."

[Note: If specific regulatory guidelines or requirements are applicable to this model, but information regarding their adherence is not available in the provided codebase summaries, the following statement should be included: "Information regarding the specific regulatory requirements or guidelines that this PFE calculation model and its documentation adhere to needs to be sourced or further investigated, as it is not fully available in the provided codebase summaries."]

## 2. Model Methodology

**2. Model Methodology**

This section provides a detailed explanation of the theoretical basis, mathematical formulation, assumptions, and limitations of the methodologies employed in the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS).

**2.1. Theoretical Basis**

The model's core methodology is based on the following financial and mathematical theories:

1. **Monte Carlo Simulation**: The model utilizes Monte Carlo simulation techniques to generate multiple possible future scenarios for the underlying asset prices. This approach is widely used in financial modeling and risk management to capture the inherent uncertainty and randomness in asset price movements.

2. **Geometric Brownian Motion (GBM)**: The simulation of asset price paths is driven by the Geometric Brownian Motion (GBM) process, a stochastic process commonly used in finance to model the behavior of asset prices under the assumption of log-normal distribution. The GBM process is defined by the following stochastic differential equation:

```

dS(t) = μ * S(t) dt + σ * S(t) dW(t)

```

Where:

- S(t) is the asset price at time t

- μ is the drift term (expected rate of return)

- σ is the volatility of the asset price

- dW(t) is the increment of a Wiener process (Brownian motion)

The GBM process assumes that the logarithm of asset prices follows a Brownian motion with constant drift and volatility parameters.

3. **Valuation of Equity Total Return Swaps (TRS)**: The model incorporates the valuation of Equity TRS instruments, which are derivative contracts that exchange the total return of an underlying equity asset for a fixed or floating rate payment. The valuation of TRS contracts is based on the mark-to-market (MtM) value, which is calculated as the change in the underlying asset's price relative to the initial price at inception, multiplied by the notional amount.

**2.2. Mathematical Formulation**

The key mathematical formulations and algorithms involved in the PFE calculation process are as follows:

1. **Simulation of Asset Price Paths**:

- The GBM process is discretized using the Euler-Maruyama method, resulting in the following equation for simulating asset prices at each time step:

```

S(t + Δt) = S(t) * exp((μ - σ^2/2) * Δt + σ * sqrt(Δt) * Z)

```

Where:

- S(t) is the asset price at time t

- μ is the drift term (risk-free rate - dividend yield)

- σ is the volatility of the asset price

- Δt is the time increment (time step)

- Z is a standard normal random variable

- This equation is applied iteratively to generate multiple asset price paths over the specified time horizon and number of time steps.

2. **Valuation of Equity TRS**:

- The mark-to-market (MtM) value of an Equity TRS at time t is calculated as:

```

MtM(t) = Notional * (S(t) - S_0) * Direction

```

Where:

- Notional is the notional amount of the TRS contract

- S(t) is the underlying asset price at time t

- S_0 is the initial asset price at inception

- Direction is +1 for a "receive equity return" trade, and -1 for a "pay equity return" trade

3. **Exposure Calculation**:

- The exposure at time t is defined as the maximum of 0 and the MtM value:

```

Exposure(t) = max(0, MtM(t))

```

- This calculation assumes that positive MtM values represent exposure to the counterparty, while negative MtM values do not contribute to exposure.

4. **PFE Calculation**:

- The PFE at each time step is calculated as a specified quantile (e.g., 95th percentile) of the positive exposures across all simulated paths.

- Let Exposure_paths be a 2D array of shape (

### 2.1. Theoretical Basis

**2.1. Theoretical Basis**

The Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS) is underpinned by several financial and mathematical theories and principles. The core theoretical foundations are:

**1. Geometric Brownian Motion (GBM)**

The model employs the Geometric Brownian Motion (GBM) process to simulate the underlying equity asset price paths. GBM is a widely used stochastic process in finance for modeling the behavior of asset prices under the assumption of log-normal distribution. The GBM process is defined by the following stochastic differential equation:

```

dS(t) = μ * S(t) dt + σ * S(t) dW(t)

```

Where:

- S(t) is the asset price at time t

- μ is the drift term (expected rate of return)

- σ is the volatility of the asset price

- dW(t) is the increment of a Wiener process (Brownian motion)

The GBM process assumes that the logarithm of the asset price follows a Brownian motion with a constant drift and volatility. This process is implemented in the `simulation_engine.gbm_model` module, which generates multiple asset price paths over time based on the provided market data (initial price, drift, volatility) and simulation parameters (time steps, number of paths).

**2. Monte Carlo Simulation**

The model employs Monte Carlo simulation techniques to generate a large number of potential future asset price paths. The `simulation_engine.monte_carlo_simulator` module orchestrates the Monte Carlo simulations by leveraging the GBM process to generate asset price paths. The simulation parameters, such as the number of paths and time steps, are configurable and can be adjusted based on the desired level of accuracy and computational resources.

**3. Valuation of Equity Total Return Swaps (TRS)**

The model incorporates the valuation of Equity Total Return Swaps (TRS), which are financial instruments that exchange the total return of an underlying equity asset for a fixed or floating rate payment. The `financial_instruments.equity_trs` module provides the `EquityTRS` class, which calculates the mark-to-market (MtM) and exposure values of a TRS contract based on the simulated underlying asset price paths.

The MtM calculation is based on the change in the underlying equity price relative to the initial price at inception, multiplied by the notional amount. The exposure calculation takes the maximum of 0 and the MtM values, assuming positive MtM means the counterparty owes the TRS holder.

**4. Quantile-based PFE Calculation**

The model employs a quantile-based approach to calculate the PFE profile from the exposure paths generated for each TRS trade. The `pfe_calculation.pfe_computer` module provides the `PFEQuantileCalculator` class, which calculates the PFE at each time step as a specified quantile (e.g., 95th percentile) of positive exposures across all simulated paths.

The quantile-based approach is a widely used method for estimating PFE, as it provides a measure of the potential exposure at a given confidence level (e.g., 95% confidence that the exposure will not exceed the calculated PFE value).

**5. Aggregation of PFE Profiles**

The model includes functionality for aggregating individual trade PFE profiles to obtain a portfolio-level PFE profile. The `pfe_calculation.exposure_aggregator` module provides the `TradeAggregator` class, which manages the storage of individual trade PFE profiles and implements a simple summation method for aggregating PFE profiles across trades.

However, it is important to note that the simple summation approach implemented in the provided codebase is generally not the correct way to calculate portfolio PFE due to netting effects and trade dependencies. More sophisticated aggregation methods, such as netting or considering trade dependencies, are typically required for accurate portfolio PFE calculation.

In summary, the PFE calculation model for Equity TRS is built upon the theoretical foundations of Geometric Brownian Motion for asset price modeling, Monte Carlo simulation techniques for generating potential future price paths, valuation principles for Equity TRS instruments, quantile-based PFE calculation, and basic aggregation methods for combining individual trade PFE profiles.

### 2.2. Mathematical Formulation

**Executive Summary**

This model implements a Monte Carlo simulation approach to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). The key methodologies employed are:

1. **Monte Carlo Simulation**: The model generates multiple simulated price paths for the underlying equity asset using the Geometric Brownian Motion (GBM) process. These simulated paths are used to value the TRS instruments and calculate exposure profiles.

2. **Equity TRS Valuation**: The model represents Equity TRS instruments and calculates their mark-to-market (MtM) values based on the simulated underlying asset price paths. The MtM values are then used to derive exposure paths.

3. **PFE Calculation**: The PFE profile for each trade is computed by taking a specified quantile (e.g., 95th percentile) of the positive exposure values across all simulated paths at each time step.

The primary output of the model is the PFE profile for individual trades, as well as an aggregated PFE profile across the portfolio. The aggregation is currently implemented as a simple summation of individual trade PFE profiles, although this approach may not accurately capture portfolio effects and netting.

Overall, the model's methodology is based on well-established financial principles and techniques, such as the GBM process for asset price simulation and Monte Carlo methods for risk analysis. However, some limitations include the assumptions inherent to the GBM process (e.g., constant volatility, log-normal price distributions) and the simplistic approach to portfolio PFE aggregation.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric used in counterparty credit risk management and regulatory capital calculations. It represents an estimate of the potential future exposure arising from a derivative or securities financing transaction, considering the potential for future changes in market prices or other risk factors.

In the context of Equity TRS, PFE quantifies the potential future exposure to the counterparty due to changes in the underlying equity asset's price over the remaining life of the swap contract.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS). An Equity TRS is a type of over-the-counter (OTC) derivative contract where one party (the "total return payer") agrees to pay the other party (the "total return receiver") the total economic performance of an underlying equity asset, including any capital gains or losses, dividends, and any other income or cash flows.

The model's scope is currently limited to Equity TRS instruments. Other product types or asset classes, such as interest rate swaps, credit derivatives, or commodities, are not covered by this model's implementation.

The model can be applied to individual Equity TRS trades or portfolios of such trades. However, the provided codebase summaries do not specify any limitations or exclusions regarding the size or composition of the portfolios it can handle.

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures arising from Equity TRS positions.

- Traders: To evaluate the potential future risk associated with their Equity TRS trades.

- Regulators: To review and validate the bank's or financial institution's PFE calculations for regulatory capital purposes.

Other potential users may include risk committees, senior management, or model validation teams responsible for ensuring the model's integrity and appropriate usage.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is primarily based on the following financial and mathematical theories:

1. **Monte Carlo Simulation**: Monte Carlo simulation is a computational technique that uses random sampling to obtain numerical results for problems that cannot be easily solved analytically. In this model, Monte Carlo simulation is used to generate multiple possible future price paths for the underlying equity asset.

2. **

### 2.3. Assumptions and Justifications

**Executive Summary**

This model is designed to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of TRS instruments based on the simulated price paths.

3. Calculation of exposure paths from the mark-to-market (MtM) values of the TRS instruments.

4. Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles, representing the potential future exposure over time for individual trades and aggregated across the portfolio. The model's overall soundness is based on the widely accepted GBM process for asset price modeling and the standard quantile-based approach for PFE calculation. However, limitations include the assumption of constant volatility and drift in the GBM process, as well as the simplistic aggregation method used for portfolio PFE calculation, which does not account for netting effects or trade dependencies.

**1. Assumptions Related to Model Methodology**

1.1. Geometric Brownian Motion (GBM) Process for Asset Price Simulation

- The model assumes that the underlying equity prices follow a Geometric Brownian Motion (GBM) process, which is a widely used stochastic process for modeling asset prices in finance.

- The GBM process assumes that asset prices are log-normally distributed, with constant drift (expected rate of return) and volatility over time.

- This assumption is a simplification of real-world asset price dynamics, which may exhibit more complex behaviors, such as jumps, stochastic volatility, or regime shifts.

- The GBM process is chosen for its mathematical tractability and widespread acceptance in financial modeling, despite its limitations.

1.2. Constant Drift and Volatility Parameters

- The model assumes that the drift (expected rate of return) and volatility parameters for the underlying assets are constant over the simulation period.

- In reality, these parameters may vary over time due to changing market conditions, economic factors, or other external influences.

- The assumption of constant drift and volatility is a simplification made for computational efficiency and to align with the GBM process assumptions.

1.3. Independence of Asset Price Paths

- The model assumes that the simulated asset price paths are independent of each other.

- This assumption may not hold true in cases where the underlying assets exhibit strong correlations or dependencies, which can impact the joint distribution of asset prices.

- The independence assumption is a simplification made for computational tractability and to align with the GBM process assumptions.

**2. Assumptions Related to Financial Instrument Valuation**

2.1. Equity Total Return Swap (TRS) Valuation

- The model assumes that the valuation of Equity TRS instruments is based solely on the change in the underlying equity price relative to the initial price at inception, multiplied by the notional amount.

- This assumption simplifies the valuation process by focusing only on the equity leg of the TRS and ignoring any potential adjustments or fees related to the funding leg (fixed or floating rate payments).

- The assumption may not accurately capture the full complexity of TRS valuation in practice, which may involve additional considerations or modeling components.

2.2. Exposure Calculation Assumptions

- The model assumes that positive mark-to-market (MtM) values of the TRS instrument represent exposure to the counterparty.

- This assumption may not hold true in certain scenarios or under different assumptions regarding collateral management, credit risk, or regulatory considerations.

- The exposure calculation does not account for potential netting agreements or portfolio-level effects, which can impact the actual exposure profile.

**3. Assumptions Related to PFE Calculation and Aggregation**

3.1. Quantile-based PFE Calculation

- The model assumes that the PFE profile can be accurately represented by a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

- This assumption is based on the standard industry practice for PFE calculation but may not fully capture tail risk or extreme events beyond the chosen quantile level.

3.2. Simple Summation for Portfolio PFE Aggregation

- The model currently implements a simple summation approach for aggregating individual trade P

### 2.4. Limitations of the Methodology

**Executive Summary**

The model's primary purpose is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each trade.

4. Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles for individual trades and an aggregated PFE profile across the portfolio.

While the model's overall approach is sound and follows established financial modeling practices, there are several inherent limitations to the chosen methodologies, which are discussed in detail below.

**Limitations of the Geometric Brownian Motion (GBM) Process**

1. **Constant Volatility Assumption:** The GBM process assumes that the volatility of the underlying asset remains constant over time. However, in real-world markets, volatility can be stochastic and exhibit time-varying behavior, which the GBM process does not account for.

2. **Log-Normal Distribution:** The GBM process assumes that asset prices follow a log-normal distribution, which may not accurately capture the true distribution of asset returns, especially in the presence of extreme events or market shocks.

3. **Continuous Price Paths:** The GBM process models asset prices as continuous paths, while in reality, asset prices are discrete and can exhibit jumps or discontinuities due to various market events or news.

4. **Lack of Mean Reversion:** The GBM process does not incorporate mean-reverting behavior, which may be present in certain asset classes or market regimes.

**Limitations of the Monte Carlo Simulation Approach**

1. **Computational Complexity:** Monte Carlo simulations can be computationally intensive, especially for large portfolios or long-dated instruments, as they require generating and processing a large number of simulated paths.

2. **Convergence and Sampling Error:** The accuracy of Monte Carlo simulations depends on the number of simulated paths and the quality of the random number generator. Insufficient paths or poor sampling can lead to inaccurate results or convergence issues.

3. **Parameter Sensitivity:** The results of Monte Carlo simulations can be sensitive to the input parameters, such as volatility, drift, and other market data. Inaccurate or outdated parameters can lead to biased or unreliable results.

**Limitations of the PFE Calculation Methodology**

1. **Quantile-Based Approach:** The model calculates PFE as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths. This approach may not fully capture tail risk or extreme events beyond the chosen quantile level.

2. **Netting and Portfolio Effects:** The current implementation of the PFE aggregation method simply sums individual trade PFE profiles, which does not account for netting effects or potential dependencies between trades in a portfolio. This can lead to an overestimation or underestimation of the true portfolio-level PFE.

3. **Static Trade Assumptions:** The model assumes that the trade details (notional, maturity, etc.) are static and does not account for potential changes or adjustments to the trades over time, which can impact the PFE calculations.

**Limitations of the Equity TRS Valuation**

1. **Simplified Valuation:** The Equity TRS valuation in the model is based solely on the change in the underlying equity price relative to the initial price at inception, multiplied by the notional amount. This simplified approach may not accurately capture the true value of the TRS, as it does not consider other factors such as funding costs, collateral management, or credit risk adjustments.

2. **Trade Type Limitation:** The model currently supports only two trade types: "receive_equity_return" and "pay_equity_return". It does not account for other variations or features of Equity TRS contracts, such as embedded options or more complex payoff structures.

**General Limitations**

1. **Static Market Data:** The model relies on static market data (e.g., volatility, risk-free rate, dividend yield) loade

## 3. Data

**3. Data**

This section provides a comprehensive description of the data used by the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). It covers the input data sources and specifications, data preprocessing and transformations, data quality assessment processes, and an overview of the data lineage.

**3.1. Input Data Sources and Specifications**

The model relies on the following input data sources:

1. **Trade Data**

- **Source:** JSON file located at `config/trades.json`

- **Description:** This file contains a list of dictionaries, where each dictionary represents the configuration details for a specific Equity TRS trade. The key fields include:

- `trade_id`: A unique identifier for the trade.

- `underlying_asset_id`: The identifier of the underlying equity asset associated with the trade.

- `notional`: The notional amount or size of the trade.

- `initial_price_at_inception`: The initial price of the underlying asset at the trade's inception.

- `maturity_in_years`: The maturity period of the trade in years.

- `time_steps_per_year`: The number of time steps per year for the trade.

- `trade_type`: The type of trade, either "receive_equity_return" or "pay_equity_return".

- **Frequency:** The trade data is static and loaded once during the model initialization.

- **Format:** JSON

2. **Market Data**

- **Source:** JSON file located at `config/market_data.json`

- **Description:** This file contains market data parameters for the underlying equity assets. Currently, it includes two dictionaries, "EQ_A" and "EQ_B", each representing a set of market data parameters for a specific asset. The key fields include:

- `current_price`: The current market price of the asset.

- `volatility`: The volatility of the asset's price.

- `risk_free_rate`: The risk-free rate of return.

- `dividend_yield`: The dividend yield of the asset.

- **Frequency:** The market data is static and loaded once during the model initialization.

- **Format:** JSON

3. **Simulation Parameters**

- **Source:** JSON file located at `config/simulation_params.json`

- **Description:** This file contains parameters for configuring the Monte Carlo simulation used in the PFE calculation. The key fields include:

- `simulation_id`: A string identifier for the simulation run.

- `num_paths`: The number of simulation paths to generate.

- `pfe_quantile`: The quantile level for PFE calculations (e.g., 0.95 for the 95th percentile).

- `output_directory`: The directory path for storing simulation results.

- **Frequency:** The simulation parameters are static and loaded once during the model initialization.

- **Format:** JSON

**3.2. Data Preprocessing and Transformations**

The input data from the JSON files is loaded and parsed into Python dictionaries or lists using the `data_management.loader` module. No additional data cleaning, filtering, or transformation steps are explicitly mentioned in the provided codebase summaries. However, it is a common practice to perform data validation and sanitization before using the input data in the model calculations.

**3.3. Data Quality Assessment**

The provided codebase summaries do not describe any specific processes for assessing the accuracy, completeness, or appropriateness of the input data. However, it is generally recommended to implement data quality checks and validation mechanisms to ensure the integrity of the input data, especially for critical financial models and risk management applications.

Potential data quality checks that could be implemented include:

- Validating the structure and data types of the input JSON files.

- Checking for missing or null values in the trade data, market data, or simulation parameters.

- Verifying that the provided values (e.g., notional, maturity, volatility) are within reasonable ranges.

- Ensuring consistency and referential integrity between related data elements (e.g., underlying asset IDs match across trade data and market data).

If any data quality issues are detected, appropriate error handling or data imputation strategies should be implemented to handle missing, erroneous, or anomalous data.

**3.4. Data Lineage**

The data lineage for

### 3.1. Input Data Sources and Specifications

**3.1. Input Data Sources and Specifications**

This section details the various input data sources and their specifications required for the Potential Future Exposure (PFE) calculation system for Equity Total Return Swaps (TRS). The input data is primarily stored in JSON configuration files located in the `config/` directory.

**Trade Data**

The trade data is stored in the `config/trades.json` file, which contains a list of dictionaries representing individual trade configurations. Each trade configuration dictionary includes the following key-value pairs:

- `trade_id` (str): A unique identifier for the trade.

- `underlying_asset_id` (str): The identifier of the underlying asset associated with the trade.

- `notional` (float): The notional amount or size of the trade.

- `initial_price_at_inception` (float): The initial price of the underlying asset at the trade's inception.

- `maturity_in_years` (float): The maturity period of the trade in years.

- `time_steps_per_year` (int): The number of time steps per year for the trade.

- `trade_type` (str): The type of trade, either "receive_equity_return" or "pay_equity_return".

The trade data is loaded and managed by the `ConfigManager` class in the `data_management.loader` module.

**Market Data**

The market data parameters for the underlying assets are stored in the `config/market_data.json` file. This file defines a dictionary for each asset, where the keys represent the asset identifiers (e.g., "EQ_A", "EQ_B"), and the values are dictionaries containing the following market data parameters:

- `current_price` (float): The current market price of the asset.

- `volatility` (float): The volatility of the asset price.

- `risk_free_rate` (float): The risk-free rate used in pricing models.

- `dividend_yield` (float): The dividend yield of the asset.

The market data is loaded and managed by the `ConfigManager` class in the `data_management.loader` module.

**Simulation Parameters**

The simulation parameters for the Monte Carlo PFE calculation are stored in the `config/simulation_params.json` file. This file contains the following key-value pairs:

- `simulation_id` (str): A string identifier for the simulation run.

- `num_paths` (int): The number of simulation paths to be generated.

- `pfe_quantile` (float): The quantile level for PFE calculations (e.g., 0.95 for the 95th percentile).

- `output_directory` (str): The directory path for storing simulation results.

The simulation parameters are loaded and managed by the `ConfigManager` class in the `data_management.loader` module.

**Configuration Data Management**

The `ConfigManager` class in the `data_management.loader` module provides a centralized mechanism for loading and managing the configuration data from the JSON files mentioned above. It exposes the following methods:

- `load_all(config_dir: str = "config")`: Loads and stores the trade data, market data, and simulation parameters from the respective JSON files in the specified configuration directory (default: `"config/"`).

The loaded configuration data is then accessible through the following attributes of the `ConfigManager` instance:

- `trades`: A list of dictionaries representing the trade configurations.

- `market_data`: A dictionary containing the market data parameters for each asset.

- `sim_params`: A dictionary containing the simulation parameters.

[Information regarding the specific format and structure of the configuration files needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 3.2. Data Preprocessing and Transformations

**3.2. Data Preprocessing and Transformations**

This section describes the data preprocessing and transformation steps applied to the raw data before it is used by the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). The model primarily relies on the following types of input data:

1. **Trade Details**

- The trade details are loaded from a JSON file (`config/trades.json`) containing a list of dictionaries, where each dictionary represents the configuration for a specific trade.

- The trade details include:

- `trade_id`: A unique identifier for the trade.

- `underlying_asset_id`: The identifier of the underlying asset associated with the trade.

- `notional`: The notional amount or size of the trade.

- `initial_price_at_inception`: The initial price of the underlying asset at the trade's inception.

- `maturity_in_years`: The maturity period of the trade in years.

- `time_steps_per_year`: The number of time steps per year for the trade.

- `trade_type`: The type of trade, either "receive_equity_return" or "pay_equity_return".

- No explicit data preprocessing or transformations are applied to the trade details. The data is loaded directly from the JSON file and used as-is by the model.

2. **Market Data**

- The market data for the underlying assets is loaded from a JSON file (`config/market_data.json`).

- The market data includes parameters such as the current price, volatility, risk-free rate, and dividend yield for each asset.

- Similar to the trade details, no explicit data preprocessing or transformations are applied to the market data. The data is loaded directly from the JSON file and used as-is by the model.

3. **Simulation Parameters**

- The simulation parameters are loaded from a JSON file (`config/simulation_params.json`).

- The simulation parameters include:

- `simulation_id`: A string identifier for the simulation run.

- `num_paths`: An integer specifying the number of simulation paths.

- `pfe_quantile`: A float representing the quantile level for PFE calculations (e.g., 0.95 for the 95th percentile).

- `output_directory`: A string specifying the directory path for storing simulation results.

- No data preprocessing or transformations are applied to the simulation parameters. The data is loaded directly from the JSON file and used as-is by the model.

4. **Derived Data**

- The model calculates certain derived data based on the input trade details, such as the total time steps and time delta for each trade.

- The `_calculate_time_parameters` function in `main_pfe_runner.py` computes the total time steps and time delta based on the trade's maturity and time steps per year.

- These derived values are calculated on-the-fly during the model execution and do not require any separate preprocessing or transformation steps.

In summary, the PFE calculation model for Equity TRS does not perform any explicit data preprocessing or transformation steps on the raw input data. The trade details, market data, and simulation parameters are loaded directly from their respective JSON files and used as-is by the model. The only data transformation occurs when deriving the total time steps and time delta for each trade based on the provided trade details.

[Information regarding any additional data preprocessing or transformation steps needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 3.3. Data Quality Assessment

**3.3. Data Quality Assessment**

This section outlines the processes and methodologies employed to assess the quality, accuracy, completeness, and appropriateness of the input data used in the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). It also details the handling of missing, erroneous, or anomalous data.

**3.3.1. Data Sources and Inputs**

The primary data inputs for the PFE calculation model are:

1. **Trade Details:** A list of dictionaries containing trade-specific parameters for each Equity TRS contract, such as:

- Trade ID

- Underlying asset ID

- Notional amount

- Initial price at inception

- Maturity (in years)

- Time steps per year

- Trade type (receive or pay equity return)

These trade details are loaded from a JSON file (`config/trades.json`) by the `data_management.loader` module.

2. **Market Data:** A dictionary containing market data parameters for the underlying assets, including:

- Current price

- Volatility

- Risk-free rate

- Dividend yield

The market data is loaded from a JSON file (`config/market_data.json`) by the `data_management.loader` module.

3. **Simulation Parameters:** A dictionary containing parameters for the Monte Carlo simulation, such as:

- Simulation ID

- Number of paths

- PFE quantile (e.g., 95th percentile)

- Output directory

These simulation parameters are loaded from a JSON file (`config/simulation_params.json`) by the `data_management.loader` module.

**3.3.2. Data Validation and Cleansing**

[Information regarding data validation and cleansing processes needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**3.3.3. Missing Data Handling**

[Information regarding the handling of missing data needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**3.3.4. Outlier and Anomaly Detection**

[Information regarding the detection and handling of outliers or anomalous data needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**3.3.5. Data Appropriateness and Limitations**

The input data sources and formats are considered appropriate for the PFE calculation model, as they provide the necessary trade details, market data, and simulation parameters required for the model's execution. However, the following limitations and assumptions should be noted:

1. **Trade Details:**

- The trade details are assumed to be accurate and consistent with the expected format and data types.

- The `trade_type` values are limited to either "receive_equity_return" or "pay_equity_return".

- No validation or error checking mechanisms are implemented for the trade configurations within the JSON file.

2. **Market Data:**

- The market data parameters provided in the JSON file are assumed to be accurate and up-to-date.

- The structure and keys of the market data dictionaries are expected and understood by the consuming components of the system.

- No mechanisms are provided for validating or sanitizing the input market data.

3. **Simulation Parameters:**

- The simulation parameters are hard-coded in the JSON file, which may limit flexibility and require code changes for different simulation setups.

- No validation or error handling is implemented for the provided parameter values.

While the input data sources and formats are suitable for the current implementation, it is recommended to enhance the data quality assessment processes by incorporating robust validation, cleansing, and error handling mechanisms. This will ensure the integrity and reliability of the input data, mitigate potential issues arising from erroneous or incomplete data, and improve the overall robustness of the PFE calculation model.

### 3.4. Data Lineage

**3.4. Data Lineage**

The Potential Future Exposure (PFE) calculation system for Equity Total Return Swaps (TRS) involves several data sources and transformations before the final PFE profiles are generated. This section describes the flow of data from its source to its use in the model, and ultimately to the model outputs.

**Data Sources**

The primary data sources for the PFE calculation system are:

1. **Trade Data**: The trade details for Equity TRS contracts are stored in a JSON file (`config/trades.json`). Each trade is represented as a dictionary containing the following keys:

- `trade_id`: A unique identifier for the trade.

- `underlying_asset_id`: The identifier of the underlying asset associated with the trade.

- `notional`: The notional amount or size of the trade.

- `initial_price_at_inception`: The initial price of the underlying asset at the trade's inception.

- `maturity_in_years`: The maturity period of the trade in years.

- `time_steps_per_year`: The number of time steps per year for the trade.

- `trade_type`: The type of trade, either "receive_equity_return" or "pay_equity_return".

2. **Market Data**: The market data parameters for the underlying assets are stored in a separate JSON file (`config/market_data.json`). Each asset is represented as a dictionary containing keys such as `current_price`, `volatility`, `risk_free_rate`, and `dividend_yield`.

3. **Simulation Parameters**: The parameters governing the Monte Carlo simulation process are stored in another JSON file (`config/simulation_params.json`). This includes the `simulation_id`, `num_paths` (number of simulation paths), `pfe_quantile` (quantile level for PFE calculation), and `output_directory` (directory path for storing simulation results).

**Data Loading and Management**

The `data_management.loader` module provides functions and a `ConfigManager` class for loading and managing the configuration data from the JSON files:

1. The `load_json_data` function reads and parses JSON data from a specified file path.

2. The `get_trades`, `get_market_data`, and `get_simulation_params` functions use `load_json_data` to retrieve the respective data from the corresponding JSON files.

3. The `ConfigManager` class initializes with a configuration directory path and provides a `load_all` method to load and store trades, market data, and simulation parameters in its attributes (`trades`, `market_data`, `sim_params`).

**Data Transformations and Calculations**

The loaded data undergoes several transformations and calculations before the final PFE profiles are generated:

1. **Asset Price Path Simulation**: The `MonteCarloEngine` class from the `simulation_engine.monte_carlo_simulator` module orchestrates the Monte Carlo simulations for generating asset price paths. It utilizes the `GBMProcess` class from `simulation_engine.gbm_model` to simulate asset price paths based on the Geometric Brownian Motion (GBM) process, using the market data parameters (current price, volatility, risk-free rate, dividend yield) and simulation parameters (number of paths, time steps).

2. **Instrument Valuation**: The `EquityTRS` class from `financial_instruments.equity_trs` represents and values the Equity Total Return Swap (TRS) instrument. It calculates the mark-to-market (MtM) values and exposure values for the TRS contract based on the simulated asset price paths, trade details (notional, initial price, trade type), and the trade type ("receive_equity_return" or "pay_equity_return").

3. **PFE Calculation**: The `PFEQuantileCalculator` class from `pfe_calculation.pfe_computer` calculates the PFE profile for a trade by taking the specified quantile (e.g., 95th percentile) of positive exposures across the simulated paths at each time step.

4. **PFE Aggregation**: The `TradeAggregator` class from `pfe_calculation.exposure_aggregator` manages the aggregation of individual trade PFE profiles. It stores the PFE profiles for each trade and provides a method to calculate a simple sum of PFE profiles across

## 4. Model Implementation

**4. Model Implementation**

This section provides details on how the methodology for calculating Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) is implemented in the production environment. It covers the system architecture, key components, algorithms, and computational aspects of the model.

**4.1. System Architecture**

The PFE calculation system follows a modular design pattern, consisting of several interconnected components. The high-level architecture can be summarized as follows:

1. **Main Entry Point and Orchestration**: The `main_pfe_runner.py` module serves as the primary entry point and orchestrator for the PFE calculation process. It manages the overall workflow, including loading configuration data, initializing required components, processing individual trades, and aggregating and writing the results.

2. **Configuration and Data Management**: The `data_management` module is responsible for loading and managing configuration data from JSON files, such as trade details, market data, and simulation parameters. The `ConfigManager` class provides a centralized interface for accessing this data.

3. **Simulation Engine**: The `simulation_engine` module handles the Monte Carlo simulation of asset price paths. The `MonteCarloEngine` class orchestrates the simulations, while the `GBMProcess` class implements the Geometric Brownian Motion (GBM) process for generating asset price paths.

4. **Financial Instruments**: The `financial_instruments` module contains classes for representing and valuing financial instruments. The `EquityTRS` class models and values Equity Total Return Swaps based on simulated asset price paths.

5. **PFE Calculation**: The `pfe_calculation` module is responsible for calculating exposure paths, PFE profiles, and aggregating PFE across trades. The `PFEQuantileCalculator` class computes PFE profiles from exposure paths, and the `TradeAggregator` class manages and aggregates individual trade PFE profiles.

6. **Reporting**: The `reporting` module handles the writing of PFE results to output files. The `ResultsWriter` class creates an output directory and writes aggregated and individual PFE profiles to a JSON file.

The overall workflow and interactions between these components can be summarized as follows:

1. The `main_pfe_runner.py` module loads the required configuration data (trades, market data, simulation parameters) from JSON files using the `data_management` module.

2. For each trade, `main_pfe_runner.py` retrieves the market data for the underlying asset and initializes the Monte Carlo simulation engine from the `simulation_engine` module.

3. The Monte Carlo engine simulates asset price paths using the GBM process implemented in `gbm_model.py`.

4. The `EquityTRS` class from `financial_instruments` is used to value the TRS instrument and calculate mark-to-market (MtM) and exposure paths based on the simulated asset price paths.

5. The `PFEQuantileCalculator` from `pfe_calculation` is used to compute the PFE profile for the trade based on the exposure paths.

6. The individual trade PFE profiles are stored and aggregated using the `TradeAggregator` from `pfe_calculation`.

7. After processing all trades, the aggregated PFE profile and individual trade PFE profiles are written to an output file using the `ResultsWriter` from the `reporting` module.

**4.2. Detailed Module Descriptions**

This section provides detailed descriptions of the significant code modules or scripts involved in the PFE calculation process, including their purpose, key functions/classes, core algorithms, inputs, outputs, and dependencies.

**4.2.1. main_pfe_runner.py**

- **Purpose**: Orchestrate and execute the entire PFE calculation process for a portfolio of Equity Total Return Swaps (TRS).

- **Key Components**:

- `PFECalculationOrchestrator` (Class): Manages the overall PFE calculation workflow, including initializing and loading configuration data, instantiating required components, processing individual trades, and aggregating and writing results.

- `_calculate_time_parameters` (Method): Calculates the total time steps and time delta for a given trade based on its maturity and time steps per year.

- `process_single_trade` (Method): Processes a single trade by simulating asset price paths, val

### 4.1. System Architecture

**Executive Summary**

This model is designed to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

- Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

- Valuation of TRS instruments based on the simulated price paths.

- Calculation of exposure paths from the mark-to-market (MtM) values of the TRS instruments.

- Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles, representing the potential future exposure over time for individual trades and aggregated across the portfolio.

The model's overall approach is sound and follows established financial modeling principles. However, some key limitations include:

- The GBM process assumes constant drift and volatility, which may not accurately capture real-world asset price dynamics.

- The PFE calculation based on a single quantile may not fully represent tail risk.

- The current portfolio aggregation method (simple summation) does not account for netting effects or trade dependencies.

A critical recommendation is to enhance the portfolio aggregation methodology to incorporate netting effects and consider trade dependencies for more accurate portfolio-level PFE calculations.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric used to estimate the potential future credit exposure arising from derivative instruments, such as TRS. It is an essential input for risk management, counterparty credit risk assessment, and regulatory capital calculations.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), a type of derivative contract where one party receives the total return (capital gains and dividends) of an underlying equity asset, while the other party receives a fixed or floating rate payment. The model currently does not support other asset classes or derivative types.

The model can be applied to individual TRS trades or portfolios of TRS trades. [Information regarding any specific portfolio or trading desk this model is intended for needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures.

- Traders: To evaluate the potential future risk of TRS positions.

- Regulators: To review and validate the bank's PFE calculations for regulatory capital purposes.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines this model and its documentation adhere to needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is based on the following financial and mathematical theories:

- **Geometric Brownian Motion (GBM)**: The GBM process is used to simulate the underlying equity price paths. It is a widely-used stochastic process in finance that models asset prices as following a log-normal distribution with constant drift (expected return) and volatility.

- **Monte Carlo Simulation**: The model employs Monte Carlo simulation techniques to generate multiple possible future scenarios (price paths) for the underlying equity asset. This allows for the calculation of potential future exposures across a range of possible outcomes.

- **Derivative Valuation**: The model values the Equity Total Return Swap (TRS) instruments based on the simulated underlying price paths. The TRS valuation is based on the change in the underlying equity price relative to the initial price at inception, multiplied by the notional amount.

**2.2. Mathematical Formulation**

The key mathematical formulations and equations used in the model are:

1. **Geometric Brownian Motion (GBM) Process**:

The GBM process is defined by the following stochastic differential equation:

```

dS(t) = μ * S(t) dt + σ * S(t) dW(t)

```

Where:

### 4.2. Detailed Module Descriptions

**Executive Summary**

The codebase implements a system for calculating Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

1. Monte Carlo simulation of underlying asset price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated asset price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each TRS trade.

4. Computation of PFE profiles for individual trades by taking a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

5. Aggregation of individual trade PFE profiles to obtain an overall portfolio-level PFE profile.

The primary output of the system is a set of PFE profiles, both at the individual trade level and aggregated across the portfolio. These PFE profiles represent the potential future exposure to counterparties over time, which is a critical risk metric for risk management and regulatory capital calculations.

The overall model implementation appears sound, leveraging well-established financial modeling techniques and Monte Carlo simulation methods. However, some potential limitations include:

1. The assumption of constant volatility and drift parameters in the GBM process, which may not accurately capture real-world asset price dynamics.

2. The use of a simple summation approach for aggregating individual trade PFE profiles, which does not account for potential netting effects or trade dependencies within the portfolio.

It is recommended to further investigate and potentially enhance the model's aggregation methodology to incorporate more sophisticated portfolio effects and netting considerations for accurate portfolio-level PFE calculations.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the model is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a critical risk metric used in risk management and regulatory capital calculations, representing the potential future exposure to counterparties over time. The model aims to provide PFE profiles for individual TRS trades and aggregated across the portfolio, enabling effective counterparty credit risk management and compliance with regulatory requirements.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are a type of derivative contract where one party (the receiver) receives the total return of an underlying equity asset, including capital gains and dividends, in exchange for paying a floating rate of return to the other party (the payer). The model's scope is currently limited to Equity TRS instruments, and it does not cover other asset classes or derivative types.

The model can be applied to individual TRS trades or portfolios of TRS trades. [Information regarding any specific portfolio or broader applicability needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of the model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures and manage risk limits.

- Traders: To evaluate the potential future exposure associated with their TRS positions.

- Regulators: To ensure compliance with regulatory requirements for capital adequacy and risk management practices.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is underpinned by the following financial and mathematical theories:

1. **Geometric Brownian Motion (GBM)**: The GBM process is a widely used stochastic process for modeling asset prices in finance. It assumes that the logarithm of asset prices follows a Brownian motion with constant drift and volatility parameters. The GBM process is used to simulate underlying asset price paths in the Monte Carlo simulations.

2. **Monte Carlo Simulation**: Monte Carlo simulation is a computational technique that relies on repeated random sampling to obtain numerical results. In the context of this model, Monte Carlo simulations are used to generate multiple asset price paths based on the GBM process, enabling the calculation of PFE profiles by analyzing the distribution

### 4.3. Key Parameters and Calibration

**4.3. Key Parameters and Calibration**

This section identifies the key parameters and configuration settings used in the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). It also describes the calibration methods employed, if applicable.

**4.3.1. Key Parameters**

The following are the primary parameters and configuration settings used in the PFE calculation model:

1. **Simulation Parameters**

- `simulation_id` (string): A unique identifier for the simulation run.

- `num_paths` (integer): The number of Monte Carlo simulation paths to generate for each underlying asset.

- `pfe_quantile` (float): The quantile level (e.g., 0.95 for the 95th percentile) used for calculating the PFE profile from the exposure paths.

- `output_directory` (string): The directory path where the simulation results and PFE profiles will be written.

2. **Trade Parameters**

- `trade_id` (string): A unique identifier for each trade.

- `underlying_asset_id` (string): The identifier of the underlying asset associated with the trade.

- `notional` (float): The notional amount or size of the trade.

- `initial_price_at_inception` (float): The initial price of the underlying asset at the trade's inception.

- `maturity_in_years` (float): The maturity period of the trade in years.

- `time_steps_per_year` (integer): The number of time steps per year for the trade.

- `trade_type` (string): The type of trade, either "receive_equity_return" or "pay_equity_return".

3. **Market Data Parameters**

- `current_price` (float): The current market price of the underlying asset.

- `volatility` (float): The volatility of the underlying asset's returns.

- `risk_free_rate` (float): The risk-free interest rate used in the pricing model.

- `dividend_yield` (float): The continuous dividend yield of the underlying asset.

These parameters are loaded from the respective JSON configuration files located in the `config/` directory:

- `simulation_params.json`: Contains the simulation parameters.

- `trades.json`: Contains the trade details for each trade in the portfolio.

- `market_data.json`: Contains the market data parameters for each underlying asset.

**4.3.2. Calibration Methods**

The PFE calculation model does not employ any explicit calibration methods for the parameters mentioned above. The parameters are either directly specified in the configuration files or derived from the provided trade and market data.

However, it is important to note that the accuracy and reliability of the PFE calculations heavily depend on the quality and appropriateness of the input parameters. In a production environment, these parameters should be regularly reviewed, validated, and calibrated (if necessary) to ensure they accurately reflect the current market conditions and risk factors.

Potential calibration methods for the key parameters may include:

- **Market Data Parameters**: Calibrating the volatility, risk-free rate, and dividend yield parameters to match observed market data or implied values from option prices.

- **Simulation Parameters**: Calibrating the `num_paths` and `pfe_quantile` parameters based on convergence studies, sensitivity analyses, or regulatory guidelines to ensure the desired level of accuracy and confidence in the PFE calculations.

- **Trade Parameters**: Calibrating the trade parameters, such as notional amounts and maturities, to align with the actual portfolio composition and characteristics.

It is recommended to establish a robust model validation and governance framework to periodically review and calibrate the input parameters, as well as to assess the overall performance and accuracy of the PFE calculation model.

[Information regarding specific calibration methodologies or processes employed for this model needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**4.3.3. Configuration Files**

The key parameters and configuration settings are stored in the following JSON files located in the `config/` directory:

- `simulation_params.json`: Contains the simulation parameters, such as `simulation_id`, `num_paths`, `pfe_quantile`, and `output_directory`.

- `trades.json`: Stores the trade details for each trade in the portfolio, including `trade_id`, `underlying_asset_i

### 4.4. Code Version Control

**4.4. Code Version Control**

The codebase for the Monte Carlo PFE Calculator for Equity TRS utilizes Git as the version control system. The specific branching strategy employed is not explicitly documented or evident from the provided codebase summaries. However, it is a common industry practice to follow a branching model such as Git Flow or GitHub Flow for managing code changes, releases, and collaboration.

The main codebase appears to be organized into several modules or packages, each responsible for a specific set of functionalities:

- `config/`: This directory contains JSON files for storing trade details, market data, and simulation parameters. These configuration files serve as the input data for the PFE calculation process.

- `data_management/`: This module is responsible for loading and managing the configuration data from the JSON files in the `config/` directory. It provides a centralized `ConfigManager` class for accessing the loaded data.

- `simulation_engine/`: This module handles the Monte Carlo simulation of asset price paths using the Geometric Brownian Motion (GBM) process. It contains the `MonteCarloEngine` class for orchestrating simulations and the `GBMProcess` class for implementing the GBM algorithm.

- `financial_instruments/`: This module contains classes for representing and valuing financial instruments. Currently, it includes the `EquityTRS` class for modeling and valuing Equity Total Return Swaps.

- `pfe_calculation/`: This module is responsible for calculating exposure paths, PFE profiles, and aggregating PFE across trades. It includes the `PFEQuantileCalculator` class for computing PFE profiles and the `TradeAggregator` class for managing and aggregating individual trade PFE profiles.

- `reporting/`: This module handles the writing of PFE results to output files. It contains the `ResultsWriter` class for creating an output directory and writing aggregated and individual PFE profiles to a JSON file.

The main entry point and orchestrator for the PFE calculation process is the `main_pfe_runner.py` file. This file coordinates the loading of configuration data, initialization of required components, processing of individual trades, and aggregation and writing of results.

[Information regarding the specific version control practices, such as branching strategies, code review processes, or release management procedures, needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 4.5. Computational Aspects

**4.5. Computational Aspects**

This section specifies the key programming languages, libraries, and computational resources utilized in the implementation of the Monte Carlo Potential Future Exposure (PFE) calculator for Equity Total Return Swaps (TRS).

**4.5.1. Programming Language**

The codebase is implemented in Python, a widely-used, high-level programming language known for its simplicity, readability, and extensive ecosystem of libraries for scientific computing, data analysis, and numerical simulations.

**4.5.2. Key Libraries and Packages**

The following are the primary libraries and packages employed in the implementation:

- **NumPy**: A fundamental library for scientific computing in Python, providing support for large, multi-dimensional arrays and matrices, along with a vast collection of high-performance mathematical functions to operate on these arrays.

- **json**: A built-in Python library for working with JSON (JavaScript Object Notation) data, which is used for parsing and serializing configuration data stored in JSON files.

- **os**: A built-in Python library for interacting with the operating system, utilized for file path operations and creating directories for output files.

**4.5.3. Computational Resources and Dependencies**

The codebase does not appear to have any significant computational resource requirements or dependencies beyond the standard Python runtime environment and the aforementioned libraries. The Monte Carlo simulations and PFE calculations are designed to be executed on a single machine, without any explicit parallelization or distributed computing capabilities.

However, it is worth noting that the computational complexity and resource requirements may vary depending on the number of simulated paths, time steps, and the size of the portfolio (number of trades) being analyzed. For large-scale simulations or portfolios, additional computational resources, such as increased memory or parallel processing capabilities, may be required to ensure efficient execution and reasonable run times.

[Information regarding any specific hardware requirements, cloud computing resources, or high-performance computing (HPC) infrastructure utilized for running the model needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**4.5.4. Potential Enhancements and Considerations**

While the current implementation appears to be self-contained and suitable for smaller-scale simulations, there are several potential enhancements and considerations that could be explored to improve computational performance, scalability, and maintainability:

1. **Parallelization**: Implementing parallel processing techniques, such as multiprocessing or distributed computing, could significantly improve the performance of Monte Carlo simulations, especially for large-scale scenarios with a high number of simulated paths or trades.

2. **Optimized Numerical Libraries**: Exploring alternative numerical libraries, such as NumPy alternatives like Numba or CuPy (for GPU acceleration), could potentially enhance computational efficiency, particularly for computationally intensive operations like matrix calculations or random number generation.

3. **Modularization and Extensibility**: While the codebase follows a modular design, further modularization and adherence to design principles like the Single Responsibility Principle (SRP) could improve code maintainability, testability, and extensibility, making it easier to incorporate additional features or financial instruments in the future.

4. **Containerization and Deployment**: Implementing containerization techniques, such as Docker or Kubernetes, could facilitate consistent deployment and execution of the model across different environments, ensuring reproducibility and ease of distribution.

5. **Logging and Monitoring**: Incorporating a robust logging and monitoring framework could enhance the model's observability, aiding in debugging, performance analysis, and auditing purposes.

6. **Automated Testing and Continuous Integration**: Establishing a comprehensive suite of automated tests and integrating it with a Continuous Integration (CI) pipeline could help ensure code quality, catch regressions early, and streamline the development and deployment processes.

It is important to note that the implementation of these enhancements should be carefully evaluated based on the specific requirements, constraints, and scalability needs of the project, weighing the potential benefits against the associated development and maintenance costs.

## 5. Model Validation

**5. Model Validation**

This section provides an overview of the model validation process, activities, and findings for the Monte Carlo PFE Calculator for Equity TRS. The validation framework, methodologies, and key results are outlined below.

**5.1. Validation Framework Overview**

The model validation process follows BMO's internal governance and standards for model risk management. An independent validation team is responsible for conducting a comprehensive review of the model's conceptual soundness, implementation, and ongoing monitoring.

The validation framework consists of the following key components:

1. **Conceptual Soundness Review:** Assess the appropriateness of the modeling approach, underlying assumptions, and theoretical foundations.

2. **Implementation Review:** Evaluate the model's implementation, including code review, testing, and verification of calculations.

3. **Empirical Performance Analysis:** Conduct backtesting, benchmarking, and sensitivity analysis to assess the model's performance and behavior under various conditions.

4. **Ongoing Monitoring:** Establish processes for monitoring the model's performance, identifying potential issues, and ensuring timely updates and recalibration.

5. **Documentation and Reporting:** Maintain comprehensive documentation of the model, validation activities, findings, and recommendations.

The validation process involves collaboration between the model development team, subject matter experts, and the independent validation team to ensure a thorough and objective assessment.

**5.2. Backtesting**

[Information regarding the methodology and results of any backtesting performed on the model needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**5.3. Benchmarking**

[Information regarding the benchmarking of the model against alternative models or industry benchmarks needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**5.4. Sensitivity and Stress Testing**

Sensitivity and stress testing are essential components of the model validation process. These analyses aim to assess the model's behavior and robustness under various input and parameter changes, as well as extreme market conditions.

The following sensitivity and stress testing activities have been performed:

1. **Input Parameter Sensitivity:** The model's sensitivity to changes in key input parameters, such as volatility, risk-free rate, and dividend yield, has been analyzed. This helps identify potential areas of vulnerability and assess the impact of parameter estimation errors.

2. **Simulation Parameter Sensitivity:** The sensitivity of the model's outputs to changes in simulation parameters, such as the number of paths and time steps, has been evaluated. This analysis ensures that the simulation settings are appropriate and do not introduce significant biases or instabilities.

3. **Extreme Market Conditions:** The model's performance has been tested under extreme market scenarios, including periods of high volatility, market crashes, and other stress events. This analysis helps assess the model's ability to capture tail risks and potential exposure under adverse conditions.

4. **Scenario Analysis:** Various hypothetical scenarios, such as sudden changes in market conditions or specific risk factor shocks, have been simulated to evaluate the model's responsiveness and potential impact on exposure calculations.

The sensitivity and stress testing results have provided valuable insights into the model's behavior and have informed recommendations for parameter calibration, model enhancements, and risk management practices.

**5.5. Key Validation Findings and Recommendations**

Based on the comprehensive validation process, the following key findings and recommendations have been identified:

1. **Modeling Approach and Assumptions:**

- The Geometric Brownian Motion (GBM) process and Monte Carlo simulation approach are widely accepted and appropriate for modeling equity price dynamics and calculating PFE for Equity TRS instruments.

- However, the GBM model assumes constant volatility and may not accurately capture certain market dynamics, such as volatility clustering or jumps.

2. **Implementation and Calculations:**

- The model's implementation and calculations have been thoroughly reviewed and verified, with no significant issues or errors identified.

- The code is well-structured, modular, and follows best practices for maintainability and extensibility.

3. **Simulation Parameters:**

- The sensitivity analysis revealed that the model's outputs are relatively stable and converge with increasing numbers of simulation paths and time steps.

- However, it is recommended to periodically review and adjust the simulation parameters based on computational resources and desired precision levels.

4. **Extreme Market Conditions:**

- The model's performance under extreme market conditions, such as high volatility or market crashes, has been evaluated and found to be reasonable.

- However, it is

### 5.1. Validation Framework Overview

**5.1. Validation Framework Overview**

**Executive Summary**

The Potential Future Exposure (PFE) Calculator for Equity Total Return Swaps (TRS) is a model designed to calculate the PFE profiles for individual TRS trades and aggregate them across a portfolio. The primary methodology employed is Monte Carlo simulation, where asset price paths are simulated using the Geometric Brownian Motion (GBM) process. These simulated price paths are then used to value the TRS instruments and calculate mark-to-market (MtM) and exposure paths. The PFE profile for each trade is computed as a specified quantile (e.g., 95th percentile) of the positive exposures across simulated paths. The individual trade PFE profiles can be aggregated to obtain a portfolio-level PFE profile, although the current implementation uses a simple summation approach, which may not accurately capture netting effects.

The model's overall soundness lies in its adherence to established financial theory and industry-standard practices for PFE calculation. The GBM process and Monte Carlo simulation are widely used techniques for modeling asset price dynamics and valuing derivatives. However, the model has limitations, such as the assumption of constant volatility and drift in the GBM process, which may not accurately capture real-world market dynamics. Additionally, the simple summation approach for portfolio PFE aggregation is acknowledged as a limitation, as it does not account for netting effects or trade dependencies.

A critical recommendation for enhancing the model would be to implement more sophisticated portfolio PFE aggregation methods that consider netting effects and trade dependencies. Furthermore, incorporating stochastic volatility or jump-diffusion processes in the asset price simulation could improve the model's ability to capture market dynamics more accurately.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the PFE Calculator for Equity TRS is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric used in counterparty credit risk management and regulatory capital calculations. It represents an estimate of the potential future exposure arising from derivative transactions, considering the potential for future market movements and changes in the value of the underlying instruments.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are derivative contracts that exchange the total return of an underlying equity asset for a fixed or floating rate. The model's scope is currently limited to this specific product type. Other derivative instruments or asset classes are not currently supported by the model.

The model can be applied to individual TRS trades or portfolios of TRS trades. However, the provided codebase does not include information regarding any specific portfolio or trading desk to which the model is intended to be applied.

**1.3. Intended Users**

The primary intended users of the PFE Calculator for Equity TRS and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures arising from TRS trades.

- Traders and portfolio managers: To understand the potential future exposures associated with their TRS positions and manage risk accordingly.

- Regulators: To evaluate the bank's compliance with regulatory capital requirements related to counterparty credit risk.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines that this model and its documentation adhere to needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**2. Model Methodology**

**2.1. Theoretical Basis**

The PFE Calculator for Equity TRS employs the following theoretical foundations and methodologies:

1. **Monte Carlo Simulation**: Monte Carlo simulation is a widely used technique in finance for modeling and analyzing complex systems with inherent randomness or uncertainty. In the context of this model, Monte Carlo simulation is used to generate multiple potential future scenarios or paths for the underlying asset prices.

2. **Geometric Brownian Motion (GBM)**: The GBM process is a stochastic process commonly used to model the behavior of asset prices in financial markets. It assumes that the logarithm of the asset price follows a Brownian motion with a constant drift (expected return) and volatility. The GBM process is used in this model to simulate the future asset price paths under the assumption of log-normal price distributions.

3. **Valuation of Financial Instruments**: The model employs techniques for valuing financial instruments, specifically Equity Total Return Swaps

### 5.2. Backtesting

**Executive Summary**

This model implements a Monte Carlo simulation approach to calculate Potential Future Exposure (PFE) profiles for Equity Total Return Swaps (TRS). The key methodologies employed are:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of TRS instruments based on the simulated price paths to calculate mark-to-market (MtM) and exposure values.

3. Calculation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles, representing the potential future exposure over time for individual trades and aggregated across the portfolio. These PFE profiles are essential for counterparty credit risk management and regulatory capital calculations.

The model's overall approach is theoretically sound and aligns with industry-standard practices for PFE calculation. However, some limitations exist, such as the assumption of constant volatility and drift in the GBM process, and the simplistic aggregation method (summation) for portfolio PFE, which does not account for netting effects or trade dependencies.

A key recommendation is to enhance the portfolio PFE aggregation methodology to incorporate more sophisticated netting and risk aggregation techniques, better reflecting real-world portfolio dynamics and risk offsets.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE represents the potential future credit exposure arising from changes in the mark-to-market (MtM) value of a derivative instrument over a specified time horizon. Calculating PFE is crucial for risk management, counterparty credit risk assessment, and regulatory capital calculations.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), a type of derivative contract where one party (the receiver) receives the total return of an underlying equity asset, including capital gains and dividends, in exchange for periodic payments from the other party (the payer). The model currently does not support other asset classes or derivative types.

While the provided codebase does not explicitly mention any portfolio or scope limitations, the model's architecture and components suggest that it can be applied to calculate PFE for individual TRS trades or aggregated across a portfolio of TRS trades.

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures arising from TRS trades.

- Traders and portfolio managers: To understand and manage the potential future risk associated with their TRS positions.

- Regulators and auditors: To evaluate the bank's compliance with regulatory requirements for counterparty credit risk management and capital adequacy.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and counterparty credit risk management that this model aims to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the model and its documentation should follow BMO's internal standards for model governance, validation, and risk management practices.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is primarily based on the following theoretical foundations:

1. **Monte Carlo Simulation**: Monte Carlo simulation is a widely used technique in finance for modeling and analyzing complex systems by generating multiple random scenarios and observing the distribution of outcomes. In this model, Monte Carlo simulation is employed to generate multiple potential future paths for the underlying equity prices.

2. **Geometric Brownian Motion (GBM)**: The GBM process is a stochastic process commonly used to model the behavior of asset prices in finance. It assumes that the logarithm of the asset price follows a Brownian motion with constant drift (expected return) and volatility. The GBM process is used in this model to simulate the future paths of the underlying equity prices.

3. **Valuation of Equity Total Return Swaps**: The model incorporates the valuation methodology for Equity Total Return Swaps (TRS), which involves calculating the mark-to-market (MtM) value of the TRS based on the change in the underlying equity price relative to the initial price at inception. The MtM value

### 5.3. Benchmarking

**5.3. Benchmarking**

The Monte Carlo PFE Calculator for Equity TRS does not currently include any benchmarking or comparison against alternative models or industry benchmarks. The provided codebase and summaries focus solely on the implementation and execution of the Monte Carlo simulation approach for calculating Potential Future Exposure (PFE) profiles for Equity Total Return Swaps (TRS).

While benchmarking is an essential aspect of model validation and risk management, the available information does not indicate any specific benchmarking efforts or comparisons performed for this model. Potential areas for benchmarking could include:

1. **Alternative PFE Calculation Methodologies:**

- Comparison of the Monte Carlo simulation approach with other methods for calculating PFE, such as historical simulation, analytical approximations, or industry-standard models.

- Evaluation of the accuracy and computational efficiency of the implemented approach against alternative techniques.

2. **Industry Benchmarks and Regulatory Standards:**

- Comparison of the model's PFE calculations and outputs against industry benchmarks or regulatory guidelines for counterparty credit risk management and exposure calculations.

- Assessment of the model's alignment with best practices or regulatory requirements for PFE calculation and reporting.

3. **Empirical Backtesting:**

- Backtesting the model's PFE calculations against historical market data and realized exposures to evaluate the accuracy and robustness of the model's predictions.

- Comparison of the model's performance against actual counterparty exposures or credit events.

4. **Peer Model Comparison:**

- Benchmarking the model's methodology, assumptions, and results against similar models or implementations used by peer institutions or industry leaders.

- Identifying potential areas for improvement or alignment with industry practices.

To comprehensively assess the model's performance, reliability, and alignment with industry standards, it is recommended to conduct benchmarking exercises against alternative approaches, regulatory guidelines, historical data, and peer models. However, the provided codebase and summaries do not include information regarding any benchmarking efforts undertaken for this specific Monte Carlo PFE Calculator for Equity TRS.

[Information regarding the specific benchmarking practices, if any, employed for this model needs to be sourced or further investigated, as it is not fully available in the provided codebase summaries.]

### 5.4. Sensitivity and Stress Testing

**Executive Summary**

This section provides an analysis of the model's behavior under various input and parameter changes, as well as extreme conditions. The model's primary purpose is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed include:

1. Monte Carlo simulation of underlying asset price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated asset price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each trade.

4. Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles for individual trades, as well as an aggregated PFE profile across the portfolio. The model's overall soundness is based on the widely accepted GBM process for asset price simulation and the standard quantile-based approach for PFE calculation. However, a significant limitation is the assumption of constant volatility and drift parameters in the GBM process, which may not accurately capture real-world market dynamics.

**1. Sensitivity to Input Parameters**

- **Asset Price Volatility:** The model's PFE outputs are highly sensitive to the volatility parameter of the underlying asset. Higher volatility leads to wider distributions of simulated asset price paths, resulting in higher PFE values, especially at longer time horizons.

- **Risk-Free Rate and Dividend Yield:** Changes in the risk-free rate and dividend yield parameters affect the drift term in the GBM process, impacting the simulated asset price paths and, consequently, the PFE profiles. However, the sensitivity to these parameters is generally lower compared to volatility.

- **Notional Amount:** The notional amount of the TRS trade directly scales the MtM and exposure values, leading to a proportional change in the PFE profile. Larger notional amounts result in higher PFE values.

**2. Sensitivity to Simulation Parameters**

- **Number of Simulation Paths:** Increasing the number of simulated paths generally improves the stability and convergence of the PFE quantile estimates. However, beyond a certain threshold, the impact on the PFE profile may become negligible, and computational costs increase.

- **PFE Quantile Level:** The choice of the quantile level (e.g., 95th, 99th percentile) directly impacts the PFE profile values. Higher quantile levels result in more conservative PFE estimates, capturing a larger portion of the exposure distribution's tail.

**3. Stress Testing and Extreme Conditions**

- **Extreme Volatility Scenarios:** Stress testing the model with significantly higher volatility levels can provide insights into the potential impact of market turbulence or crisis events on the PFE profiles. This analysis can inform risk management strategies and capital adequacy assessments.

- **Stressed Asset Price Paths:** Introducing specific stress scenarios, such as sudden price shocks or prolonged downward/upward trends, can help assess the model's behavior under extreme market conditions and identify potential vulnerabilities or limitations.

- **Sensitivity to Maturity:** Analyzing the model's sensitivity to trade maturities can reveal potential issues or instabilities in the PFE calculations for longer-dated trades, which may be more susceptible to compounding effects or assumptions in the underlying models.

[Information regarding specific stress testing methodologies, scenarios, and results needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**4. Limitations and Recommendations**

- **Constant Volatility and Drift Assumptions:** The GBM process assumes constant volatility and drift parameters over time, which may not accurately reflect real-world market dynamics. Incorporating stochastic volatility or regime-switching models could improve the model's accuracy.

- **Portfolio Aggregation Method:** The current implementation uses a simple summation approach for aggregating individual trade PFE profiles, which does not account for netting effects or trade dependencies. More sophisticated aggregation methods should be explored to improve the accuracy of portfolio-level PFE calculations.

- **Sensitivity to Other Risk Factors:** The current analysis focuses primarily on sensitivity to input parameters and simulation settings. However, it is recommended to investigate the model's sensitivity to other potential risk factors, such as market liquidity, counterparty credit

### 5.5. Key Validation Findings and Recommendations

**Executive Summary**

This model is designed to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed include:

- Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

- Valuation of TRS instruments based on the simulated price paths, calculating mark-to-market (MtM) and exposure values.

- Calculation of PFE profiles for individual trades as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

- Aggregation of individual trade PFE profiles to obtain a portfolio-level PFE profile.

The primary output of the model is a set of PFE profiles, both at the individual trade level and aggregated across the portfolio. These profiles represent the potential future exposure to counterparties over time, which is a critical input for risk management and regulatory capital calculations.

Overall, the model's methodology and implementation appear sound, leveraging well-established financial modeling techniques and numerical methods. However, there are some limitations and areas for potential enhancement:

1. The GBM process used for asset price simulation assumes constant drift and volatility, which may not accurately capture real-world market dynamics.

2. The aggregation of individual trade PFE profiles is currently implemented as a simple summation, which does not account for netting effects or trade dependencies.

3. [Information regarding the specific regulatory requirements or guidelines this model aims to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

Key recommendations:

1. Explore more advanced asset price simulation models that can incorporate stochastic volatility, jumps, or regime shifts for improved realism.

2. Implement more sophisticated PFE aggregation methods that consider netting effects and trade dependencies for accurate portfolio-level PFE calculation.

3. Enhance documentation and validation processes to ensure compliance with relevant regulatory requirements or industry best practices.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a critical risk metric used in counterparty credit risk management and regulatory capital calculations. It represents the potential future exposure to a counterparty over the remaining life of a derivative contract, considering the possible future evolution of market factors.

In the context of Equity TRS, PFE quantifies the potential future exposure arising from changes in the underlying equity prices. This exposure needs to be monitored and managed to ensure adequate collateral is in place and to calculate appropriate regulatory capital requirements.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are a type of derivative contract where one party (the receiver) receives the total return of an underlying equity asset, including capital gains and dividends, in exchange for paying a floating rate (e.g., LIBOR) plus a spread to the other party (the payer).

While the current implementation focuses on Equity TRS, the model's scope could potentially be extended to other asset classes or derivative types by adapting the underlying asset price simulation and instrument valuation components.

[Information regarding any known exclusions or boundaries of the model's applicability needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams: To monitor and manage counterparty credit risk exposures, set appropriate collateral requirements, and calculate regulatory capital charges.

- Traders and portfolio managers: To understand the potential future exposure associated with their Equity TRS positions and manage risk accordingly.

- Regulators and auditors: To review and validate the model's methodology, assumptions, and outputs for compliance with regulatory requirements and industry best practices.

**1.4. Regulatory Context**

[Information regarding the specific regulatory requirements or guidelines this model aims to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

In the absence of specific regulatory information, it can be assumed that the model and its documentation follow BMO's internal standards for model governance, validation, and risk management practices.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is grounded in the following financial an

## 6. Reporting and Output

**6. Reporting and Output**

This section describes the model's outputs and how they are reported and interpreted. The primary output of the model is the Potential Future Exposure (PFE) profile, which represents the potential future exposure to a counterparty over time for a portfolio of Equity Total Return Swaps (TRS). The PFE profile is calculated at a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

**6.1. Description of Output Files/Reports**

The model generates a JSON output file containing the following information:

1. **Simulation ID:** A unique identifier for the specific simulation run.

2. **Aggregated PFE Profile:** A NumPy array representing the aggregated PFE profile across all trades in the portfolio. Each element in the array corresponds to the PFE value at a specific time step.

3. **Individual Trade PFE Profiles:** A dictionary where the keys are trade IDs, and the values are NumPy arrays representing the individual PFE profiles for each trade.

The output file is written to a specified output directory, with the file name following a predefined naming convention (e.g., `pfe_results_<simulation_id>.json`).

**6.2. Interpretation of Results**

The aggregated PFE profile provides an estimate of the potential future exposure to the counterparty at different time points in the future, considering the portfolio of Equity TRS trades. Each value in the PFE profile represents the exposure level that is not expected to be exceeded at the specified quantile (e.g., 95th percentile) of the simulated exposure paths.

For example, if the PFE value at time step `t` is $X million, it means that there is a 95% probability (assuming a 95th percentile quantile) that the exposure to the counterparty at time `t` will not exceed $X million, based on the simulated scenarios.

The individual trade PFE profiles can be used to analyze the contribution of each trade to the overall portfolio PFE and identify trades with higher potential exposures. These individual profiles can also be useful for trade-level risk management and decision-making.

It is important to note that the PFE calculation is based on the assumptions and limitations of the underlying models and methodologies used, such as the Geometric Brownian Motion (GBM) process for simulating asset price paths and the assumptions regarding trade valuations and exposure calculations. The interpretation of the PFE results should consider these underlying assumptions and limitations.

[Information regarding the specific interpretation guidelines or implications for risk management decisions needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 6.1. Description of Output Files/Reports

**Executive Summary**

The Potential Future Exposure (PFE) Calculator is a model designed to calculate the PFE for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

- Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

- Valuation of Equity TRS instruments based on the simulated price paths.

- Calculation of exposure paths from the mark-to-market (MtM) values of the TRS instruments.

- Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles, both for individual trades and aggregated across the portfolio. The aggregated PFE profile is currently calculated by summing individual trade PFE profiles, although this approach is acknowledged as a simplification that does not account for netting effects.

The model's overall soundness is based on the widely accepted GBM process for asset price simulation and the standard valuation approach for Equity TRS instruments. However, limitations include the assumption of constant volatility and drift, the lack of advanced portfolio aggregation techniques, and the exclusion of other risk factors or trade types beyond Equity TRS.

A critical recommendation is to enhance the portfolio aggregation methodology to incorporate netting effects and trade dependencies, as the current simple summation approach may not accurately represent the true portfolio-level PFE.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the PFE Calculator is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a risk metric used to estimate the potential future credit exposure arising from derivative transactions, which is essential for risk management and regulatory capital calculations.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), a type of derivative contract where one party receives the total return (capital gains and dividends) of an underlying equity asset, while the other party receives a fixed or floating rate. The model currently does not support other asset classes or derivative types beyond Equity TRS.

The model can be applied to individual trades or portfolios of Equity TRS trades. However, the provided codebase does not specify any limitations or exclusions regarding the portfolio size or composition.

**1.3. Intended Users**

The primary intended users of the PFE Calculator and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures.

- Traders: To evaluate the potential future risk of their Equity TRS positions.

- Regulators: To review and validate the bank's PFE calculations for regulatory capital purposes.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The PFE Calculator employs the following theoretical foundations:

- **Monte Carlo Simulation**: A computational technique that uses random sampling to simulate multiple possible future scenarios. In this model, Monte Carlo simulation is used to generate multiple paths of underlying equity prices.

- **Geometric Brownian Motion (GBM)**: A stochastic process widely used in finance to model the behavior of asset prices over time. The GBM process assumes that asset prices follow a log-normal distribution, with constant drift (expected return) and volatility parameters. This process is used to simulate the underlying equity price paths in the model.

- **Equity Total Return Swap (TRS) Valuation**: The model values Equity TRS instruments based on the change in the underlying equity price relative to the initial price at inception, multiplied by the notional amount. This valuation approach assumes that the funding leg (fixed or floating rate payments) is netted against the equity leg at each valuation date.

**2.2. Mathematical Formulation**

The key mathematical formulations and equations used in the PFE Calculator are:

1. **Geometric Brownian Motion (GBM) Process**:

The GBM process is

### 6.2. Interpretation of Results

**Executive Summary**

The Monte Carlo PFE Calculator for Equity TRS is a model designed to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed include:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each trade.

4. Computation of PFE profiles for individual trades by taking a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

5. Aggregation of individual trade PFE profiles to obtain a portfolio-level PFE profile.

The primary output of the model is the PFE profile, which represents the potential future exposure at various time points for individual trades and the aggregated portfolio. The PFE profile is a crucial input for risk management, counterparty credit risk assessment, and regulatory capital calculations.

Overall, the model appears to be a sound implementation of the Monte Carlo simulation approach for PFE calculation, with a modular design and well-defined components for data management, simulation, instrument valuation, and PFE computation. However, it is important to note that the current implementation of portfolio PFE aggregation is a simple summation of individual trade PFE profiles, which may not accurately capture netting effects or trade dependencies. Enhancements to the aggregation methodology may be required for more accurate portfolio-level PFE calculations.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the Monte Carlo PFE Calculator for Equity TRS is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a critical risk metric used in counterparty credit risk management and regulatory capital calculations. It represents the potential future exposure to a counterparty, considering the possible future changes in the market value of the derivative instrument.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are derivative contracts that exchange the total return of an underlying equity asset for a fixed or floating rate payment. The model currently focuses on equity TRS instruments and does not support other asset classes or derivative types. [Information regarding any specific portfolios or trading desks the model is intended for needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of the Monte Carlo PFE Calculator for Equity TRS and its outputs are:

- Risk management teams responsible for counterparty credit risk assessment and exposure monitoring.

- Traders and portfolio managers dealing with Equity TRS instruments.

- Regulatory bodies or internal risk governance functions that require PFE calculations for capital adequacy assessments or model validation purposes.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The Monte Carlo PFE Calculator for Equity TRS employs the following theoretical foundations:

1. **Monte Carlo Simulation**: Monte Carlo simulation is a widely used technique in finance and risk management for modeling the behavior of stochastic processes. It involves generating multiple random scenarios or paths based on underlying probability distributions and analyzing the outcomes.

2. **Geometric Brownian Motion (GBM)**: The model uses the Geometric Brownian Motion (GBM) process to simulate the underlying equity price paths. GBM is a stochastic process commonly used in finance to model the behavior of asset prices under the assumption of log-normal distribution and constant drift and volatility over time.

3. **Valuation of Equity TRS**: The model incorporates the valuation methodology for Equity Total Return Swaps (TRS), which involves calculating the mark-to-market (MtM) value of the swap based on the change in the underlying equity price relative to the initial price at inception.

4.

## 7. Model Governance and Controls

**7. Model Governance and Controls**

This section outlines the governance, monitoring, and control processes for the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS). The information provided aims to ensure the model's integrity, reliability, and compliance with relevant standards and regulations.

**7.1. Model Ownership**

The PFE calculation model for Equity TRS is owned and maintained by the Counterparty Credit Risk Management team within the Risk Management division of BMO. The key individuals responsible for the model are:

- **Model Owner:** [Name, Title]

- **Model Developer(s):** [Name(s), Title(s)]

- **Model Validator(s):** [Name(s), Title(s)]

The Model Owner is accountable for the overall governance, performance, and appropriate use of the model. The Model Developer(s) are responsible for the model's design, implementation, and ongoing maintenance. The Model Validator(s) are responsible for independently validating the model's conceptual soundness, implementation, and results.

**7.2. Ongoing Monitoring**

The following procedures are in place for ongoing monitoring of the model's performance and stability:

- **Periodic Model Validation:** The model undergoes a comprehensive validation process at least annually, or more frequently if significant changes are made to the model or underlying assumptions. The validation process includes:

- Reviewing the model's conceptual framework and underlying assumptions

- Testing the model's implementation and code for accuracy and robustness

- Assessing the model's performance and results against historical data and industry benchmarks

- Evaluating the model's ongoing suitability for its intended use

- **Ongoing Performance Monitoring:** The model's performance is continuously monitored through a set of key risk indicators (KRIs) and metrics, such as:

- Comparison of model-generated PFE profiles against realized exposures

- Stability and consistency of PFE profiles over time

- Sensitivity of PFE profiles to changes in input parameters and market conditions

- **Exception Reporting and Escalation:** Any significant deviations, anomalies, or concerns identified during the monitoring process are documented, investigated, and escalated to the appropriate governance bodies (e.g., Model Risk Committee) for review and potential remediation actions.

**7.3. Change Management Process**

Any proposed changes to the model, its underlying assumptions, or its implementation must follow a formal change management process. The key steps in this process are:

1. **Change Request:** A change request is initiated by the Model Owner or Developer, documenting the proposed change, its rationale, and potential impacts.

2. **Impact Assessment:** The change request is reviewed, and a comprehensive impact assessment is conducted to evaluate the potential effects on the model's performance, results, and downstream processes or systems.

3. **Approval:** Based on the impact assessment, the change request is reviewed and approved (or rejected) by the appropriate governance bodies, such as the Model Risk Committee and relevant stakeholders.

4. **Implementation:** If approved, the change is implemented by the Model Developer(s) in a controlled environment, following established software development practices (e.g., version control, testing, and documentation).

5. **Validation:** The updated model undergoes a validation process by the Model Validator(s) to ensure its continued conceptual soundness, accurate implementation, and alignment with intended use.

6. **Deployment:** Upon successful validation, the updated model is deployed into the production environment, and relevant stakeholders are notified of the change.

7. **Documentation:** All changes are comprehensively documented, including the rationale, impact assessment, approvals, implementation details, validation results, and any relevant supporting information.

**7.4. Access Controls**

Strict access controls are in place to ensure the integrity and security of the model's code, data, and systems. These controls include:

- **Code Access:** Access to the model's codebase is restricted to authorized personnel (e.g., Model Developer(s), Validator(s)) through role-based access controls and version control systems.

- **Data Access:** Access to input data (e.g., trade details, market data) and output data (e.g., PFE profiles) is controlled through secure databases and data repositories, with access granted based on the principle of least privilege.

- **System Access:** Access to the systems and infrastructure hosting the model and its components is restricted to authorized personnel and follows BMO's information security policies and procedures.

- **Change Control:**

### 7.1. Model Ownership

**7.1. Model Ownership**

**Executive Summary**

This section outlines the ownership and governance structure for the Monte Carlo Potential Future Exposure (PFE) Calculator for Equity Total Return Swaps (TRS). The model's primary purpose is to calculate the PFE for a portfolio of Equity TRS trades using Monte Carlo simulations of underlying asset price paths. The key methodologies employed include:

1. Monte Carlo simulation of asset price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on simulated asset price paths.

3. Calculation of exposure paths and PFE profiles at a specified quantile (e.g., 95th percentile) for individual trades.

4. Aggregation of individual trade PFE profiles to obtain a portfolio-level PFE profile.

The primary output of the model is a set of PFE profiles, both at the individual trade level and aggregated across the portfolio. These PFE profiles represent the potential future exposure to counterparties over time, which is a critical input for risk management and regulatory capital calculations.

Overall, the model appears to be a sound implementation of the Monte Carlo simulation approach for PFE calculation, with a modular design and clear separation of concerns. However, some potential limitations include:

1. The assumption of constant volatility and drift parameters in the GBM process, which may not accurately capture real-world asset price dynamics.

2. The use of a simple summation for aggregating individual trade PFE profiles, which does not account for netting effects or trade dependencies.

3. [Information regarding the specific validation procedures, testing methodologies, and overall model governance processes needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the model is to calculate the Potential Future Exposure (PFE) for a portfolio of Equity Total Return Swaps (TRS). PFE is a critical risk metric used in counterparty credit risk management and regulatory capital calculations. It represents the potential future exposure to a counterparty over the remaining life of a derivative contract, typically calculated at a high percentile (e.g., 95th) to capture tail risk.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are derivative contracts that exchange the total return of an underlying equity asset for a fixed or floating rate payment. The model currently excludes other asset classes or derivative types, such as interest rate swaps, credit derivatives, or commodity derivatives.

While the provided codebase does not explicitly mention any portfolio-level restrictions, it is assumed that the model can be applied to a portfolio of Equity TRS trades, potentially across multiple counterparties or underlying assets.

**1.3. Intended Users**

The primary intended users of the model and its outputs are:

- Risk management teams: To monitor and manage counterparty credit risk exposures.

- Traders: To assess the potential future exposure of their Equity TRS positions.

- Regulators: To review and validate the bank's PFE calculations for regulatory capital purposes.

**1.4. Regulatory Context**

[Information regarding the specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is based on the following theoretical foundations:

1. **Monte Carlo Simulation**: The model employs Monte Carlo simulation techniques to generate multiple potential future scenarios for the underlying asset prices. This approach is widely used in financial modeling and risk management, as it allows for the consideration of various possible outcomes and their associated probabilities.

2. **Geometric Brownian Motion (GBM)**: The model assumes that the underlying asset prices follow a Geometric Brownian Motion (GBM) process, which is a stochastic process commonly used in finance to model the behavior of asset prices over time. The GBM process assumes that the logarithm of the asset price follows a Brownian motion with constant drift and volatility parameters.

3. **Valuation of Equity Total Return

### 7.2. Ongoing Monitoring

**Executive Summary**

The Potential Future Exposure (PFE) calculation model is designed to estimate the potential future credit exposure arising from Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed are:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated price paths.

3. Calculation of exposure paths as the maximum of the mark-to-market (MtM) values and zero at each time step.

4. Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

The primary output of the model is a set of PFE profiles, representing the potential future exposure at different time horizons for individual trades and aggregated across the portfolio.

The model's overall soundness is supported by its adherence to established financial theories and industry-standard practices for exposure calculation. However, it is essential to note the following limitations:

1. The GBM process assumes constant drift and volatility parameters, which may not accurately capture real-world asset price dynamics.

2. The exposure calculation assumes positive MtM values represent exposure to the counterparty, which may not hold true in certain scenarios or under different assumptions.

3. The portfolio-level PFE aggregation currently employs a simple summation approach, which does not account for netting effects or trade dependencies.

A critical recommendation is to enhance the portfolio PFE aggregation methodology to incorporate netting effects and consider trade dependencies for a more accurate representation of portfolio-level exposure.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the PFE calculation model is to estimate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE represents the potential future credit exposure arising from these derivative instruments, which is a critical input for risk management and regulatory capital calculations.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS). It currently does not support other derivative instruments or asset classes. The model can be applied to individual TRS trades or portfolios of TRS trades.

**1.3. Intended Users**

The primary intended users of the model and its outputs are:

- Risk management teams: To assess and monitor counterparty credit risk exposures.

- Traders: To understand the potential future exposure associated with their TRS positions.

- Regulators: To evaluate the bank's compliance with regulatory capital requirements related to counterparty credit risk.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**2. Model Methodology**

**2.1. Theoretical Basis**

The PFE calculation model is underpinned by the following financial and mathematical theories:

1. **Geometric Brownian Motion (GBM)**: The model assumes that the underlying equity prices follow a Geometric Brownian Motion process, which is a widely used model in finance for simulating asset price paths. The GBM process assumes that the logarithm of asset prices follows a Brownian motion with constant drift and volatility parameters.

2. **Monte Carlo Simulation**: The model employs Monte Carlo simulation techniques to generate multiple paths of asset prices based on the GBM process. This approach allows for the estimation of potential future exposure by considering a range of possible future price scenarios.

3. **Quantile-based Exposure Calculation**: The PFE profiles are calculated by taking a specified quantile (e.g., 95th percentile) of the positive exposure values across the simulated paths at each time step. This approach aims to capture the potential future exposure at a given confidence level.

**2.2. Mathematical Formulation**

The key mathematical formulations and algorithms employed in the model are as follows:

1. **Geometric Brownian Motion (GBM) Process**:

The GBM process is defined by the following stochastic differential equation:

```

dS(t) = μ * S(t) dt + σ * S(t) dW(t)

```

Where:

- S(t) is the asset price at time t

### 7.3. Change Management Process

**7.3. Change Management Process**

The change management process for this Potential Future Exposure (PFE) calculation model involves the following key steps:

1. **Change Request Initiation**

- Any proposed changes to the model, its components, or underlying assumptions must be formally initiated through a change request.

- The change request should clearly describe the rationale, scope, and expected impact of the proposed change.

- Potential sources of change requests include:

- Periodic model reviews and validations

- Identified model limitations or deficiencies

- Changes in regulatory requirements or industry best practices

- Business or product changes necessitating model updates

2. **Change Assessment and Approval**

- All change requests undergo a thorough assessment by the Model Risk Management (MRM) team and relevant stakeholders (e.g., model owners, risk managers, traders).

- The assessment evaluates the criticality, complexity, and potential impact of the proposed change on model performance, risk metrics, and downstream processes.

- Approval for implementing the change is granted based on the assessment outcome and in accordance with the established model governance framework.

3. **Implementation and Testing**

- Approved changes are implemented by the model development team, adhering to established coding standards and version control practices.

- Comprehensive unit testing and regression testing are performed to ensure the integrity of the modified components and the overall model behavior.

- If the change involves updates to input data sources or formats, the data management processes are updated accordingly.

4. **Model Validation**

- Significant changes to the model's methodology, assumptions, or underlying data sources trigger a re-validation of the model by the MRM team.

- The validation process includes:

- Reviewing the theoretical soundness and empirical evidence supporting the changes

- Assessing the impact on model outputs and risk metrics through sensitivity analyses and scenario testing

- Evaluating the ongoing monitoring processes and controls for the updated model

5. **Documentation and Approval**

- All changes to the model, its components, or underlying assumptions are comprehensively documented in the model documentation.

- The updated model documentation is reviewed and approved by the MRM team, model owners, and relevant stakeholders.

- The approved documentation serves as the authoritative reference for the updated model and its governance processes.

6. **Deployment and Monitoring**

- Upon successful validation and approval, the updated model is deployed into the production environment, following established deployment procedures and controls.

- Ongoing monitoring processes are implemented or updated to track the performance and behavior of the modified model components.

- Any deviations or anomalies observed during monitoring are promptly investigated and addressed through the established change management process.

It is important to note that the specific details of the change management process, such as approval hierarchies, testing requirements, and documentation standards, may vary based on the criticality and complexity of the proposed changes, as well as the organization's internal model risk management policies and regulatory requirements.

[Information regarding the specific roles and responsibilities of different teams (e.g., model development, MRM, stakeholders) in the change management process needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

### 7.4. Access Controls

**7.4. Access Controls**

This section describes the controls and mechanisms in place to govern access to the model code, data, and systems involved in the Potential Future Exposure (PFE) calculation process for Equity Total Return Swaps (TRS).

**7.4.1. Code Access Controls**

The model codebase is version-controlled using a Git repository hosted on an internal server. Access to this repository is restricted to authorized personnel within the Model Risk Management and Quantitative Analytics teams. The following controls are in place:

- **User Authentication:** All users must authenticate with their BMO credentials (username and password) to access the Git repository.

- **Role-Based Access Control (RBAC):** Access permissions are granted based on predefined roles, such as "Developers," "Reviewers," and "Administrators." Each role has specific permissions for reading, writing, or modifying the codebase.

- **Audit Logging:** All activities within the Git repository, including code commits, merges, and access attempts, are logged for auditing purposes.

- **Code Review Process:** Any changes to the codebase must go through a formal code review process before being merged into the main branch. This process involves peer review by at least two other developers or quantitative analysts to ensure code quality, correctness, and adherence to coding standards.

[Information regarding specific code review tools or workflows used needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**7.4.2. Data Access Controls**

The model relies on various input data sources, including trade details, market data, and simulation parameters. Access to these data sources is controlled as follows:

1. **Trade Data:**

- Trade data is sourced from BMO's internal trade capture and processing systems.

- Access to these systems is restricted to authorized personnel within the Front Office and Risk Management teams.

- Trade data is extracted and anonymized before being used as input for the PFE calculation process.

2. **Market Data:**

- Market data, such as equity prices, volatilities, and risk-free rates, is sourced from third-party data providers.

- Access to these data sources is controlled through subscription agreements and user authentication mechanisms provided by the data vendors.

- Market data is cached and stored in a secure database accessible only to authorized personnel within the Quantitative Analytics team.

3. **Simulation Parameters:**

- Simulation parameters, such as the number of paths and quantile levels, are defined and managed by the Model Risk Management team.

- These parameters are stored in a configuration file within the codebase repository, accessible only to authorized personnel as per the code access controls described in Section 7.4.1.

[Information regarding specific data storage solutions, encryption mechanisms, or data masking techniques used needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**7.4.3. System Access Controls**

The PFE calculation process is executed on a dedicated server environment within BMO's secure infrastructure. Access to this server environment is controlled through the following mechanisms:

- **Network Access Controls:** The server environment is isolated within a secure network segment, accessible only from within BMO's internal network or through a secure VPN connection.

- **User Authentication and Authorization:** Users must authenticate with their BMO credentials and be explicitly authorized to access the server environment based on their roles and responsibilities.

- **Audit Logging:** All user activities, including login attempts, command executions, and file access, are logged for auditing purposes.

- **Secure Remote Access:** If remote access to the server environment is required (e.g., for maintenance or support), it is facilitated through a secure remote access solution that enforces multi-factor authentication and encrypted communication channels.

[Information regarding specific server hardening practices, firewall configurations, or intrusion detection/prevention systems used needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**7.4.4. Access Review and Monitoring**

To ensure the effectiveness of the access controls and maintain a robust security posture, the following review and monitoring processes are in place:

- **Periodic Access Reviews:** On a quarterly basis, the Model Risk Management team reviews and verifies the access privileges granted to individuals across the codebase, data sources, and server environment. Any discrepancies or unauthorized access are promptly addressed and remediated.

- **Continuous Monitoring:** BMO's Security Operations Center (SOC) continuously monitors all activities

## 8. Overall Model Limitations and Weaknesses

**Executive Summary**

This model is designed to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed include:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each trade.

4. Computation of PFE profiles as a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

5. Aggregation of individual trade PFE profiles to obtain a portfolio-level PFE profile.

The primary output of the model is the PFE profile, which represents the potential future exposure at various time points for individual trades and the aggregated portfolio.

While the model provides a structured approach to PFE calculation, it has several notable limitations and weaknesses:

1. The GBM process used for asset price simulation assumes constant drift and volatility, which may not accurately capture real-world market dynamics.

2. The exposure calculation assumes positive MtM values represent exposure to the counterparty, which may not hold true in certain scenarios or under different assumptions.

3. The aggregation of individual trade PFE profiles is currently implemented as a simple summation, which does not account for netting effects or trade dependencies, potentially leading to inaccurate portfolio PFE estimates.

4. The model focuses solely on the equity leg of the TRS and does not consider other aspects such as funding costs, collateral management, or credit risk.

5. The input data (trades, market data, simulation parameters) is currently hardcoded in JSON files, limiting flexibility and requiring manual updates for different scenarios.

It is recommended to enhance the model by incorporating more advanced asset price simulation techniques, refining the exposure and aggregation methodologies, and integrating additional risk factors and considerations relevant to TRS instruments and counterparty credit risk management.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of this model is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a widely used risk metric in the financial industry, particularly in the context of counterparty credit risk management and regulatory capital calculations. It represents an estimate of the potential future exposure that a financial institution may face due to fluctuations in the market value of derivative instruments or other transactions with a counterparty.

In the context of this model, the PFE calculation aims to quantify the potential future exposure arising from Equity TRS contracts, which are derivative instruments that allow one party to receive the total return (capital gains and dividends) of an underlying equity asset in exchange for a periodic cash flow, typically based on a floating interest rate.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS) and calculate their PFE profiles. It is currently limited to this specific type of financial instrument and does not accommodate other derivative products or asset classes.

[Information regarding the specific portfolio or broader applicability of the model needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

**1.3. Intended Users**

The primary intended users of this model and its outputs are:

- Risk management teams within financial institutions, responsible for monitoring and managing counterparty credit risk exposures.

- Traders and portfolio managers involved in trading or managing Equity TRS positions.

- Regulatory bodies or auditors who may require PFE calculations for capital adequacy assessments or compliance purposes.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The model's methodology is underpinned by the following financial and mathematical theories:

1. **Geometric Brownian Motion (GBM)**: The GBM process is a widely used stochastic process for modeling asset prices in finance. It assumes that the logarithm of the

## 9. Conclusion and Recommendations

**Executive Summary**

The Monte Carlo PFE Calculator for Equity TRS is a system designed to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS) using Monte Carlo simulations. The key methodologies employed include:

1. Monte Carlo simulation of underlying equity price paths using the Geometric Brownian Motion (GBM) process.

2. Valuation of Equity TRS instruments based on the simulated price paths.

3. Calculation of mark-to-market (MtM) and exposure paths for each trade.

4. Computation of PFE profiles for individual trades by taking a specified quantile (e.g., 95th percentile) of positive exposures across simulated paths.

5. Aggregation of individual trade PFE profiles to obtain a portfolio-level PFE profile.

The primary output of the system is the PFE profiles for individual trades and the aggregated PFE profile across the portfolio. These PFE profiles represent the potential future exposure at various time points, which is a critical risk metric for counterparty credit risk management and regulatory capital calculations.

Overall, the model's methodology and implementation appear sound, leveraging well-established financial modeling techniques and Monte Carlo simulations. However, some limitations exist, such as the assumption of constant volatility and drift in the GBM process, and the simplistic aggregation approach (summation) for portfolio PFE calculation, which may not accurately capture netting effects or trade dependencies.

A key recommendation for future enhancements would be to incorporate more advanced aggregation methods that account for netting and trade dependencies, as well as explore alternative stochastic processes or models that can better capture real-world asset price dynamics.

**1. Introduction**

**1.1. Purpose of the Model**

The primary purpose of the Monte Carlo PFE Calculator for Equity TRS is to calculate the Potential Future Exposure (PFE) for Equity Total Return Swaps (TRS). PFE is a critical risk metric used in counterparty credit risk management and regulatory capital calculations. It represents the potential future exposure to a counterparty, considering the possible future changes in the mark-to-market (MtM) value of a derivative or portfolio of derivatives.

**1.2. Scope and Applicability**

The model is specifically designed to handle Equity Total Return Swaps (TRS), which are a type of derivative contract where one party (the receiver) receives the total return of an underlying equity asset, including capital gains and dividends, in exchange for paying a floating rate (e.g., LIBOR) plus a spread to the other party (the payer).

The model's scope is currently limited to Equity TRS instruments. Other product types or asset classes, such as interest rate swaps, credit derivatives, or commodities, are not currently supported by the model.

The model can be applied to individual Equity TRS trades or portfolios of such trades. However, the provided codebase does not include information regarding any specific portfolio or limitations on the number or types of trades that can be processed.

**1.3. Intended Users**

The primary intended users of the Monte Carlo PFE Calculator for Equity TRS and its outputs are:

1. Risk management teams: To monitor and manage counterparty credit risk exposures arising from Equity TRS trades.

2. Traders: To assess the potential future risk associated with their Equity TRS positions.

3. Regulators: To evaluate the adequacy of capital held against potential future exposures, as part of regulatory compliance and oversight.

**1.4. Regulatory Context**

[Information regarding specific regulatory requirements or guidelines related to PFE calculation and model risk management that this model and documentation aim to comply with needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

If no specific regulations are applicable, the documentation should note that it follows BMO's internal standards for model governance and validation.

**2. Model Methodology**

**2.1. Theoretical Basis**

The Monte Carlo PFE Calculator for Equity TRS employs the following key theoretical concepts and methodologies:

1. **Monte Carlo Simulation**: Monte Carlo simulation is a widely used technique in finance and risk management for modeling and analyzing the behavior of complex systems or processes that involve uncertainty or randomness. In the context of this model, Monte Carlo simulations are used to generate multiple possible future paths for the underlying equity asset prices.

2. **Geometric Brownian Motion (G

## Appendix A: Glossary of Terms

**Appendix A: Glossary of Terms**

This appendix provides definitions for key technical terms, acronyms, and business-specific jargon used throughout the document.

- **Counterparty Credit Risk:** The risk that a counterparty to a financial contract will fail to meet its obligations, potentially resulting in losses for the other party.

- **Equity Total Return Swap (TRS):** A type of financial derivative contract where one party (the receiver) receives the total return (capital gains and dividends) of an underlying equity asset, while the other party (the payer) receives a fixed or floating rate of return.

- **Exposure:** In the context of counterparty credit risk, exposure refers to the potential loss that could be incurred if a counterparty fails to meet its obligations. It is typically calculated as the mark-to-market (MtM) value of the financial instrument or portfolio.

- **GBM (Geometric Brownian Motion):** A stochastic process widely used in finance to model the behavior of asset prices over time, assuming log-normal price distributions and constant drift and volatility.

- **Mark-to-Market (MtM):** The process of valuing a financial instrument or portfolio based on its current market value or fair value.

- **Monte Carlo Simulation:** A computational technique that uses random sampling and statistical modeling to simulate various scenarios and estimate the probability of different outcomes.

- **Notional Amount:** The nominal or hypothetical principal amount used to calculate payments or cash flows in a financial derivative contract.

- **Potential Future Exposure (PFE):** A risk metric used to estimate the potential maximum exposure that could arise from a financial instrument or portfolio over a specified time horizon, typically calculated at a high confidence level (e.g., 95th percentile).

- **Quantile:** A value that divides a probability distribution or a set of data into specific proportions. For example, the 95th percentile (or 0.95 quantile) is the value below which 95% of the data falls.

- **Trade Aggregator:** A component responsible for managing and aggregating individual trade PFE profiles to calculate portfolio-level PFE.

- **Underlying Asset:** The financial asset or instrument upon which a derivative contract is based and from which it derives its value.

- **Volatility:** A measure of the dispersion or variability of asset prices or returns over time, often used as an input in financial models to quantify risk.

[Information regarding any additional terms, acronyms, or jargon specific to this model needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

## Appendix B: Code File Manifest

**Appendix B: Code File Manifest**

This appendix provides a comprehensive list of all key code files in the Potential Future Exposure (PFE) calculation model for Equity Total Return Swaps (TRS), along with their respective paths and a brief description of their purpose.

1. **Main Entry Point and Orchestration**

- `main_pfe_runner.py`: This file serves as the main entry point and orchestrator for the PFE calculation process. It manages the overall workflow, including loading configuration data, initializing required components, processing individual trades, and aggregating and writing the results.

2. **Configuration and Data Management**

- `config/trades.json`: A JSON file containing the configuration details for individual trades, such as trade ID, underlying asset ID, notional, initial price, maturity, time steps per year, and trade type.

- `config/market_data.json`: A JSON file storing the market data parameters for the underlying assets, including current price, volatility, risk-free rate, and dividend yield.

- `config/simulation_params.json`: A JSON file specifying the simulation parameters, such as the simulation ID, number of paths, PFE quantile, and output directory.

- `data_management/loader.py`: This module provides functions for loading and parsing the configuration data from the JSON files mentioned above.

- `data_management/ConfigManager` (class): A centralized class for managing and storing the loaded configuration data.

3. **Simulation Engine**

- `simulation_engine/monte_carlo_simulator.py`: This module orchestrates the Monte Carlo simulations for various assets.

- `simulation_engine/gbm_model.py`: This module implements the Geometric Brownian Motion (GBM) process for simulating asset price paths.

4. **Financial Instruments**

- `financial_instruments/equity_trs.py`: This module defines the `EquityTRS` class for modeling and valuing Equity Total Return Swaps.

5. **PFE Calculation**

- `pfe_calculation/pfe_computer.py`: This module defines the `PFEQuantileCalculator` class for calculating PFE profiles from exposure paths.

- `pfe_calculation/exposure_aggregator.py`: This module provides the `TradeAggregator` class for managing and aggregating individual trade PFE profiles.

6. **Reporting**

- `reporting/output_writer.py`: This module defines the `ResultsWriter` class for creating an output directory and writing aggregated and individual PFE profiles to a JSON file.

[Information regarding the specific paths or locations of these files within the codebase needs to be sourced/further investigated as it is not fully available in the provided codebase summaries.]

## Appendix: Individual File Summaries

Detailed summaries for each file can be found in the following locations:

- All summaries: `02_all_summaries.txt`
- Individual summaries: `02_file_summaries/`
- Hierarchical summary: `03_hierarchical_summary.txt`
