# Router Log Monitoring & Testing Suite

## 📌 Project Overview
This project is a real-time router log monitoring system that collects logs via UDP, processes them, and generates statistics, alerts, and visualizations.

The project is also used as a QA testing case study, focusing on test design, edge cases, and system reliability.

![Python](https://img.shields.io/badge/Python-3.14.3-blue)
![Status](https://img.shields.io/badge/status-development_stopped-yellow)
![QA](https://img.shields.io/badge/focus-QA_testing-purple)
![Test Status](https://img.shields.io/badge/Testing_Status-Not_fully_tested-orange)

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

## 📦 Main Dependencies

| Library | Purpose |
|---|---|
| matplotlib | Chart generation |
| numpy | Data processing |
| psutil | System monitoring |
| requests | HTTP communication |
| pillow | Image processing |

## ⚠️ Known Limitations

- Currently tested only on Windows 10
- Requires router syslog support
- No graphical dashboard implemented yet
- File-based storage may become inefficient under extreme long-term load

---

## 🖥️ Test Environment

| Component | Details |
|---|---|
| Test Laptop | Lenovo IdeaPad Y580 |
| CPU | Intel Core i7 (3rd Gen Ivy Bridge) |
| GPU | NVIDIA GeForce GTX 660M |
| RAM | DDR3 Memory |
| Operating System | Windows |
| Main Router | ASUS ZenWiFi BQ16 |
| Mesh Nodes | 2x ASUS ZenWiFi ET12 |
| Network Protocol | UDP Syslog |
| Programming Language | Python 3.x |
| Data Visualization | Matplotlib |
| Testing Type | Manual Testing, Stability Testing, Burst Traffic Testing |
| Runtime Mode | Real-Time Continuous Monitoring |

---

## 🌐 Real Network Environment

The system was tested in a real home network environment using ASUS mesh infrastructure and live router-generated syslog traffic.

The testing environment allowed realistic validation of:
- continuous log monitoring
- burst traffic detection
- anomaly detection
- long runtime stability
- real-time statistics generation

---

## 👨‍💻 Author
Karol Stefanowski  
Aspiring QA Engineer
