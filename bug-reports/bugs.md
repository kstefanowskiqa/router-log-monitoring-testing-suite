# Bug Reports

## BUG-001: False Positive in Blocked Detection
**Description:**
System marks logs containing "dropdown" as blocked attempts.

**Expected:**
Only exact matches like "blocked", "denied", "drop"

**Actual:**
"dropdown" is incorrectly counted

---

## BUG-002: No Input Validation
**Description:**
System processes malformed or empty logs without validation.

**Risk:**
Potential incorrect stats or crashes

---

## BUG-003: JSON File Corruption Handling
**Description:**
If JSON file is corrupted, system may fail on load

**Expected:**
Graceful handling + fallback

---

## BUG-004: Performance Risk on High Burst
**Description:**
Very high log bursts may cause performance degradation

**Expected:**
System should handle load or throttle input
