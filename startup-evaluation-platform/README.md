# Startup Evaluation Platform - High Level Design

## Overview
An end-to-end AI-powered platform for evaluating startups and generating investment memos for investors using GCP services and Vertex AI Agent Engine.

## Evaluation Criteria
1. **Founder Market Fit** - Assess founder's background, experience, and alignment with the market
2. **Problem Evaluation & Competition** - Analyze market problem, competition landscape, and market size
3. **USP Evaluation** - Evaluate unique selling proposition and competitive advantages
4. **Team Profile Overall** - Comprehensive team assessment and capability analysis

## AI Agents
1. **Evaluation Agent** - Analyzes provided information and conducts online research
2. **Scheduling Agent** - Manages calendar integration and founder meeting coordination
3. **Interview Agent** - Conducts AI-powered calls with founders for additional insights

## Technology Stack
- **Cloud Platform**: Google Cloud Platform (GCP)
- **AI Engine**: Vertex AI Agent Engine
- **Backend Services**: Cloud Run, Cloud Functions
- **Database**: Firestore, Cloud SQL
- **Storage**: Cloud Storage
- **APIs**: Various GCP AI/ML services

## Project Structure
```
startup-evaluation-platform/
├── agents/
│   ├── evaluation-agent/
│   ├── scheduling-agent/
│   └── interview-agent/
├── backend/
│   ├── api/
│   ├── services/
│   └── models/
├── infrastructure/
│   ├── terraform/
│   └── deployment/
├── docs/
└── tests/
```
