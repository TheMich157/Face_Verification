# Summary of All Roles Used in Bot

## Staff Hierarchy
1. `senior_staff`
   - Used in: admin_control.py, advanced_features.py
   - Full administrative access
   - Can manage all verification systems
   - Access to all analytics and settings

2. `staff_trainer`
   - Used in: advanced_features.py
   - Manages staff training
   - Reviews staff performance
   - Updates training materials

3. `trained_staff`
   - Used in: verification.py, moderation.py
   - Completed training modules
   - Can process verifications
   - Access to moderation tools

4. `staff`
   - Used in: all cogs
   - Basic moderation access
   - Can view verification queue
   - Access to staff channels

## Verification Roles
1. `verified_18plus` (or "18+")
   - Used in: verification.py, automod.py
   - Full server access
   - Age-restricted content
   - Strong profanity allowed

2. `verified_13plus` (or "13+")
   - Used in: verification.py, automod.py
   - Standard server access
   - Age-appropriate content
   - Moderate profanity allowed

3. `awaiting_staff_check`
   - Used in: verification.py
   - Temporary role during verification
   - Limited access
   - Pending review

4. `unverified`
   - Used in: verification.py, moderation.py
   - New members
   - Basic access only
   - No sensitive content

5. `banned_appeals`
   - Used in: appeals.py
   - Failed verification
   - Can only submit appeals
   - Very limited access

## Role Usage in Files

### src/cogs/verification.py
- verified_18plus
- verified_13plus
- awaiting_staff_check
- unverified
- staff

### src/cogs/automod.py
- verified_18plus
- verified_13plus
- staff

### src/cogs/appeals.py
- banned_appeals
- staff

### src/cogs/admin_control.py
- senior_staff
- staff

### src/cogs/advanced_features.py
- senior_staff
- staff_trainer
- trained_staff
- staff

### src/cogs/moderation.py
- trained_staff
- staff
- unverified

### src/cogs/statistics.py
- staff
- senior_staff

### src/cogs/privacy.py
- staff

## Role Permissions Matrix

```
Role            | Verify | Ban | Mod | Admin | Training
----------------|--------|-----|-----|-------|----------
senior_staff    |   ✓    |  ✓  |  ✓  |   ✓   |    ✓
staff_trainer   |   ✓    |  ✓  |  ✓  |       |    ✓
trained_staff   |   ✓    |  ✓  |  ✓  |       |
staff          |   ✓    |     |  ✓  |       |
verified_18plus |        |     |     |       |
verified_13plus |        |     |     |       |
awaiting_check |        |     |     |       |
unverified     |        |     |     |       |
banned_appeals |        |     |     |       |
```

## Role Color Scheme
```
senior_staff: #FF0000 (Red)
staff_trainer: #FFA500 (Orange)
trained_staff: #FFFF00 (Yellow)
staff: #00FF00 (Green)
verified_18plus: #800080 (Purple)
verified_13plus: #0000FF (Blue)
awaiting_staff_check: #FFA07A (Light Salmon)
unverified: #808080 (Gray)
banned_appeals: #A52A2A (Brown)
```

## Role Creation Order
1. senior_staff
2. staff_trainer
3. trained_staff
4. staff
5. verified_18plus
6. verified_13plus
7. awaiting_staff_check
8. unverified
9. banned_appeals

This order is important for maintaining proper role hierarchy and permissions inheritance.
