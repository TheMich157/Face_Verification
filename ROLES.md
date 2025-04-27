# Role Guide - Age Verification Bot

## Staff Roles (Highest to Lowest)

### 1. `senior_staff`
- Full administrative access
- Can manage other staff
- Access to all commands
- Can modify bot settings
- View analytics dashboard
- Handle appeals
- Manage training

### 2. `staff_trainer`
- Train new staff members
- Review staff performance
- Access training modules
- Update training materials
- Monitor staff accuracy
- Provide feedback

### 3. `trained_staff`
- Completed training modules
- Process verifications
- Handle user appeals
- Access mod logs
- View queue status
- Monitor analytics

### 4. `staff`
- Basic moderation access
- View verification queue
- Process basic verifications
- Access staff chat
- Training in progress

## Verification Roles

### 1. `verified_18plus` (or "18+")
- Full server access
- Age-restricted channels
- Strong profanity allowed
- Adult content access
- Special permissions

### 2. `verified_13plus` (or "13+")
- Standard server access
- Age-appropriate channels
- Moderate profanity allowed
- Basic permissions
- No adult content

### 3. `awaiting_staff_check`
- Temporary role
- Verification in progress
- Limited server access
- Pending review
- No special permissions

### 4. `unverified`
- New members
- Basic channel access
- No sensitive content
- No profanity allowed
- Restricted permissions

### 5. `banned_appeals`
- Failed verification
- Can submit appeals
- Very limited access
- No sensitive content
- Temporary status

## Role Hierarchy

```
Senior Staff
    └── Staff Trainer
        └── Trained Staff
            └── Staff
                └── Verified 18+
                    └── Verified 13+
                        └── Awaiting Staff Check
                            └── Unverified
                                └── Banned Appeals
```

## Permission Sets

### Senior Staff
- Manage Roles
- Manage Channels
- Ban Members
- Kick Members
- Manage Messages
- View Audit Log
- Manage Server
- All Staff Permissions

### Staff Trainer
- Access Training Tools
- Review Performance
- Manage Training
- View Analytics
- All Trained Staff Permissions

### Trained Staff
- Process Verifications
- Handle Appeals
- Access Mod Logs
- View Queue
- All Staff Permissions

### Staff
- Basic Moderation
- View Queue
- Process Verifications
- Access Staff Chat

### Verified 18+
- Access All Channels
- Adult Content
- Strong Profanity
- Special Features

### Verified 13+
- Standard Access
- Age-Appropriate Content
- Moderate Profanity
- Basic Features

### Awaiting Staff Check
- Limited Access
- Verification Channels
- Basic Chat
- No Sensitive Content

### Unverified
- Welcome Channel
- Basic Information
- Verification Process
- No Special Access

### Banned Appeals
- Appeals Channel Only
- No Other Access
- Temporary Status

## Role Management

1. **Automatic Assignment**
   - Unverified: On join
   - Awaiting Staff Check: During verification
   - 13+/18+: After approval
   - Banned Appeals: After rejection

2. **Manual Assignment**
   - Staff roles
   - Training roles
   - Special permissions

3. **Role Removal**
   - Automatic cleanup
   - Verification updates
   - Appeal results
   - Staff changes

## Role Colors (Recommended)

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

## Role Setup

The bot automatically creates and manages these roles. Ensure:
1. Bot role is at top of hierarchy
2. Roles are in correct order
3. Permissions are properly set
4. Colors are assigned (optional)

## Role Commands

Staff can use:
- `/review` - Process verifications
- `/18approve` - Grant 18+ status
- `/verification_status` - Check status

Admins can use:
- `/bulk_verify` - Mass role updates
- `/clear_verification_queue` - Reset queue
- `/verification` - Toggle systems

## Notes

- Keep role hierarchy intact
- Don't modify permissions without approval
- Monitor role assignments
- Regular role audits recommended
- Document role changes
