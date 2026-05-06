# Test Cases

## TC-001: Burst Detection Threshold
**Steps:**
1. Send 300 logs within 5 seconds
2. Send 301 logs within 5 seconds

**Expected:**
- 300 → No alert
- 301 → Alert triggered

---

## TC-002: Empty Log Entry
**Steps:**
1. Send empty UDP packet

**Expected:**
- System should not crash
- Log should be ignored or handled safely

---

## TC-003: Large Log Input
**Steps:**
1. Send very large log message (>4096 bytes)

**Expected:**
- System handles truncation or logs safely
- No crash

---

## TC-004: Blocked Keyword Detection
**Steps:**
1. Send log containing "blocked"
2. Send log containing "BLOCKED"

**Expected:**
- Both should be detected

---

## TC-005: False Positive Detection
**Steps:**
1. Send log: "dropdown menu opened"

**Expected:**
- Should NOT be counted as blocked

---

## TC-006: Day Change Handling
**Steps:**
1. Simulate change of date (or wait until midnight)

**Expected:**
- Data archived
- New daily stats created

---

## TC-007: JSON Corruption
**Steps:**
1. Manually corrupt JSON file

**Expected:**
- System should not crash
- Error should be logged

---

## TC-008: High Traffic Load
**Steps:**
1. Send large number of logs rapidly

**Expected:**
- System remains stable
- Burst detection works

---

## TC-009: Special Characters in Logs
**Steps:**
1. Send logs with unicode / weird characters

**Expected:**
- No crash
- Proper handling

---

## TC-010: No Incoming Logs
**Steps:**
1. Run system with no incoming data

**Expected:**
- System stays alive
- Heartbeat logs appear
