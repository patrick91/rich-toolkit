---
release type: patch
---

Fix inline menu option wrapping by using spaces instead of tabs.

When using inline menus (e.g., `app.confirm()`), options like "Yes" and "No" were wrapping to separate lines due to tab character separators expanding unpredictably in fixed-width table columns. This release replaces tab separators with two spaces for consistent, predictable spacing.

**Before:**
```
● Yes
○ No
```

**After:**
```
● Yes  ○ No
```
