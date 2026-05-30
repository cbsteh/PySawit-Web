# PySawit Web

PySawit Web is a browser-based oil palm growth and yield simulator developed for teaching, learning, and scenario-based exploration in agroclimatology and crop modelling.

The platform allows users to run oil palm simulations directly through a web browser without installing software. Students can load weather data, define agronomic scenarios, run simulations, visualize outputs, and collaboratively write reports through an integrated wiki system.

Originally developed under the Universiti Putra Malaysia (UPM) teaching grant GIPP No. 9323724 (2017–2020), PySawit Web was designed to translate a research simulation model into an interactive teaching platform accessible to undergraduate students without programming experience.

---

## Project Status

PySawit Web is no longer hosted online because the original grant-funded server infrastructure has been discontinued.

This repository serves primarily as:

* an academic archive,
* a historical record of the project,
* a reference for teaching and research workflows,
* and documentation of the platform architecture and pedagogical approach.

The complete source code and supporting files have been preserved.

PySawit Web has since been superseded in research and graduate teaching by Sawit.jl, a research-grade oil palm model written in Julia with substantially improved computational performance and updated scientific implementations.

---

## Educational Purpose

PySawit Web was developed to support teaching in:

* agroclimatology,
* crop modelling,
* soil–weather interactions,
* scenario-based reasoning,
* and collaborative scientific communication.

The platform was built around four main educational goals:

1. Make crop modelling more interactive and accessible than spreadsheet-based workflows.
2. Move students beyond pre-computed answers by requiring them to define scenarios, run simulations, and interpret outputs.
3. Replace isolated lab reports with collaborative wiki-based reporting.
4. Expose students to professional digital workflows involving data preparation, simulation, visualization, and online publication.

---

## Main Features

* Fully browser-based interface
* No software installation required
* Cross-platform operation (Windows, macOS, Linux, Android, iOS)
* Oil palm growth and yield simulation
* Weather data upload support
* Direct retrieval of NASA POWER climate data
* Interactive charts and tabular outputs
* Export to Excel
* Collaborative wiki reporting system
* Scenario-based simulation exercises

---

## Typical Workflow

A typical student session involved:

1. Defining a scenario question
2. Loading weather data
3. Setting agronomic and soil parameters
4. Running simulations
5. Analyzing tables and charts
6. Exporting outputs
7. Writing a collaborative wiki report

Students could iteratively modify inputs and rerun simulations to explore the effects of climate, soil, and management changes on oil palm growth and yield.

---

## Pedagogical Context

PySawit Web was developed partly in response to limitations observed in an earlier Excel-based oil palm model.

The spreadsheet version was scientifically functional but computationally slow, with full simulations sometimes requiring 20–30 minutes per run. This reduced classroom interactivity and negatively affected student engagement during practical sessions.

Moving computation to a server-side browser workflow substantially improved usability and restored interactive exploratory learning within class sessions.

One key lesson from the project was:

> A tool students cannot interact with fluidly will not teach well, regardless of the science behind it.

---

## Student Evaluation

PySawit Web was formally evaluated in 2019 and 2021 through student usability surveys.

Summary findings:

* Combined mean usability score: 4.39 / 5.00
* No student gave a score of 1 or 2 on any item
* 100% of 2021 respondents rated the platform 4 or 5 stars overall

Students consistently highlighted:

* ease of scenario exploration,
* visualization of climate effects,
* collaborative wiki reporting,
* and the ability to work with real climate data without programming.

The most common criticism was model run wait time during simultaneous class usage.

---

## Industry Use

PySawit Web was used for commercial oil palm cultivation simulations, including:

* irrigation scheduling,
* and planting density optimization.

This external use strengthened the educational value of the platform because students were working with workflows similar to those used in plantation management and applied research.

---

## Technology

PySawit Web functioned as the graphical user interface (GUI) for the underlying PySawit simulation engine written in Python.

Core components included:

* Python backend simulation engine
* Browser-based web interface
* Server-side computation queue
* Weather data handling system
* Collaborative wiki module
* NASA POWER climate data integration

---

## Copyright

Copyright © Christopher Teh

Copyright Registration:
Copyright No. LY2019000695 (Malaysia)

All rights reserved.

This repository is provided for academic reference, inspection, reproducibility, and historical documentation purposes only.

No permission is granted to use, modify, redistribute, commercialize, deploy, or create derivative works from this software without prior written permission from the copyright holder.

---

## Citation

If referencing this repository in academic or educational work, please cite:

Teh, C. B. S. PySawit Web: Web-Based Oil Palm Simulator. Universiti Putra Malaysia.

---

## Acknowledgement

Development supported by:

Universiti Putra Malaysia (UPM)
Teaching Grant GIPP No. 9323724 (2017–2020)

---

## Repository Purpose

This repository is maintained primarily as:

* an academic archive,
* evidence of educational innovation,
* and documentation of the evolution from spreadsheet-based teaching models to browser-based simulation and later research-grade scientific software.
