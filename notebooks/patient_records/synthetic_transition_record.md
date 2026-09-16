# Luma Health synthetic transition-of-care record

> **FICTIONAL WORKSHOP DOCUMENT — NOT A REAL PATIENT RECORD**

| Field | Value |
|---|---|
| Record ID | PT-88421 |
| Patient name | Elena Marquez |
| MRN | HLS-88421 |
| Date of birth | 1961-04-22 |
| Phone | 555-010-8842 |
| Email | elena.marquez@example.test |
| Address | 884 Cedar Lane, Lakeview, NY 10001 |
| Classification | Synthetic PHI |

## Transition-of-care note

Record PT-88421 belongs to Elena Marquez, MRN HLS-88421, date of birth 1961-04-22,
who lives at 884 Cedar Lane, Lakeview, NY 10001. Contact: 555-010-8842 or
elena.marquez@example.test. The patient was discharged yesterday with congestive heart failure.

## Workshop use

This record is loaded by the PHI-safety fixture. Unsafe scenarios pass its raw content through the
agent and patient-record tool. Governed scenarios reduce it to the clinical concept and timing needed
to select policy, before traced model, tool, logging, and memory boundaries.
