# Project Report

## Title
Agentic AI Document Intelligence System for Autonomous Workflow Automation

## Executive Summary
This project delivers a full-stack B2C document workflow platform using React, Django, CrewAI, Google Gemini, MongoDB, and MinIO. It automates ingestion, preprocessing, classification, extraction, validation, routing, exceptions, human review, and audit logging.

## Business Need
Organizations process high volumes of scanned and inconsistent documents. Manual handling increases delays, errors, and compliance risk.

## Implemented Solution
- React UI for upload, dashboard, search, and human review
- Django REST API with JWT auth
- CrewAI multi-agent pipeline with Pydantic outputs
- Gemini reasoning for all agent decisions
- MongoDB collections for workflow state and logs
- MinIO for document object storage
- Django SMTP notifications (MailHog for local testing)

## Workflow Outcome
- straight-through processing for low-risk documents
- review routing for low-confidence or policy-conflict cases
- immutable audit trail for every stage and reviewer action

## Compliance with Requirements
- Backend: Django
- Frontend: React
- Agent framework: CrewAI
- LLM: Gemini
- Database: MongoDB local and Atlas-compatible deployment
- External workflow tools: not used
- Open-source components only except allowed Gemini API and Atlas usage
