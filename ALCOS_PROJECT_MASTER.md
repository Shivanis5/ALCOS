# ALCOS (Automated Letter of Credit Operating System)

## Project Goal

Build a professional desktop Trade Finance Operating System using Python and PySide6 that simulates a real banking Letter of Credit workflow.

This is NOT just an MT700 generator.

The application manages the complete lifecycle of a Trade Transaction.

------------------------------------------------------------

## Technology Stack

Language:

- Python 3.10

GUI:

- PySide6 (Qt)

Database:

- SQLite

ORM:

- SQLAlchemy (future)

PDF:

- ReportLab

Email:

- SMTP (Gmail)

AI:

- OCR

- Rule Extraction

- Document Validation

- Risk Scoring

- Compliance Checking

------------------------------------------------------------

## Current Progress

Completed

✔ Boot Screen

✔ Login Screen

✔ Dashboard

✔ Sidebar

✔ Header

✔ Statistics Cards

✔ Recent LC Table

✔ Trade Summary Widget

✔ Logger

✔ Theme Manager

✔ SQLite Database

✔ MT700 Screen Skeleton

------------------------------------------------------------

## Official Architecture

User Login

      │

      ▼

Dashboard

      │

      ▼

Create Trade Transaction

      │

      ▼

Transaction Workspace

      │

      ├── General Information

      ├── MT700

      ├── MT707

      ├── Documents

      ├── OCR + AI

      ├── Validation

      ├── Discrepancy

      ├── Risk

      ├── Compliance

      ├── PDF

      └── Email

------------------------------------------------------------

## Transaction Lifecycle

Create Trade Transaction

↓

Fill General Details

↓

Create MT700

↓

Save to SQLite

↓

Generate MT700 PDF

↓

Email PDF

↓

Create MT707 Amendment

↓

Generate Amendment PDF

↓

Upload Trade Documents

↓

OCR Extraction

↓

AI Rule Extraction

↓

Cross Document Validation

↓

Discrepancy Detection

↓

Risk Score

↓

Compliance Check

↓

Generate Bank Submission Package

↓

Email Submission Package

------------------------------------------------------------

## Folder Structure

app/

controllers/

core/

models/

services/

utils/

views/

widgets/

database/

generated/

logs/

resources/

------------------------------------------------------------

## Development Rules

1. Never modify dashboard layout without explaining UI impact.

2. Every new section must be a separate reusable widget.

3. Compile after every major change.

4. Test after every integration.

5. Dashboard remains stable while features are added.

6. Everything belongs to a Trade Transaction.

7. MT700 and MT707 are modules inside a transaction.

8. PDF generation happens from MT700/MT707.

9. Email always sends generated PDF.

10. Build like a real banking product, not just a demo.

------------------------------------------------------------

## Current Phase

Phase 3

Trade Transaction Workspace

Next Step

Create Transaction Workspace

General Information

MT700 Module

MT707 Module

Database Integration

PDF

Email

After that

OCR

AI

Validation

Compliance

Reports

------------------------------------------------------------

End Goal

A professional desktop Trade Finance Operating System capable of:

• Creating Trade Transactions

• Creating MT700 LC

• Creating MT707 Amendments

• Storing data in SQLite

• Generating professional banking PDFs

• Sending PDFs via Gmail

• Uploading trade documents

• OCR extraction

• AI rule extraction

• Cross-document validation

• Discrepancy detection

• Risk scoring

• Compliance checking

• Generating complete bank submission packages