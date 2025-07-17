# 📊 KoboToolbox to ArcGIS Automation Template
A template repo with a script to migrate kobo forms entries into an ArcGIS Portal instance

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg


---


This repository provides a **Python-based template** to automate the extraction, geospatial processing, and publishing of **KoboToolbox form data** into **ArcGIS Online or Enterprise** Feature Layers.

It is designed as a **flexible pipeline**, allowing users to:

1. **Download form responses from KoboToolbox**
2. **Perform custom data processing and geospatial transformations**
3. **Publish or update data directly to ArcGIS Feature Layers**

---

## 🔧 Key Features

* Fetch data from KoboToolbox via the **Synchronous Export API**
* Process data using **Pandas** and **GeoPandas**
* Standardize fields for **ArcGIS compatibility** (e.g., column names, data types)
* Upload data to **ArcGIS Online or Enterprise** portals
* Includes support for **GitHub Actions** automation via an `environment.yml` and workflow examples

---

## 🚀 Quickstart

### 1. Clone the Repository

```bash
git clone https://github.com/guilhermeiablo/kobotoagol.git
cd kobotoagol
```

### 2. Install Dependencies

```bash
conda env create -f environment.yml
conda activate kobotoagol
```

### 3. Set Required Environment Variables

Configure the following:

| Variable          | Description                              |
| ----------------- | ---------------------------------------- |
| `KOBO_USER`       | KoboToolbox username                     |
| `KOBO_PASSWORD`   | KoboToolbox password                     |
| `KOBO_TOKEN`      | KoboToolbox export token                 |
| `ARCGIS_USER`     | ArcGIS portal username                   |
| `ARCGIS_PASSWORD` | ArcGIS portal password                   |
| `ARCGIS_PORTAL`   | ArcGIS portal URL (Online or Enterprise) |

You can define these locally or as **GitHub Repository Secrets** for automation.

### 4. Configure Your Kobo URLs

Update the script with your specific **KoboToolbox export URLs**.

### 5. Run the Script

```bash
python script.py
```

---

## 🔄 Optional Automation with GitHub Actions

You can automate the execution of this pipeline with a scheduled **GitHub Actions workflow**:

```
.github/workflows/kobotoagol.yml
```

### Example Schedule

Run daily:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'
```

---

## 📚 Resources

* [KoboToolbox Synchronous Export API](https://support.kobotoolbox.org/synchronous_exports.html)
* [ArcGIS API for Python Documentation](https://developers.arcgis.com/python/)
* [GeoPandas Documentation](https://geopandas.org/)

---

## ✅ License

MIT License or your preferred license.Creative Commons Share-alike Non-commercial 4.0 (CC-BY-NC-SA-4.0)

