# Olist E-Commerce ETL Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualizations-3776AB?style=for-the-badge&logo=python&logoColor=white)


</div>

---

## Overview

This project implements a fully automated, production-grade **ETL (Extract, Transform, Load)** pipeline coupled with a multi-domain **Business Intelligence & Analytics suite**. Built around the Olist Brazilian E-Commerce dataset, the system cleans raw relational data, normalizes it into a local SQLite data warehouse, and generates executive-ready 4-panel visual dashboards tracking core business KPIs.

---

## Analytical Insights & Dashboards

The pipeline automatically compiles and plots multi-metric Seaborn dashboards saved under data/output/:

Logistics & Delivery Performance: Evaluates carrier transit times, delivery delays, and fulfillment bottlenecks.

Products & Revenue Concentration: Identifies top-performing product categories, revenue drivers, and volumetric weight distributions.

Payment Behaviors: Analyzes installment trends, preferred transaction types, and payment value distributions.

Seller Performance: Ranks regional merchant efficiency and delivery compliance.

Customer Geography: Maps state-by-state customer distribution, macro-region shares (Southeast, South, Northeast, etc.), and city concentrations.

Geolocation Spatial Density: Spatial mapping of zip-code coordinates across Brazil.

---

## Getting Started & Installation

1. Clone the Repository

git clone [https://github.com/your-username/ETL_Pipeline.git](https://github.com/your-username/ETL_Pipeline.git)
cd ETL_Pipeline

2. Set Up Virtual Environment

python -m venv venv
venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

---

## Execution

python main.py

---

## Built With

Python: Core pipeline orchestration and data manipulation.

Pandas & NumPy: Data cleaning, transformation, and numerical aggregation.

SQLite & SQL: Relational database storage and querying.

Matplotlib & Seaborn: Automated executive reporting and multi-panel data visualization.

---
