# MediAnalytics – Healthcare Data Analysis & Patient Management System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Academic](https://img.shields.io/badge/Course-FDS%2021CSS202T-teal.svg)](#fds-syllabus-coverage)

A full-stack, enterprise-grade healthcare data science and patient management web application built with **Django**, **Bootstrap 5**, **NumPy**, **Pandas**, **Matplotlib**, and **Seaborn**. Designed for academic rigor, clinical simulation, and data science workflows.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Academic Abstract (FDS 21CSS202T)](#2-academic-abstract-fds-21css202t)
- [3. Key Features (13 Modules)](#3-key-features-13-modules)
- [4. Technology Stack](#4-technology-stack)
- [5. Prerequisites](#5-prerequisites)
- [6. Installation & Setup](#6-installation--setup)
- [7. Default Login Credentials](#7-default-login-credentials)
- [8. Project Structure](#8-project-structure)
- [9. Database Schema](#9-database-schema)
- [10. FDS Syllabus Coverage (21CSS202T)](#10-fds-syllabus-coverage-21css202t)
- [11. Screenshots Checklist](#11-screenshots-checklist)
- [12. Testing](#12-testing)
- [13. Troubleshooting (Windows / PowerShell)](#13-troubleshooting-windows--powershell)
- [14. Authors & Acknowledgments](#14-authors--acknowledgments)
- [15. License](#15-license)
- [16. Medical Disclaimer](#16-medical-disclaimer)

---

## 1. Project Overview

**MediAnalytics** is an end-to-end healthcare analytics and clinical record management portal. It bridges clinical workflows (patient registration, longitudinal EHR tracking, biometric recordings) with modern data engineering and statistical analytics (automated data pre-processing, missing value imputation, outlier detection, biomarker correlation matrices, and automated PDF reporting).

Built specifically for the **Fundamentals of Data Science (21CSS202T)** curriculum, MediAnalytics showcases how data science techniques can be operationalized inside an interactive web system with role-based access control.

---

## 2. Academic Abstract (FDS 21CSS202T)

Modern clinical healthcare environments generate voluminous biometric and diagnostic data, yet medical decision support systems frequently suffer from data quality deficits—including missing clinical observations, duplicate entries, non-standardized categorical attributes, and skewed clinical biomarker measurements.

This project introduces **MediAnalytics**, an integrated software platform engineered to illustrate the complete data science lifecycle within healthcare informatics:
1. **Data Ingestion**: Multi-format clinical datasets ingestion (CSV, structured EHR records).
2. **Data Wrangling & Cleaning**: Algorithmic handling of missing data via mean/median/mode imputation, deduplication protocols, and label standardization.
3. **Exploratory Data Analysis (EDA)**: Statistical characterization of central tendency, dispersion, interquartile ranges (IQR), and skewness across cardiac biomarkers (e.g., Troponin, CK-MB, Blood Pressure, Cholesterol).
4. **Data Visualization**: Automated generation of publication-quality univariate, bivariate, and multivariate visualizations (boxplots, kernel density histograms, scatter plots, correlation heatmaps).
5. **Statistical Risk Stratification & Reporting**: Parametric (Z-score) and non-parametric (IQR) outlier detection algorithms combined with automated report generation.

Implemented using Django, SQLite, NumPy, and Pandas, MediAnalytics delivers a reproducible, fully auditable computational environment adhering to the syllabus requirements of course **21CSS202T**.

---

## 3. Key Features (13 Modules)

1. **User Authentication & Role-Based Access Control (RBAC)**: Secure multi-role access (Administrator, Medical Doctor, Clinical Data Analyst) utilizing Django authentication.
2. **Executive Analytical Dashboard**: Real-time KPI indicator cards (Total Patients, Active Records, Ingestion Status, Positive Outcomes Rate) with high-level visual charts.
3. **Patient Registry & Demographics Manager**: Full CRUD operations for patient profiles, demographic tracking, contact records, and patient search.
4. **Longitudinal Clinical Records & EHR**: Patient-centric medical checkup histories capturing vitals (Systolic/Diastolic BP, Heart Rate) and cardiac biomarkers (Troponin, CK-MB, Blood Glucose, Cholesterol).
5. **Dataset Ingestion Pipeline**: Safe CSV upload interface with schema verification, encoding detection, and file storage integrity checks.
6. **Data Pre-processing & Cleaning Engine**: Automated tools for handling null/missing fields, duplicate record elimination, and categorical harmonization.
7. **Exploratory Data Analysis (EDA) Workbench**: On-demand statistical summaries, quartile breakdowns, variance, and data distribution metrics.
8. **Univariate & Bivariate Visualization Engine**: Automated rendering and caching of clinical charts (histograms, violin/box plots, pairwise scatter plots).
9. **Correlation & Multivariate Statistical Analysis**: Heatmaps and correlation matrices computing Pearson and Spearman coefficients between vital signs and diagnostic outcomes.
10. **Outlier & Anomaly Detection**: Dual-technique outlier filtering (Standard Deviation / Z-score and Interquartile Range method) for anomaly flag alerts.
11. **Automated Clinical Report Generator**: One-click generation and export of formatted diagnostic summaries and analytical evaluation reports.
12. **Synthetic Healthcare Data Generator**: Custom Django CLI command leveraging NumPy seeds to generate reproducible, realistic clinical cohorts with controlled data noise.
13. **System Audit & Data Management**: Audit trails tracking dataset versions, upload histories, and database maintenance tools.

---

## 4. Technology Stack

- **Backend Framework**: Python 3.10+, Django 4.2+ (MTV Architecture)
- **Database**: SQLite3 (ACID compliant, zero-config relational store)
- **Frontend Architecture**: HTML5, Modern CSS3 Custom Properties, Vanilla JavaScript (ES6+), Bootstrap 5.3 CDN, Bootstrap Icons
- **Data Science & Statistics**:
  - `numpy`: Numerical processing, synthetic distribution generation, array operations
  - `pandas`: DataFrames, data cleaning, aggregation, exploratory analysis
  - `scipy`: Statistical computations, z-scores, hypothesis metrics
- **Data Visualization**:
  - `matplotlib`: Core visualization generation and canvas rendering
  - `seaborn`: Statistical data visualization, regression plots, and correlation heatmaps
- **Reporting & Export**: CSV export, HTML-to-PDF / printable reports engine

---

## 5. Prerequisites

Before setting up MediAnalytics on your machine, verify the following are installed:
- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Version 3.10 or higher (`py --version` or `python --version`)
- **Package Manager**: `pip` (included with Python installations)
- **Shell**: PowerShell 5.1+ or PowerShell Core 7+ (on Windows)

---

## 6. Installation & Setup

Execute the following commands sequentially in **PowerShell**:

```powershell
# 1. Navigate to the project directory
cd "d:\Engineering Subjects\FDS Fundamentels of data science\Healthcare Management\MediAnalytics"

# 2. Create a Python virtual environment
py -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 4. Upgrade pip and install all required dependencies
py -m pip install --upgrade pip
py -m pip install -r requirements.txt

# 5. Create database migrations for all project apps
py manage.py makemigrations accounts patients medical_records datasets analytics reports

# 6. Apply database migrations
py manage.py migrate

# 7. Generate synthetic benchmark dataset, superuser, and sample records
py manage.py generate_sample_data

# 8. Start the development server
py manage.py runserver
```

Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 7. Default Login Credentials

Upon running `py manage.py generate_sample_data`, a pre-configured administrator account is created:

| Field | Value |
|---|---|
| **URL** | `http://127.0.0.1:8000/accounts/login/` |
| **Username** | `admin` |
| **Password** | `admin123` |
| **Role** | System Administrator |

---

## 8. Project Structure

```text
MediAnalytics/
├── manage.py                          # Django command-line execution utility
├── requirements.txt                   # Production Python package dependencies
├── README.md                          # Comprehensive academic & technical documentation
├── config/                            # Core Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # App settings, static/media configurations
│   ├── urls.py                        # Master routing table
│   └── wsgi.py
├── accounts/                          # User authentication & RBAC profiles
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── dashboard/                         # Analytics KPI summary & executive views
│   ├── views.py
│   └── urls.py
├── patients/                          # Patient registry & demographic CRUD
│   ├── management/
│   │   └── commands/
│   │       └── generate_sample_data.py # Synthetic data generation engine
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── medical_records/                   # Longitudinal EHR records, vitals, biomarkers
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── datasets/                          # Dataset upload, CSV parsing, data cleaning
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── analytics/                         # EDA, visualization engine, correlations
│   ├── views.py
│   └── urls.py
├── reports/                           # Summary reporting, clinical PDF export
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── static/                            # Static asset distribution
│   ├── css/
│   │   └── style.css                  # Custom healthcare theme design system
│   ├── js/
│   │   └── main.js                    # Interactive DOM, AJAX, alert management
│   └── images/                        # Branding logos and graphics
├── media/                             # Dynamic user-generated and cached data
│   ├── uploaded_datasets/             # Uploaded raw CSV clinical files
│   ├── cleaned_datasets/              # Preprocessed & imputed datasets
│   ├── charts/                        # Generated Matplotlib/Seaborn plots
│   └── reports/                       # Exported PDF and HTML reports
└── templates/                         # HTML5 Django template views
    ├── base.html                      # Primary layout with navigation and sidebar
    ├── accounts/                      # Login and user profile templates
    ├── dashboard/                     # Metrics dashboard templates
    ├── patients/                      # Patient management templates
    ├── medical_records/               # Clinical history templates
    ├── datasets/                      # Dataset ingestion and cleaning templates
    ├── analytics/                     # Statistical charts and EDA templates
    └── reports/                       # Clinical report templates
```

---

## 9. Database Schema

The SQLite relational database maintains the following primary entities:

### 1. `User` (`accounts.CustomUser` or Django Auth)
- `id`: Auto-increment primary key
- `username`: Unique username (e.g., `admin`)
- `email`: User email address
- `role`: Role designation (`Admin`, `Doctor`, `Analyst`)
- `is_staff`, `is_superuser`: Django permission flags

### 2. `Patient` (`patients.Patient`)
- `id`: Primary key
- `patient_id`: Unique alphanumeric identifier (e.g., `SYN-PAT-0001`)
- `first_name`, `last_name`: Patient name attributes
- `gender`: Gender categorization (`Male`, `Female`, `Other`)
- `date_of_birth`: Birth date (calculates dynamic age)
- `blood_group`: ABO/Rh categorization (`A+`, `O+`, `B+`, etc.)
- `contact_number`, `email`, `address`: Contact information
- `created_at`, `updated_at`: Audit timestamps

### 3. `MedicalRecord` (`medical_records.MedicalRecord`)
- `id`: Primary key
- `patient`: Foreign key linked to `Patient`
- `doctor_name`: Attending physician or analyst
- `visit_date`: Date of clinical evaluation
- `heart_rate`: Resting pulse (bpm)
- `systolic_bp`, `diastolic_bp`: Blood pressure parameters (mmHg)
- `cholesterol`: Total serum cholesterol (mg/dL)
- `blood_glucose`: Fasting plasma glucose (mg/dL)
- `ck_mb`: Creatine Kinase-MB isoenzyme biomarker (ng/mL)
- `troponin`: Cardiac Troponin level (ng/mL)
- `outcome`: Clinical classification (`Positive`, `Negative`, `Inconclusive`)
- `diagnosis`, `symptoms`, `notes`: Clinical assessment narratives

### 4. `UploadedDataset` (`datasets.UploadedDataset`)
- `id`: Primary key
- `name`: Dataset title
- `file`: Path to raw uploaded CSV file
- `uploaded_by`: Foreign key to `User`
- `row_count`, `column_count`: Ingestion dimensions
- `uploaded_at`: Upload timestamp
- `is_cleaned`: Boolean preprocessing status indicator

### 5. `CleanedDataset` (`datasets.CleanedDataset`)
- `id`: Primary key
- `original_dataset`: Foreign key to `UploadedDataset`
- `cleaned_file`: File path to transformed dataset
- `cleaning_summary`: JSON or text metadata documenting imputations, dropped nulls, and removed duplicates

---

## 10. FDS Syllabus Coverage (21CSS202T)

| Syllabus Unit | Key Theoretical Topics | MediAnalytics Implementation Module |
|---|---|---|
| **Unit 1: Introduction to Data Science** | Data science lifecycle, NumPy arrays, Pandas DataFrames, indexing, vectorization. | Dataset ingestion (`datasets`), reproducible synthetic data generator command (`patients/management/commands/generate_sample_data.py`). |
| **Unit 2: Data Pre-processing & Wrangling** | Missing value strategies, deduplication, categorical transformation, feature scaling, outlier filtering. | Automated Cleaning Workbench (`datasets` app): mean/median/mode imputation, duplicate record drop, Z-score & IQR outlier detection. |
| **Unit 3: Exploratory Data Analysis (EDA)** | Descriptive statistics, measures of central tendency, variance, quartiles, skewness, kurtosis. | Interactive EDA View (`analytics` app): dynamic frequency counts, five-number summary calculations, distribution metrics. |
| **Unit 4: Data Visualization** | Univariate, bivariate, multivariate plots, boxplots, histograms, scatter plots, heatmaps. | Visualization Engine (`analytics` app): Matplotlib and Seaborn chart rendering, cached high-resolution plots. |
| **Unit 5: Statistical Modeling & Communication** | Correlation analysis, hypothesis formulation, executive reporting, communicating insights. | Correlation Heatmap Engine (`analytics`), Automated Clinical Diagnostic Report Generation (`reports` app). |

---

## 11. Screenshots Checklist

When compiling your academic submission or laboratory record, capture the following application views:

- [ ] **1. Authentication**: Login screen with custom healthcare branding (`/accounts/login/`).
- [ ] **2. Executive Dashboard**: KPI statistics cards and high-level health overview (`/dashboard/`).
- [ ] **3. Patient Registry**: Table listing synthetic patients with search and filter controls (`/patients/`).
- [ ] **4. Patient Profile**: Comprehensive demographic view and historical medical visits (`/patients/<id>/`).
- [ ] **5. Medical Records Log**: Biomarkers, vitals, and diagnostic outcomes listing (`/medical_records/`).
- [ ] **6. Dataset Ingestion**: Upload screen for raw CSV files (`/datasets/upload/`).
- [ ] **7. Data Quality & Cleaning**: Missing values and duplicate detection interface (`/datasets/<id>/clean/`).
- [ ] **8. Exploratory Data Analysis**: Statistical summaries, variance, and distribution tables (`/analytics/eda/`).
- [ ] **9. Biomarker Visualizations**: Histograms and boxplots showing normal vs. elevated levels (`/analytics/visualizations/`).
- [ ] **10. Correlation Matrix**: Heatmap displaying Pearson correlation between cardiac biomarkers (`/analytics/correlation/`).
- [ ] **11. Clinical Report View**: Final generated PDF/print-ready analytical report (`/reports/`).

---

## 12. Testing

Run Django's built-in automated test suite to verify application integrity:

```powershell
# Run all project unit tests
py manage.py test

# Run tests for specific modules
py manage.py test patients
py manage.py test medical_records
py manage.py test datasets
py manage.py test analytics
```

---

## 13. Troubleshooting (Windows / PowerShell)

### 1. `Activate.ps1 cannot be loaded because running scripts is disabled`
PowerShell execution policy restricts script execution by default. Run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 2. `Port 8000 is already in use`
If another service or previous server instance is using port 8000, specify an alternative port:
```powershell
py manage.py runserver 8080
```

### 3. Missing Media Directories
If media folders are not automatically created, ensure permissions allow directory creation or run:
```powershell
New-Item -ItemType Directory -Force -Path "media/uploaded_datasets", "media/cleaned_datasets", "media/charts", "media/reports"
```

### 4. Migration Conflicts or Database Reset
To reinitialize the SQLite database from scratch:
```powershell
Remove-Item db.sqlite3 -Force -ErrorAction SilentlyContinue
py manage.py makemigrations
py manage.py migrate
py manage.py generate_sample_data
```

---

## 14. Authors & Acknowledgments

- **Course**: Fundamentals of Data Science (21CSS202T)
- **Institution**: Department of Computer Science & Engineering
- **Developer**: Student Project Team
- **Academic Guidance**: Course Faculty & Laboratory Mentors

---

## 15. License

This project is licensed under the **MIT License**. You are free to modify, distribute, and utilize the codebase for academic, research, and educational purposes. See the `LICENSE` file for details.

---

## 16. Medical Disclaimer

> [!CAUTION]
> **ACADEMIC SIMULATION NOTICE**:
> All patient records, clinical measurements, vital signs, biomarker concentrations (Troponin, CK-MB, Blood Glucose, Cholesterol), and diagnostic outcomes generated or processed by this application are **synthetic and computer-generated**. This software is developed solely for educational fulfillment of Course **21CSS202T** and is **NOT** intended, certified, or qualified for real-world clinical decision-making, medical diagnosis, or patient healthcare delivery.
