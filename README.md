# Home Office Tracker — Franco-Swiss

---

🇫🇷 [Version française](#version-française) | 🇬🇧 [English version](#english-version) | 🇩🇪 [Deutsche Version](#deutsche-version)

---

## Version française

Application de bureau pour le suivi des jours de télétravail et la vérification de conformité à l'**Accord franco-suisse du 11 avril 1983**, destinée aux travailleurs frontaliers.

### Avertissement important

> **⚠ Cette application est un outil d'aide personnelle. Elle ne constitue en aucun cas un conseil juridique, fiscal ou administratif.**

#### Usage et responsabilité

Cette application est conçue pour un **usage strictement personnel**. Elle fonctionne **entièrement en local**, sans connexion internet, sans collecte de données et sans envoi d'information vers un quelconque serveur externe. Toutes les données restent sur la machine de l'utilisateur.

**Les règles de calcul implémentées dans cette application (quota de 40 %, règle des 10 jours de mission, règle des 45 jours, logique d'imputation des catégories, etc.) représentent l'interprétation personnelle de l'auteur** des textes et accords applicables. Ces interprétations peuvent être incomplètes, inexactes ou ne pas refléter la position officielle des administrations compétentes (URSSAF, CLEISS, caisses de retraite, administrations fiscales française et suisse, etc.).

Il appartient à chaque utilisateur de :

- **Vérifier les règles de calcul** auprès des organismes compétents (CPAM, CLEISS, employeur, expert-comptable, conseiller fiscal, etc.) avant de prendre toute décision basée sur les résultats affichés.
- **S'assurer que l'accord franco-suisse du 11 avril 1983 et ses avenants interprétatifs (2022, 2023) sont toujours en vigueur** et n'ont pas été modifiés, complétés ou remplacés depuis la mise à jour de cette application. Les accords bilatéraux de sécurité sociale et les accords fiscaux entre États peuvent évoluer à tout moment.
- **Ne pas se fier exclusivement aux résultats de cette application** pour justifier sa situation auprès d'un employeur, d'une administration ou d'un organisme de sécurité sociale ou fiscal.

**L'auteur de cette application décline toute responsabilité** en cas d'erreur de calcul, d'interprétation erronée des règles, de modification des accords non répercutée dans l'application, ou de toute conséquence (administrative, financière, fiscale, sociale) découlant de l'utilisation des résultats produits. Chaque utilisateur est seul responsable de l'usage qu'il fait de cet outil et des décisions qu'il en tire.

### Base légale de référence

| Règle | Source |
|---|---|
| Quota de 40 % de télétravail | Accord franco-suisse du 11 avril 1983 + accords interprétatifs 2022/2023 |
| Plafond de 10 jours de missions imputables | Même accord |
| Plafond de 45 jours hors de France | Art. 1d + échange de lettres du 21-24 février 2005 |

### Catégories de jours

| Catégorie | Comptabilisé dans le quota de 40 % |
|---|---|
| Bureau (Suisse) | Non |
| Domicile (télétravail) | Oui — intégralement |
| Mission en France | Oui — imputée en priorité (max 10 jours combinés avec hors-France) |
| Mission hors France | Oui — imputée dans la capacité restante ; total plafonné à 45 jours/an |
| Jour de non-retour | Comptabilisé dans le plafond de 45 jours |
| Congé / Maladie | Non comptabilisé comme jour travaillé |

### Présentation

L'application permet de :

- Saisir et visualiser les jours de travail par catégorie sur un calendrier mensuel
- Calculer en temps réel la conformité au **quota de 40 %**
- Suivre l'utilisation de l'**échange de 45 jours** (accord de 2005)
- Générer un **rapport PDF trilingue** (FR / EN / DE) sur une page A4
- Gérer plusieurs utilisateurs avec des fichiers de données séparés

### Fonctionnement hors ligne

L'application ne nécessite **aucune connexion internet** à aucun moment. Toutes les données sont stockées localement dans le répertoire de l'application. Aucune donnée n'est synchronisée, partagée ou transmise.

### Prérequis

- Python 3.9 ou supérieur
- `reportlab` (uniquement pour l'export PDF)

```bash
pip install reportlab
```

### Installation et lancement

```bash
# Cloner le dépôt
git clone https://github.com/Anca6889/ch_fr_home_office_tracker.git
cd ch_fr_home_office_tracker

# Installer la dépendance PDF (optionnel)
pip install reportlab

# Lancer l'application
py home_office_tracking.py
```

Sous Windows, double-cliquer sur **`Frontalier.vbs`** lance l'application sans fenêtre de terminal.

### Structure du projet

```
├── home_office_tracking.py   # Point d'entrée — shell HomeOfficeApp
├── constants.py              # Codes catégories, seuils, thème UI
├── data.py                   # UserManager, DataStore (persistance JSON)
├── engine.py                 # Moteur de calcul de conformité
├── widgets.py                # CalendarWidget, SidePanel, helpers ttk
├── pdf_export.py             # Génération PDF via reportlab
└── Frontalier.vbs            # Lanceur Windows (sans terminal)
```

Les fichiers de données (`home_office_*.json`) sont créés automatiquement au premier lancement dans le même répertoire.

### Utilisation

- **Clic gauche** sur un jour ouvré → assigner une catégorie
- **Clic droit** → effacer le jour
- Menu déroulant **User** → changer d'utilisateur (+ pour ajouter, ✕ pour supprimer)
- Bouton **⬇ Export PDF** → générer le rapport annuel

---

## English version

Desktop application for tracking remote work days and checking compliance with the **Franco-Swiss Agreement of April 11, 1983**, designed for cross-border workers (frontaliers).

### Important disclaimer

> **⚠ This application is a personal assistance tool only. It does not constitute legal, tax, or administrative advice of any kind.**

#### Usage and liability

This application is designed for **strictly personal use**. It runs **entirely offline**, with no internet connection required, no data collection, and no transmission of any information to any external server. All data remains on the user's machine.

**The calculation rules implemented in this application (40% quota, 10-day mission cap, 45-day rule, category imputation logic, etc.) reflect the author's personal interpretation** of the applicable texts and agreements. These interpretations may be incomplete, inaccurate, or may not reflect the official position of the relevant authorities (French and Swiss social security bodies, tax administrations, etc.).

Each user is responsible for:

- **Verifying the calculation rules** with the competent bodies (social security funds, employer, accountant, tax adviser, etc.) before making any decision based on the results displayed by this application.
- **Confirming that the Franco-Swiss Agreement of April 11, 1983 and its interpretive amendments (2022, 2023) are still in force** and have not been amended, supplemented, or replaced since this application was last updated. Bilateral social security and tax agreements between states can change at any time.
- **Not relying solely on the results of this application** to justify their situation to an employer, a public authority, or a social security or tax body.

**The author of this application accepts no liability** for any calculation error, misinterpretation of the rules, unincorporated changes to applicable agreements, or any consequence (administrative, financial, fiscal, social) arising from the use of the results produced. Each user is solely responsible for how they use this tool and for any decisions they make based on it.

### Legal basis

| Rule | Source |
|---|---|
| 40% telework quota | Franco-Swiss Agreement, April 11, 1983 + interpretive agreements 2022/2023 |
| 10-day cap on imputable missions | Same agreement |
| 45-day outside-France cap | Art. 1d + bilateral exchange of letters, February 21–24, 2005 |

### Work day categories

| Category | Counts toward 40% quota |
|---|---|
| Office (Switzerland) | No |
| Home (remote work) | Yes — fully |
| Mission in France | Yes — imputed first (max 10 days combined with outside-FR) |
| Mission outside France | Yes — imputed within remaining capacity; total capped at 45 days/year |
| Non-return day | Counted within the 45-day cap |
| Vacation / Sick leave | Not counted as a working day |

### Overview

The application allows you to:

- Enter and visualise working days by category on a monthly calendar
- Calculate real-time compliance with the **40% quota**
- Track usage of the **45-day exchange** (2005 agreement)
- Generate a **trilingual PDF report** (FR / EN / DE) on a single A4 page
- Manage multiple users with separate data files

### Offline operation

The application requires **no internet connection** at any time. All data is stored locally in the application directory. No data is synchronised, shared, or transmitted.

### Requirements

- Python 3.9 or later
- `reportlab` (only required for PDF export)

```bash
pip install reportlab
```

### Installation and launch

```bash
# Clone the repository
git clone https://github.com/Anca6889/ch_fr_home_office_tracker.git
cd ch_fr_home_office_tracker

# Install PDF dependency (optional)
pip install reportlab

# Run the application
py home_office_tracking.py
```

On Windows, double-clicking **`Frontalier.vbs`** launches the application without a terminal window.

### Project structure

```
├── home_office_tracking.py   # Entry point — HomeOfficeApp shell
├── constants.py              # Category codes, thresholds, UI theme
├── data.py                   # UserManager, DataStore (JSON persistence)
├── engine.py                 # Compliance calculation engine
├── widgets.py                # CalendarWidget, SidePanel, ttk helpers
├── pdf_export.py             # PDF generation via reportlab
└── Frontalier.vbs            # Windows launcher (no terminal window)
```

Data files (`home_office_*.json`) are created automatically in the same folder on first run.

### Usage

- **Left click** a weekday → assign a category
- **Right click** → clear the day
- **User** dropdown → switch between users (+ to add, ✕ to delete)
- **⬇ Export PDF** button → generate the yearly report

---

## Deutsche Version

Desktop-Anwendung zur Erfassung von Homeoffice-Tagen und zur Überprüfung der Konformität mit dem **Französisch-Schweizerischen Abkommen vom 11. April 1983**, konzipiert für Grenzgänger.

### Wichtiger Hinweis

> **⚠ Diese Anwendung ist ein persönliches Hilfsmittel. Sie stellt in keiner Weise eine rechtliche, steuerliche oder administrative Beratung dar.**

#### Nutzung und Haftung

Diese Anwendung ist für den **ausschließlich persönlichen Gebrauch** konzipiert. Sie funktioniert **vollständig offline**, ohne Internetverbindung, ohne Datenerfassung und ohne Übertragung von Informationen an externe Server. Alle Daten verbleiben auf dem Rechner des Nutzers.

**Die in dieser Anwendung implementierten Berechnungsregeln (40%-Quote, 10-Tage-Regelung für Dienstreisen, 45-Tage-Regelung, Kategorienzurechnungslogik usw.) spiegeln die persönliche Auslegung des Autors** der anwendbaren Texte und Abkommen wider. Diese Auslegungen können unvollständig oder ungenau sein oder nicht der offiziellen Position der zuständigen Behörden entsprechen (französische und schweizerische Sozialversicherungsträger, Steuerverwaltungen usw.).

Jeder Nutzer ist dafür verantwortlich:

- Die **Berechnungsregeln bei den zuständigen Stellen zu überprüfen** (Sozialversicherungsträger, Arbeitgeber, Steuerberater usw.), bevor er Entscheidungen auf Grundlage der angezeigten Ergebnisse trifft.
- **Sicherzustellen, dass das französisch-schweizerische Abkommen vom 11. April 1983 und seine Auslegungsvereinbarungen (2022, 2023) noch in Kraft sind** und seit der letzten Aktualisierung dieser Anwendung nicht geändert, ergänzt oder ersetzt wurden. Bilaterale Sozialversicherungs- und Steuerabkommen zwischen Staaten können sich jederzeit ändern.
- **Die Ergebnisse dieser Anwendung nicht ausschließlich** als Nachweis gegenüber einem Arbeitgeber, einer Behörde oder einem Sozialversicherungs- oder Steuerträger zu verwenden.

**Der Autor dieser Anwendung übernimmt keine Haftung** für Berechnungsfehler, fehlerhafte Auslegungen der Regeln, nicht in der Anwendung berücksichtigte Änderungen der Abkommen oder für jegliche Folgen (verwaltungsrechtlicher, finanzieller, steuerlicher oder sozialer Natur), die sich aus der Nutzung der erzeugten Ergebnisse ergeben. Jeder Nutzer trägt die alleinige Verantwortung für die Nutzung dieses Tools und die daraus abgeleiteten Entscheidungen.

### Rechtsgrundlage

| Regel | Quelle |
|---|---|
| 40%-Telearbeit-Quote | Französisch-schweizerisches Abkommen vom 11. April 1983 + Auslegungsvereinbarungen 2022/2023 |
| 10-Tage-Obergrenze für anrechenbare Dienstreisen | Gleiches Abkommen |
| 45-Tage-Obergrenze für Aufenthalte außerhalb Frankreichs | Art. 1d + Briefwechsel vom 21.–24. Februar 2005 |

### Tageskategorien

| Kategorie | Anrechnung auf die 40%-Quote |
|---|---|
| Büro (Schweiz) | Nein |
| Homeoffice | Ja — vollständig |
| Dienstreise in Frankreich | Ja — vorrangig angerechnet (max. 10 Tage kombiniert mit Ausland) |
| Dienstreise außerhalb Frankreichs | Ja — innerhalb der verbleibenden Kapazität; Gesamtgrenze 45 Tage/Jahr |
| Nicht-Rückkehrtag | Wird auf die 45-Tage-Obergrenze angerechnet |
| Urlaub / Krankheit | Zählt nicht als Arbeitstag |

### Übersicht

Die Anwendung ermöglicht:

- Erfassung und Visualisierung von Arbeitstagen nach Kategorie in einem Monatskalender
- Echtzeit-Berechnung der Konformität mit der **40%-Quote**
- Verfolgung der Nutzung des **45-Tage-Austauschs** (Abkommen 2005)
- Erstellung eines **dreisprachigen PDF-Berichts** (FR / EN / DE) auf einer DIN-A4-Seite
- Verwaltung mehrerer Nutzer mit separaten Datendateien

### Offline-Betrieb

Die Anwendung benötigt **zu keinem Zeitpunkt eine Internetverbindung**. Alle Daten werden lokal im Anwendungsverzeichnis gespeichert. Es werden keine Daten synchronisiert, geteilt oder übertragen.

### Voraussetzungen

- Python 3.9 oder neuer
- `reportlab` (nur für den PDF-Export erforderlich)

```bash
pip install reportlab
```

### Installation und Start

```bash
# Repository klonen
git clone https://github.com/Anca6889/ch_fr_home_office_tracker.git
cd ch_fr_home_office_tracker

# PDF-Abhängigkeit installieren (optional)
pip install reportlab

# Anwendung starten
py home_office_tracking.py
```

Unter Windows startet ein Doppelklick auf **`Frontalier.vbs`** die Anwendung ohne Terminalfenster.

### Projektstruktur

```
├── home_office_tracking.py   # Einstiegspunkt — HomeOfficeApp-Shell
├── constants.py              # Kategoriecodes, Schwellenwerte, UI-Theme
├── data.py                   # UserManager, DataStore (JSON-Persistenz)
├── engine.py                 # Konformitätsberechnungs-Engine
├── widgets.py                # CalendarWidget, SidePanel, ttk-Hilfsfunktionen
├── pdf_export.py             # PDF-Erstellung via reportlab
└── Frontalier.vbs            # Windows-Starter (ohne Terminalfenster)
```

Datendateien (`home_office_*.json`) werden beim ersten Start automatisch im gleichen Verzeichnis erstellt.

### Bedienung

- **Linksklick** auf einen Werktag → Kategorie zuweisen
- **Rechtsklick** → Tag löschen
- **User**-Dropdown → Nutzer wechseln (+ zum Hinzufügen, ✕ zum Löschen)
- Schaltfläche **⬇ Export PDF** → Jahresbericht erstellen
