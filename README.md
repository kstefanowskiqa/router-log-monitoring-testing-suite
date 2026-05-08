# Router Log Monitoring & Testing Suite

## 📌 Project Overview
This project is a real-time router log monitoring system that collects logs via UDP, processes them, and generates statistics, alerts, and visualizations.

The project is also used as a QA testing case study, focusing on test design, edge cases, and system reliability.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Status](https://img.shields.io/badge/status-active-success)
![QA](https://img.shields.io/badge/focus-QA_testing-purple)

---

## ⚙️ Features
- Real-time UDP log collection
- Burst traffic detection
- Blocked/denied attempt detection
- Daily statistics tracking
- JSON-based data storage
- Automatic log archiving
- Anomaly detection (traffic spikes)
- Chart generation using matplotlib
- Heartbeat system monitoring

---

## 🧪 Testing Scope
The system was tested from a QA perspective, including:

- Input validation
- Edge case handling
- High traffic scenarios
- Time-based system behavior
- Data integrity
- Error handling and recovery
- Stability under continuous runtime

---

## 📁 Project Structure

router-log-monitoring-testing-suite/

├── app/ # Main application source code  
├── test-cases/ # Manual test cases  
├── bug-reports/ # Documented issues and findings  
├── charts/ # Generated charts  
├── logs/ # Daily log files  
├── history/ # Archived statistics  
├── README.md  
├── test-plan.md  

---

## 🚀 Example Test Areas
- Burst detection threshold validation
- Blocked keyword detection accuracy
- Daily log rotation and archiving
- Handling malformed or empty log entries
- JSON corruption handling
- Performance during heavy traffic bursts
- Unicode and special character handling

---

## 🐞 Example Issues Identified
- False positives in blocked detection
- Missing validation for malformed input
- Potential performance bottlenecks during extreme bursts
- Risk of corrupted JSON file handling

---

## 📊 Technologies Used
- Python
- UDP sockets
- JSON
- Matplotlib
- File-based data storage

---

## 🎯 Project Goal
The goal of this project is to demonstrate practical QA skills using a real-world monitoring system.

The project focuses on:
- Test design
- Edge case analysis
- Bug reporting
- System reliability testing
- Real-time data processing validation

---

## 👨‍💻 Author
Karol Stefanowski  
Aspiring QA Engineer
