# Scooter Safety System: Edge AI Model Sidewalk Detection

[![Status](https://img.shields.io/badge/Status-Production%20Ready-green)](https://github.com/T-Py-T/SideWalkDetection)
[![ML Pipeline](https://img.shields.io/badge/ML%20Pipeline-Complete-blue)](https://github.com/T-Py-T/SideWalkDetection)
[![Edge Deployment](https://img.shields.io/badge/Edge%20Deployment-Raspberry%20Pi-orange)](https://github.com/T-Py-T/SideWalkDetection)

## Problem and Solution

**The Challenge:** E-scooters operating at high speeds in pedestrian areas create safety risks and regulatory compliance issues. Cities require automated safety measures, but manual enforcement doesn't scale across fleets.

**Our Solution:** Real-time computer vision system that automatically detects sidewalks and crosswalks, then limits scooter speed to 5 mph to protect pedestrians. The system uses edge computing for immediate response without cloud dependency.

## Technical Implementation

### Architecture Overview
```
Video Collection → Data Processing → Model Training → Edge Deployment
       ↓               ↓              ↓              ↓
   Ride Videos     PC Scripts     Google Colab   Raspberry Pi
   GPS Data        Processing     MobileNetV2    TensorFlow Lite
```

### Technology Stack

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **Model Training** | Google Colab, MobileNetV2, Coral TPU | Geographic-specific model development |
| **Data Processing** | Python pipeline (25+ scripts) | Image preparation and dataset creation |
| **Edge Inference** | Raspberry Pi, TensorFlow Lite | Real-time sidewalk detection |
| **Speed Control** | Hardware integration | Safety intervention system |

### Key Features

**Geographic-Specific Models**
- Denver model: `mobileV2_denver_0303.tflite`
- Location-specific infrastructure adaptation
- Multi-city deployment capability

**Comprehensive Data Pipeline**
- Automated image processing and normalization
- Training set creation with geographic filtering
- Database-driven data management
- Video generation for model validation

**Production Deployment**
- Real-time video processing on Raspberry Pi
- Hardware GPIO integration for speed control
- Multiple deployment configurations
- Automatic startup and system integration

## Repository Structure

**`code/colab/`** - Google Colab training notebooks for MobileNetV2 model development, Coral TPU optimization, and model evaluation

**`code/pc/`** - Data processing pipeline with 25+ Python scripts for image preprocessing, training set creation, database management, and video generation

**`code/pi/`** - Raspberry Pi deployment system including neural network inference, real-time video processing, GPIO integration, and speed control scripts

**`models/`** - Production-ready TensorFlow Lite models optimized for edge deployment

## Performance Metrics

**Model Architecture**
- Base: MobileNetV2 optimized for edge deployment
- Edge TPU acceleration support via Coral training
- Multi-city validation across diverse urban environments
- TensorFlow Lite optimization for Raspberry Pi

**Production Performance**
- Real-time inference on Raspberry Pi 4
- GPS integration for location-aware model selection
- Hardware speed limiting integration
- Sub-second response time for safety interventions

## Data Engineering Pipeline

**Automated Processing Capabilities**
- Image normalization and cropping
- Training set creation with geographic filtering
- Database management for large datasets
- Video generation for validation
- KML generation for geographic visualization

**Quality Assurance**
- Low velocity filtering
- Image sorting and validation
- Post-annotation processing
- Model evaluation across multiple test sets

## Portfolio Highlights

**End-to-End Pipeline:** Complete data collection through production deployment
**Geographic Scalability:** Multi-city model training and deployment strategy
**Production Optimization:** MobileNetV2 and TensorFlow Lite for edge constraints
**Hardware Integration:** Real-time speed control with safety-critical reliability
**Data Engineering:** Comprehensive automation for large-scale data processing
**Model Lifecycle:** Training, evaluation, and deployment across multiple environments

## Getting Started

**Training New Models**
1. Use Google Colab notebooks in `colab/` directory
2. Process training data with scripts in `pc/` directory
3. Deploy models using `pi/` deployment scripts

## Future Additions

### Automated CI/CD Pipeline
- **GitHub Actions Integration:** Trigger Colab notebook execution on new data commits
- **Quality Gates:** Automated testing before model deployment to production fleet

### Fleet Management System
- **Device Discovery:** Automatic Raspberry Pi device registration and health monitoring
- **Data Pipeline Automation:** Orchestrate existing `pc/` scripts with Apache Airflow or Prefect

---

**Technical Leadership Demonstrated:** Production-ready ML system with geographic scalability, comprehensive data engineering, and safety-critical hardware integration suitable for regulatory compliance and commercial deployment.

<!--
## Deployment Options
- Standard demo: `./run_scooter`
- Speed limiting: `./run_scooter_limit_speed`
-->